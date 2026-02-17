import requests
import logging
import os
import time
from dotenv import load_dotenv

# Some code snippets developed with assistance from generative AI tools. All AI-generated content was reviewed, revised, and adapted to meet STR Sentinel requirements.

# Load environment variables
load_dotenv('/app/.env')

# NVD API Configuration
NVD_API_KEY = os.getenv('NVD_API_KEY')
NVD_CVE_API = "https://services.nvd.nist.gov/rest/json/cves/2.0"

# In-memory cache for CVE queries
cve_cache = {}


def query_cves_for_cpe(cpe_string, max_cves=100):
    """
    Query NVD API to get all CVEs associated with a CPE string.
    
    Args:
        cpe_string: CPE 2.3 formatted string (e.g., "cpe:2.3:a:openbsd:openssh:7.6p1:*:*:*:*:*:*:*")
        max_cves: Maximum number of CVEs to retrieve (default: 100)
    
    Returns:
        Dictionary containing:
        - 'cpe': The CPE string queried
        - 'cve_count': Total number of CVEs found
        - 'cves': List of CVE dictionaries with id, descriptions, cvss scores, etc.
        - 'cached': Whether results came from cache
    """
    # Check cache first
    if cpe_string in cve_cache:
        logging.debug(f"[CVE Cache] Using cached results for {cpe_string}")
        cached_result = cve_cache[cpe_string].copy()
        cached_result['cached'] = True
        return cached_result
    
    headers = {}
    if NVD_API_KEY:
        headers['apiKey'] = NVD_API_KEY
    
    params = {
        'cpeName': cpe_string,
        'resultsPerPage': min(max_cves, 2000),  # NVD max is 2000
        'startIndex': 0
    }
    
    try:
        logging.info(f"[NVD CVE API] Querying vulnerabilities for: {cpe_string}")
        
        response = requests.get(NVD_CVE_API, params=params, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            vulnerabilities = data.get('vulnerabilities', [])
            total_results = data.get('totalResults', 0)
            
            logging.info(f"[NVD CVE API] Found {total_results} CVEs for {cpe_string}")
            
            # Extract relevant CVE information
            cve_list = []
            for vuln in vulnerabilities:
                cve_data = vuln.get('cve', {})
                cve_id = cve_data.get('id', 'N/A')
                
                # Get descriptions
                descriptions = cve_data.get('descriptions', [])
                description = descriptions[0].get('value', 'No description available') if descriptions else 'No description available'
                
                # Get CVSS scores (prioritize v3.1, then v3.0, then v2.0)
                metrics = cve_data.get('metrics', {})
                cvss_v31 = metrics.get('cvssMetricV31', [])
                cvss_v30 = metrics.get('cvssMetricV30', [])
                cvss_v2 = metrics.get('cvssMetricV2', [])
                
                cvss_score = None
                cvss_severity = None
                cvss_vector = None
                cvss_version = None
                
                if cvss_v31:
                    cvss_data = cvss_v31[0].get('cvssData', {})
                    cvss_score = cvss_data.get('baseScore')
                    cvss_severity = cvss_data.get('baseSeverity')
                    cvss_vector = cvss_data.get('vectorString')
                    cvss_version = '3.1'
                elif cvss_v30:
                    cvss_data = cvss_v30[0].get('cvssData', {})
                    cvss_score = cvss_data.get('baseScore')
                    cvss_severity = cvss_data.get('baseSeverity')
                    cvss_vector = cvss_data.get('vectorString')
                    cvss_version = '3.0'
                elif cvss_v2:
                    cvss_data = cvss_v2[0].get('cvssData', {})
                    cvss_score = cvss_data.get('baseScore')
                    cvss_severity = cvss_v2[0].get('baseSeverity', 'N/A')
                    cvss_vector = cvss_data.get('vectorString')
                    cvss_version = '2.0'
                
                # Get published and modified dates
                published = cve_data.get('published', 'N/A')
                last_modified = cve_data.get('lastModified', 'N/A')
                
                cve_list.append({
                    'id': cve_id,
                    'description': description,
                    'cvss_score': cvss_score,
                    'cvss_severity': cvss_severity,
                    'cvss_vector': cvss_vector,
                    'cvss_version': cvss_version,
                    'published': published,
                    'last_modified': last_modified,
                    'url': f"https://nvd.nist.gov/vuln/detail/{cve_id}"
                })
            
            result = {
                'cpe': cpe_string,
                'cve_count': total_results,
                'cves': cve_list,
                'cached': False
            }
            
            # Cache results
            cve_cache[cpe_string] = result
            
            return result
            
        elif response.status_code == 404:
            logging.warning(f"[NVD CVE API] No CVEs found for CPE: {cpe_string}")
            result = {
                'cpe': cpe_string,
                'cve_count': 0,
                'cves': [],
                'cached': False
            }
            cve_cache[cpe_string] = result
            return result
            
        else:
            logging.error(f"[NVD CVE API] Query failed with status {response.status_code}: {response.text}")
            return {
                'cpe': cpe_string,
                'cve_count': 0,
                'cves': [],
                'error': f"API error: {response.status_code}",
                'cached': False
            }
            
    except Exception as e:
        logging.error(f"[NVD CVE API] Query failed: {e}")
        return {
            'cpe': cpe_string,
            'cve_count': 0,
            'cves': [],
            'error': str(e),
            'cached': False
        }


def get_cve_summary(cve_results):
    """
    Generate a summary of CVE results by severity.
    
    Args:
        cve_results: Dictionary returned from query_cves_for_cpe()
    
    Returns:
        Dictionary with severity breakdown
    """
    if not cve_results or cve_results.get('cve_count', 0) == 0:
        return {
            'total': 0,
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0,
            'unknown': 0
        }
    
    summary = {
        'total': cve_results.get('cve_count', 0),
        'critical': 0,
        'high': 0,
        'medium': 0,
        'low': 0,
        'unknown': 0
    }
    
    for cve in cve_results.get('cves', []):
        severity = (cve.get('cvss_severity') or 'UNKNOWN').upper()
        
        if severity == 'CRITICAL':
            summary['critical'] += 1
        elif severity == 'HIGH':
            summary['high'] += 1
        elif severity == 'MEDIUM':
            summary['medium'] += 1
        elif severity == 'LOW':
            summary['low'] += 1
        else:
            summary['unknown'] += 1
    
    return summary
