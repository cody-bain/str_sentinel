"""
Evaluate CPE matching accuracy for STR Sentinel
Tests CPE generation accuracy against known devices from NVD database
Queries CVE counts to measure vulnerability coverage
"""
import json
import os
import time
import sys
from datetime import datetime

# Add app directory to path for imports
sys.path.insert(0, '/app')

from cpe_validator import validate_cpe
from main import generate_cpe

def query_cve_count(cpe):
    """Query NVD for CVE count for a given CPE"""
    import requests
    from dotenv import load_dotenv
    
    load_dotenv()
    nvd_api_key = os.getenv('NVD_API_KEY')
    
    url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
    headers = {}
    if nvd_api_key:
        headers['apiKey'] = nvd_api_key
    
    params = {
        'cpeName': cpe,
        'resultsPerPage': 1  # We only need the count
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('totalResults', 0)
        else:
            print(f"❌ CVE query failed for {cpe}: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ CVE query error for {cpe}: {e}")
        return None

def run_validation_test():
    """Run CPE validation test on test dataset"""
    
    # Load test devices
    with open('/test/test-devices.json', 'r') as f:
        test_data = json.load(f)
    
    devices = test_data['devices']
    
    print(f"🧪 Starting CPE matching evaluation")
    print(f"📊 Test dataset: {len(devices)} STR-relevant IoT devices")
    print(f"⏱️  This will take ~{len(devices) * 0.6:.0f} seconds due to NVD API rate limits\n")
    
    # Track results
    results = []
    validation_passed = 0
    exact_matches = 0
    vendor_matches = 0
    product_matches = 0
    version_matches = 0
    cve_counts = []
    devices_with_cves = 0
    
    start_time = time.time()
    
    for i, device in enumerate(devices, 1):
        identity = device['identity']
        expected_cpe = device['expected_cpe']
        
        # Generate CPE from identity
        generated_cpe = generate_cpe(identity)
        
        # Validate against NVD - returns (cpe_string, validation_status)
        validated_cpe, validation_status = validate_cpe(generated_cpe)
        is_valid = (validation_status == 'validated')
        
        # Use validated CPE for exact matching and CVE queries
        final_cpe = validated_cpe if is_valid else generated_cpe
        
        # Parse expected and generated CPEs for comparison
        expected_parts = expected_cpe.split(':')
        generated_parts = final_cpe.split(':')
        
        # Compare components
        exact_match = final_cpe == expected_cpe
        vendor_match = (len(expected_parts) > 3 and len(generated_parts) > 3 and 
                       expected_parts[3] == generated_parts[3])
        product_match = (len(expected_parts) > 4 and len(generated_parts) > 4 and 
                        expected_parts[4] == generated_parts[4])
        version_match = (len(expected_parts) > 5 and len(generated_parts) > 5 and 
                        expected_parts[5] == generated_parts[5])
        
        # Query CVE count if validated
        cve_count = None
        if is_valid:
            cve_count = query_cve_count(final_cpe)
            if cve_count is not None:
                cve_counts.append(cve_count)
                if cve_count > 0:
                    devices_with_cves += 1
            
            # Rate limiting: 0.6s with API key, 6s without
            nvd_api_key = os.getenv('NVD_API_KEY')
            time.sleep(0.6 if nvd_api_key else 6.0)
        
        # Update statistics
        if is_valid:
            validation_passed += 1
        if exact_match:
            exact_matches += 1
        if vendor_match:
            vendor_matches += 1
        if product_match:
            product_matches += 1
        if version_match:
            version_matches += 1
        
        # Store detailed result
        result = {
            'device_number': i,
            'ip': device['ip'],
            'vendor': identity['vendor'],
            'model': identity['model'],
            'version': identity['version'],
            'detection_method': identity['detection_method'],
            'expected_cpe': expected_cpe,
            'generated_cpe': generated_cpe,
            'validated_cpe': validated_cpe,
            'validation_passed': is_valid,
            'exact_match': exact_match,
            'vendor_match': vendor_match,
            'product_match': product_match,
            'version_match': version_match,
            'cve_count': cve_count,
            'validation_status': validation_status
        }
        results.append(result)
        
        # Progress indicator
        status_icon = "✅" if is_valid else "❌"
        cve_text = f"{cve_count} CVEs" if cve_count is not None else "N/A"
        print(f"[{i:3d}/{len(devices)}] {status_icon} {identity['vendor']} {identity['model']} - {cve_text}")
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    # Calculate metrics
    total = len(devices)
    validation_rate = (validation_passed / total * 100) if total > 0 else 0
    exact_match_rate = (exact_matches / total * 100) if total > 0 else 0
    vendor_match_rate = (vendor_matches / total * 100) if total > 0 else 0
    product_match_rate = (product_matches / total * 100) if total > 0 else 0
    version_match_rate = (version_matches / total * 100) if total > 0 else 0
    
    total_cves = sum(cve_counts) if cve_counts else 0
    avg_cves = (total_cves / len(cve_counts)) if cve_counts else 0
    cve_coverage = (devices_with_cves / validation_passed * 100) if validation_passed > 0 else 0
    
    # Prepare report
    report = {
        'test_metadata': {
            'test_name': 'CPE Matching Evaluation - STR IoT Devices',
            'test_date': datetime.now().isoformat(),
            'total_devices_tested': total,
            'test_duration_seconds': elapsed_time,
            'dataset_source': 'NVD CPE Dictionary filtered for STR-relevant IoT'
        },
        'validation_metrics': {
            'devices_validated': validation_passed,
            'validation_rate_percent': round(validation_rate, 2),
            'exact_matches': exact_matches,
            'exact_match_rate_percent': round(exact_match_rate, 2),
            'vendor_matches': vendor_matches,
            'vendor_match_rate_percent': round(vendor_match_rate, 2),
            'product_matches': product_matches,
            'product_match_rate_percent': round(product_match_rate, 2),
            'version_matches': version_matches,
            'version_match_rate_percent': round(version_match_rate, 2)
        },
        'cve_metrics': {
            'total_cves_found': total_cves,
            'devices_with_cves': devices_with_cves,
            'cve_coverage_percent': round(cve_coverage, 2),
            'average_cves_per_device': round(avg_cves, 1),
            'min_cves': min(cve_counts) if cve_counts else 0,
            'max_cves': max(cve_counts) if cve_counts else 0
        },
        'detailed_results': results
    }
    
    # Save report
    os.makedirs('/test', exist_ok=True)
    with open('/test/cpe-matching-report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"📊 CPE MATCHING EVALUATION RESULTS")
    print(f"{'='*60}")
    print(f"✅ Validation Rate: {validation_rate:.1f}% ({validation_passed}/{total} devices)")
    print(f"🎯 Exact Match Rate: {exact_match_rate:.1f}% ({exact_matches}/{total} devices)")
    print(f"🏢 Vendor Match Rate: {vendor_match_rate:.1f}% ({vendor_matches}/{total} devices)")
    print(f"📦 Product Match Rate: {product_match_rate:.1f}% ({product_matches}/{total} devices)")
    print(f"🔢 Version Match Rate: {version_match_rate:.1f}% ({version_matches}/{total} devices)")
    print(f"\n🔒 CVE COVERAGE")
    print(f"{'='*60}")
    print(f"Total CVEs Found: {total_cves}")
    print(f"Devices with CVEs: {devices_with_cves}/{validation_passed} ({cve_coverage:.1f}%)")
    print(f"Average CVEs per device: {avg_cves:.1f}")
    if cve_counts:
        print(f"CVE range: {min(cve_counts)} - {max(cve_counts)}")
    print(f"\n⏱️  Test Duration: {elapsed_time:.1f} seconds")
    print(f"💾 Report saved to /test/cpe-matching-report.json")
    
    # Highlight most vulnerable devices
    vulnerable_devices = sorted([r for r in results if r.get('cve_count', 0) > 0], 
                                key=lambda x: x.get('cve_count', 0), reverse=True)[:10]
    if vulnerable_devices:
        print(f"\n🔴 TOP 10 MOST VULNERABLE DEVICES:")
        print(f"{'='*60}")
        for vd in vulnerable_devices:
            print(f"{vd['cve_count']:3d} CVEs - {vd['vendor']} {vd['model']} {vd['version']}")
    
    # Highlight validation failures
    failed = [r for r in results if not r['validation_passed']]
    if failed:
        print(f"\n❌ VALIDATION FAILURES ({len(failed)} devices):")
        print(f"{'='*60}")
        for fail in failed[:10]:  # Show first 10
            print(f"- {fail['vendor']} {fail['model']}: {fail['validation_status']}")
        if len(failed) > 10:
            print(f"... and {len(failed) - 10} more")
    
    print(f"\n{'='*60}\n")

if __name__ == '__main__':
    run_validation_test()
