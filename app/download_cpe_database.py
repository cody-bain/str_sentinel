#!/usr/bin/env python3

'''
CODE GENERATED WITH ASSISTANCE FROM VARIOUS AI TOOLS.
ALL AI-GENERATED CONTENT WAS REVIEWED, REVISED, AND ADAPTED TO MEET STR SENTINEL REQUIREMENTS.
'''

"""
Download complete CPE dictionary from NVD API for local searching.
Run this once to cache all CPEs, then update periodically (weekly/monthly).
"""

import requests
import json
import os
import time
from dotenv import load_dotenv

load_dotenv('/app/.env')

NVD_API_KEY = os.getenv('NVD_API_KEY')
NVD_CPE_API = "https://services.nvd.nist.gov/rest/json/cpes/2.0"
OUTPUT_FILE = "/app/shared/cpe_dictionary.json"

def download_all_cpes():
    """
    Download ALL CPEs from NVD API and save to local JSON file.
    This may take 10-30 minutes depending on API key and total CPEs (~250k+).
    """
    headers = {}
    if NVD_API_KEY:
        headers['apiKey'] = NVD_API_KEY
        print(f"✓ Using NVD API key (50 requests/30sec)", flush=True)
    else:
        print("⚠ No API key - using public rate limit (5 requests/30sec)", flush=True)
    
    all_cpes = []
    start_index = 0
    results_per_page = 100
    
    print(f"\nDownloading CPE dictionary from NVD...", flush=True)
    print(f"   Saving to: {OUTPUT_FILE}\n", flush=True)
    
    # First request to get total count
    params = {
        'resultsPerPage': results_per_page,
        'startIndex': 0
    }
    
    try:
        response = requests.get(NVD_CPE_API, params=params, headers=headers, timeout=30)
        if response.status_code != 200:
            print(f"Error: API returned status {response.status_code}")
            return False
        
        data = response.json()
        total_results = data.get('totalResults', 0)
        total_pages = (total_results + results_per_page - 1) // results_per_page
        
        print(f"Total CPEs to download: {total_results:,}", flush=True)
        print(f"Total pages: {total_pages}", flush=True)
        print(f"Estimated time: {total_pages * (0.6 if NVD_API_KEY else 6) / 60:.1f} minutes\n", flush=True)
        
        # Process first page
        for item in data.get('products', []):
            cpe_data = item.get('cpe', {})
            all_cpes.append({
                'cpeName': cpe_data.get('cpeName'),
                'cpeNameId': cpe_data.get('cpeNameId'),
                'titles': cpe_data.get('titles', []),
                'deprecated': cpe_data.get('deprecated', False)
            })
        
        print(f"Page 1/{total_pages} - {len(all_cpes):,} CPEs", flush=True)
        
        # Download remaining pages
        start_index = results_per_page
        page = 2
        
        while len(all_cpes) < total_results:
            params['startIndex'] = start_index
            
            # Rate limiting
            if NVD_API_KEY:
                time.sleep(0.6)  # 50 req/30sec = ~0.6sec between requests
            else:
                time.sleep(6)  # 5 req/30sec = 6sec between requests
            
            response = requests.get(NVD_CPE_API, params=params, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                products = data.get('products', [])
                
                if not products:
                    break
                
                for item in products:
                    cpe_data = item.get('cpe', {})
                    all_cpes.append({
                        'cpeName': cpe_data.get('cpeName'),
                        'cpeNameId': cpe_data.get('cpeNameId'),
                        'titles': cpe_data.get('titles', []),
                        'deprecated': cpe_data.get('deprecated', False)
                    })
                
                # Progress update every page
                percent = (len(all_cpes) / total_results) * 100
                print(f"✓ Page {page}/{total_pages} - {len(all_cpes):,}/{total_results:,} CPEs ({percent:.1f}%)", flush=True)
                
                start_index += results_per_page
                page += 1
            else:
                print(f"⚠ Warning: Page {page} failed with status {response.status_code}")
                break
        
        # Save to file
        print(f"\nSaving {len(all_cpes):,} CPEs to {OUTPUT_FILE}...", flush=True)
        
        output_data = {
            'download_date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_cpes': len(all_cpes),
            'cpes': all_cpes
        }
        
        with open(OUTPUT_FILE, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        file_size_mb = os.path.getsize(OUTPUT_FILE) / (1024 * 1024)
        print(f"Success! Downloaded {len(all_cpes):,} CPEs ({file_size_mb:.1f} MB)", flush=True)
        print(f"   File: {OUTPUT_FILE}", flush=True)
        
        return True
        
    except Exception as e:
        print(f"Error downloading CPEs: {e}")
        return False


if __name__ == '__main__':
    print("=" * 60)
    print("  NVD CPE Database Downloader")
    print("=" * 60)
    
    success = download_all_cpes()
    
    if success:
        print("\nCPE database ready for offline searching!")
        print("   Run scans normally - they will now use local database.\n")
    else:
        print("\nDownload failed. Check your API key and connection.\n")
