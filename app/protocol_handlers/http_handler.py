import requests
import re
import logging
import urllib3
import subprocess
import json

# Suppress SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Recog gem XML file locations
RECOG_FILES = {
    'server': '/var/lib/gems/3.3.0/gems/recog-3.1.25/recog/xml/http_servers.xml',
    'auth': '/var/lib/gems/3.3.0/gems/recog-3.1.25/recog/xml/http_wwwauth.xml',
}


def recog_match(data, xml_file):
    '''
    Call recog_match to fingerprint a string.
    Returns dict with vendor/product or None.
    '''
    try:
        # Same as typing in terminal: 'recog_match --format json http_servers.xml -'
        result = subprocess.run(
            ['recog_match', '--format', 'json', xml_file, '-'],
            input=data.encode(),
            capture_output=True,
            timeout=2
        )
        
        if result.returncode == 0 and result.stdout:
            # Recog outputs JSON. Extract the 'match' object
            output = json.loads(result.stdout.decode().strip())
            return output.get('match')
    except Exception as e:
        logging.debug(f"Recog failed: {e}")
    
    return None


def detect_device_from_http(headers, html, title):
    '''
    Identify device from HTTP headers using Recog.
    Returns (vendor, model) tuple.
    '''
    # Try WWW-Authenticate header first (most device-specific)
    if 'WWW-Authenticate' in headers:
        match = recog_match(headers['WWW-Authenticate'], RECOG_FILES['auth'])
        if match:
            vendor = match.get('service.vendor') or match.get('hw.vendor')
            model = match.get('service.product') or match.get('hw.product')
            if vendor:
                return vendor, model
    
    # Try Server header (may have multiple values like "nginx, Hikvision-Webs")
    if 'Server' in headers:
        server_header = headers['Server']
        
        # Check each comma-separated value (last to first b/c most specific usually last)
        for value in reversed(server_header.split(',')):
            match = recog_match(value.strip(), RECOG_FILES['server'])
            if match:
                vendor = match.get('service.vendor') or match.get('hw.vendor')
                model = match.get('service.product') or match.get('hw.product')
                
                # Skip generic servers if there is more to check
                if vendor not in ['nginx', 'Apache', 'IIS'] or ',' not in server_header:
                    return vendor, model
    
    return None, None

def probe_http_service(ip, port=80, timeout=3):
    '''
    Probe a single IP:port for HTTP service and extract device information.
    Returns device info dict or None if no HTTP service.
    '''
    urls = [f"http://{ip}:{port}"]
    
    for url in urls:
        try:
            response = requests.get(url, timeout=timeout, verify=False, allow_redirects=True)
            
            # Extract identifying information
            headers = response.headers
            html = response.text
            
            # Parse HTML title
            title_match = re.search(r'<title>([^<]+)</title>', html, re.IGNORECASE)
            title = title_match.group(1).strip() if title_match else None
            
            # Detect device using pattern matching
            vendor, model = detect_device_from_http(headers, html, title)
            
            # Extract version from Server header if available
            version = "Unknown"
            if 'Server' in headers:
                server = headers['Server']
                version_match = re.search(r'[\d\.]+', server)
                if version_match:
                    version = version_match.group(0)
            
            # Build identity dictionary (consistent structure with mDNS handler)
            identity = {
                "vendor": vendor or "Unknown",
                "model": model or "Unknown",
                "version": version,
                "detection_method": "HTTP",
                "http_url": url,
                "http_title": title or "Unknown",
                "http_server": headers.get('Server', 'Unknown')
            }
            
            if vendor and vendor != "Unknown":
                logging.info(f"[HTTP] Found identity at {ip}:{port} - {identity['vendor']} {identity['model']}")
            else:
                logging.debug(f"[HTTP] HTTP service at {ip}:{port} but no device identification")
            
            return identity
            
        except requests.exceptions.RequestException:
            # Silent fail. No HTTP service on this port
            continue
        except Exception as e:
            logging.debug(f"[HTTP] Error probing {url}: {e}")
            continue
    
    return None


def run_http_scan(ip_list, ports=[80, 8080, 8081], timeout=3):
    '''
    Scans a list of IPs for HTTP services on common ports.
    Returns a dictionary keyed by IP address.
    '''
    logging.info(f"--- Starting HTTP Fingerprinting on {len(ip_list)} hosts ---")
    
    found_devices = {}
    
    for ip in ip_list:
        for port in ports:
            result = probe_http_service(ip, port, timeout)
            if result:
                found_devices[ip] = result
                break  # Found HTTP service. No need to try other ports
    
    logging.info(f"--- HTTP Fingerprinting Complete: {len(found_devices)} devices identified ---")
    return found_devices

'''
1. Call run_http_scan(ip_list)
2. run_http_scan() probes each IP on ports 80, 8080, 8081 (standard http ports)
3. probe_http_service() makes HTTP GET request and extracts headers, title, HTML
4. detect_device_from_http() calls recog_match (Ruby subprocess) to fingerprint via Recog patterns
5. recog_match checks WWW-Authenticate header first, then Server header (comma-separated values)
6. Return dictionary formatted as follows:
    {
        "172.20.0.10": {
            "vendor": "Hikvision",
            "model": "Hikvision Web Server",
            "version": "Unknown",
            "detection_method": "HTTP",
            ...
        }
    }
'''