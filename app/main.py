import nmap
import time
import argparse
import os
import logging
import json
import re
from datetime import datetime
# Protocol Handlers
from protocol_handlers.mdns_handler import run_mdns_scan
from protocol_handlers.http_handler import run_http_scan
from protocol_handlers.ssh_handler import run_ssh_scan
# CPE Validation
from cpe_validator import validate_cpe
# CVE Lookup & Risk Scoring
from cve_lookup import query_cves_for_cpe
from risk_scoring import calculate_device_risk_score, calculate_network_risk_summary, generate_recommendations

'''
CODE GENERATED WITH ASSISTANCE FROM VARIOUS AI TOOLS.
ALL AI-GENERATED CONTENT WAS REVIEWED, REVISED, AND ADAPTED TO MEET STR SENTINEL REQUIREMENTS.
'''

def generate_cpe(identity):
    '''
    Generate NVD-compatible CPE string from device identity.
    Uses actual version numbers and extracts model numbers from titles when available.
    '''
    vendor = identity.get('vendor', 'unknown').lower().replace(" ", "_")
    version = identity.get('version', '*')
    
    # Extract model number from HTTP title if available (ex. "DS-2CD2042WD-I")
    model = identity.get('model', 'unknown').lower().replace(" ", "_")
    if 'http_title' in identity:
        title = identity['http_title']
        # Match model numbers like DS-2CD2042WD-I, T2500E, etc.
        model_match = re.search(r'([A-Z]{2,}-[A-Z0-9\-]+|[A-Z]\d{4}[A-Z]?)', title)
        if model_match:
            model = model_match.group(1).lower().replace("-", "_")
    
    # Format version properly (remove wildcards if I have actual version)
    if version and version != 'Unknown' and version != '*':
        # Keep version string as-is for CPE format (e.g., "7.6p1")
        # Don't add colons - CPE 2.3 requires exactly 11 fields
        version_clean = version
    else:
        version_clean = "*"
    
    # Determine CPE type based on what was detected:
    #    SSH always detects applications/services (OpenSSH, Dropbear, etc.)
    #    Generic web servers (nginx, Apache) are applications even if found via HTTP
    #    Media devices (Apple TV, Chromecast) are applications
    #    Device-specific models (Hikvision Web Server, cameras) are hardware
    software_indicators = ['ssh', 'apache', 'nginx', 'iis', 'lighttpd', 'tomcat', 'openssh', 'apple_tv'] # SCALE THIS!
    is_software = (
        identity.get('detection_method') == 'SSH' or
        identity.get('model', '').lower() in software_indicators or
        'apple tv' in identity.get('model', '').lower()
    )
    cpe_type = 'a' if is_software else 'h'
    
    return f"cpe:2.3:{cpe_type}:{vendor}:{model}:{version_clean}:*:*:*:*:*:*:*"


def run_discovery(target, output=None):

    '''
    Function designed to run ARP Passive Scan on Local STR Network,
    followed by Active mDNS Identification.
    '''

    nm = nmap.PortScanner()
    logging.info(f"--- STR Sentinel Starting Discovery on {target} ---")
    
    try:
        # --- PHASE 1: HOST DISCOVERY (NMAP) ---
        logging.info("[Phase 1] Running Nmap Host Discovery...")
        nm.scan(hosts=target, arguments='-sn')
        hosts_list = []

        # Parse Nmap Results
        for x in nm.all_hosts():
            host_info = {
                "ip": x,
                "status": nm[x]['status']['state'],
                "hostname": nm[x].hostname() if 'hostname' in nm[x] else None,
                "mac": nm[x]['addresses'].get('mac') if 'addresses' in nm[x] and 'mac' in nm[x]['addresses'] else None,
                "identity": None # Placeholder for high-fidelity data
            }
            hosts_list.append(host_info)
            logging.info(f"Device Found! IP: {host_info['ip']} | MAC: {host_info['mac']}")

        if not hosts_list:
            logging.warning("No hosts found. Check your network settings!")

        # --- PHASE 2: PROTOCOL IDENTIFICATION (mDNS) ---
        # Only run if we hosts are found to correlate with
        if hosts_list:
            logging.info("[Phase 2] Listening for mDNS Identities...")
            
            # Run mDNS listener for 5 seconds
            mdns_data = run_mdns_scan(scan_duration=5)
            
            # MERGE LOGIC: Match mDNS results to Nmap results by IP
            for host in hosts_list:
                ip = host['ip']
                if ip in mdns_data:
                    # Enrich host record with specific model info
                    host['identity'] = mdns_data[ip]
                    
                    # Generate and validate CPE against NVD database
                    detected_cpe = generate_cpe(host['identity'])
                    host['cpe_suggestion'], host['cpe_validation_status'] = validate_cpe(detected_cpe)
                    
                    logging.info(f"--> Identity Confirmed for {ip}: {host['identity']['vendor']} {host['identity']['model']}")
        
        # --- PHASE 3: PROTOCOL IDENTIFICATION (HTTP) ---
        # Probe devices for HTTP services on common ports
        if hosts_list:
            logging.info("[Phase 3] Probing HTTP Services...")
            
            # Extract IPs from hosts_list
            ip_list = [host['ip'] for host in hosts_list]
            
            # Run HTTP fingerprinting
            http_data = run_http_scan(ip_list, ports=[80, 8080, 8081])
            
            # MERGE LOGIC: Match HTTP results to Nmap results by IP
            for host in hosts_list:
                ip = host['ip']
                if ip in http_data:
                    # If identity doesn't exist yet, create it; otherwise merge
                    if not host['identity']:
                        host['identity'] = http_data[ip]
                        
                        # Generate and validate CPE against NVD database
                        detected_cpe = generate_cpe(host['identity'])
                        host['cpe_suggestion'], host['cpe_validation_status'] = validate_cpe(detected_cpe)
                        
                        logging.info(f"--> Identity Confirmed for {ip}: {host['identity']['vendor']} {host['identity']['model']}")
                    else:
                        # Merge HTTP data with existing identity
                        host['identity'].update(http_data[ip])

        # --- PHASE 4: PROTOCOL IDENTIFICATION (SSH) ---
        # Probe devices for SSH services on port 22
        if hosts_list:
            logging.info("[Phase 4] Probing SSH Services...")
            
            # Extract IPs from hosts_list
            ip_list = [host['ip'] for host in hosts_list]
            
            # Run SSH fingerprinting
            ssh_data = run_ssh_scan(ip_list, port=22)
            
            # MERGE LOGIC: Match SSH results to Nmap results by IP
            for host in hosts_list:
                ip = host['ip']
                if ip in ssh_data:
                    # If identity doesn't exist yet, create it; otherwise merge
                    if not host['identity']:
                        host['identity'] = ssh_data[ip]
                        
                        # Generate and validate CPE against NVD database
                        detected_cpe = generate_cpe(host['identity'])
                        host['cpe_suggestion'], host['cpe_validation_status'] = validate_cpe(detected_cpe)
                        
                        logging.info(f"--> Identity Confirmed for {ip}: {host['identity']['vendor']} {host['identity']['model']}")
                    else:
                        # Merge SSH data with existing identity
                        host['identity'].update(ssh_data[ip])

        # --- PHASE 5: VULNERABILITY ANALYSIS & RISK SCORING ---
        logging.info("[Phase 5] Analyzing vulnerabilities and calculating risk scores...")
        
        for host in hosts_list:
            # Skip devices without validated CPE
            if not host.get('cpe_suggestion'):
                logging.debug(f"Skipping CVE lookup for {host['ip']} - no CPE")
                host['cve_results'] = {'cve_count': 0, 'cves': []}
                host['risk_assessment'] = {
                    'risk_score': 0,
                    'risk_level': 'Unknown',
                    'confidence': 'Low',
                    'factors': {}
                }
                host['recommendations'] = []
                continue
            
            # Query NVD for CVEs
            logging.info(f"Querying CVEs for {host['ip']} ({host['cpe_suggestion']})")
            cve_results = query_cves_for_cpe(host['cpe_suggestion'], max_cves=100)
            host['cve_results'] = cve_results
            
            # Calculate risk score
            risk_assessment = calculate_device_risk_score(host)
            host['risk_assessment'] = risk_assessment
            
            # Generate recommendations
            recommendations = generate_recommendations(host)
            host['recommendations'] = recommendations
            
            logging.info(f"--> {host['ip']}: {cve_results['cve_count']} CVEs, Risk: {risk_assessment['risk_level']} ({risk_assessment['risk_score']}/100)")

        # --- PHASE 6: REPORT GENERATION ---
        logging.info("[Phase 6] Generating security report...")
        
        # Calculate network-wide risk summary
        network_summary = calculate_network_risk_summary(hosts_list)
        
        # Build final report structure for dashboard
        report = {
            'scan_info': {
                'timestamp': datetime.utcnow().isoformat(),
                'subnet': target,
                'duration': None  # Could calculate if we track start time
            },
            'network_summary': network_summary,
            'devices': hosts_list
        }
        
        # Save to output file (or default to discovery-scan.json)
        output_file = output if output else "/app/shared/discovery-scan.json"
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        logging.info(f"Report written to {output_file}")
        
        # If custom output was specified, also save to discovery-scan.json for dashboard
        if output and output != "/app/shared/discovery-scan.json":
            dashboard_output = "/app/shared/discovery-scan.json"
            with open(dashboard_output, 'w') as f:
                json.dump(report, f, indent=2)
            logging.info(f"Dashboard data also saved to {dashboard_output}")
        
        # Print summary
        logging.info("\n" + "="*60)
        logging.info("SCAN SUMMARY")
        logging.info("="*60)
        logging.info(f"Total Devices: {network_summary['total_devices']}")
        logging.info(f"Devices at Risk: {network_summary['devices_at_risk']}")
        logging.info(f"Total CVEs: {network_summary['total_cves']}")
        logging.info(f"Network Risk Level: {network_summary['network_risk_level']}")
        logging.info(f"Average Risk Score: {network_summary['average_risk_score']}/100")
        logging.info("="*60)

    except Exception as e:
        logging.error(f"Discovery failed: {e}")
    logging.info("--- Discovery Complete ---")


if __name__ == "__main__":
    ## Accept parameters from the command line
    parser = argparse.ArgumentParser(description="STR Sentinel Network Discovery")
    parser.add_argument('subnet', type=str, nargs='?', default=os.getenv('STR_SUBNET', '172.20.0.0/24'), help='Target subnet to scan')
    parser.add_argument('--output', type=str, help='Optional output file (JSON)')
    parser.add_argument('--log', type=str, default=None, help='Optional log file')
    args = parser.parse_args()

    ## Log configuration
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s %(levelname)s: %(message)s',
        filename=args.log,
        filemode='w' if args.log else None
    )

    time.sleep(2)  # Small sleep to ensure test containers are all running
    run_discovery(args.subnet, args.output)