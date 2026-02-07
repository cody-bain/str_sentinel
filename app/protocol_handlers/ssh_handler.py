import socket
import logging
import subprocess
import json

# Some code snippets developed with assistance from generative AI tools. All AI-generated content was reviewed, revised, and adapted to meet STR Sentinel requirements.

# Recog gem XML file location
RECOG_SSH_FILE = '/var/lib/gems/3.3.0/gems/recog-3.1.25/recog/xml/ssh_banners.xml'


def recog_match(banner, xml_file):
    '''
    Call recog_match to fingerprint SSH banner.
    Returns dict with vendor/product or None.
    '''
    try:
        result = subprocess.run(
            ['recog_match', '--format', 'json', xml_file, '-'],
            input=banner.encode(),
            capture_output=True,
            timeout=2
        )
        
        if result.returncode == 0 and result.stdout:
            output = json.loads(result.stdout.decode().strip())
            return output.get('match')
    except Exception as e:
        logging.debug(f"Recog SSH failed: {e}")
    
    return None


def detect_device_from_ssh(banner):
    '''
    Identify device from SSH banner using Recog.
    Returns (vendor, model, version) tuple.
    '''
    # Strip SSH protocol version prefix (e.g., "SSH-2.0-Cisco-1.25" -> "Cisco-1.25")
    # Recog patterns expect just the server string, not the full SSH protocol banner
    clean_banner = banner
    if banner.startswith('SSH-'):
        parts = banner.split('-', 2)  # Split on first two hyphens: ['SSH', '2.0', 'Cisco-1.25']
        if len(parts) >= 3:
            clean_banner = parts[2]  # Get everything after "SSH-2.0-"
    
    match = recog_match(clean_banner, RECOG_SSH_FILE)
    
    if match:
        vendor = match.get('service.vendor') or match.get('hw.vendor')
        model = match.get('service.product') or match.get('hw.product')
        version = match.get('service.version') or match.get('hw.version')
        return vendor, model, version
    
    return None, None, None


def probe_ssh_service(ip, port=22, timeout=3):
    '''
    Probe a single IP:port for SSH service and extract banner.
    Returns device info dict or None if no SSH service.
    '''
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((ip, port))
        
        # SSH servers send banner immediately after connection
        banner = sock.recv(1024).decode('utf-8', errors='ignore').strip()
        sock.close()
        
        if not banner.startswith('SSH'):
            logging.debug(f"[SSH] Port {port} on {ip} not SSH (banner: {banner[:50]})")
            return None
        
        # Detect device using Recog
        vendor, model, version = detect_device_from_ssh(banner)
        
        # Build identity dictionary (consistent structure with other handlers)
        identity = {
            "vendor": vendor or "Unknown",
            "model": model or "Unknown",
            "version": version or "Unknown",
            "detection_method": "SSH",
            "ssh_banner": banner
        }
        
        if vendor and vendor != "Unknown":
            logging.info(f"[SSH] Found identity at {ip}:{port} - {identity['vendor']} {identity['model']}")
        else:
            logging.debug(f"[SSH] SSH service at {ip}:{port} but no device identification (banner: {banner})")
        
        return identity
        
    except socket.timeout:
        logging.debug(f"[SSH] Connection timeout to {ip}:{port}")
        return None
    except ConnectionRefusedError:
        logging.debug(f"[SSH] Connection refused by {ip}:{port}")
        return None
    except Exception as e:
        logging.debug(f"[SSH] Error probing {ip}:{port}: {e}")
        return None


def run_ssh_scan(ip_list, port=22, timeout=3):
    '''
    Scans a list of IPs for SSH services.
    Returns a dictionary keyed by IP address.
    '''
    logging.info(f"--- Starting SSH Fingerprinting on {len(ip_list)} hosts ---")
    
    found_devices = {}
    
    for ip in ip_list:
        result = probe_ssh_service(ip, port, timeout)
        if result:
            found_devices[ip] = result
    
    logging.info(f"--- SSH Fingerprinting Complete: {len(found_devices)} devices identified ---")
    return found_devices


'''
1. Call run_ssh_scan(ip_list)
2. run_ssh_scan() probes each IP on port 22 (standard SSH port)
3. probe_ssh_service() opens socket, reads SSH banner (e.g., "SSH-2.0-OpenSSH_7.4")
4. detect_device_from_ssh() calls recog_match (Ruby subprocess) to fingerprint via Recog patterns
5. recog_match checks banner against 152 SSH patterns from ssh_banners.xml
6. Return dictionary formatted as follows:
    {
        "172.20.0.20": {
            "vendor": "Yale",
            "model": "Yale Smart Lock",
            "version": "1.2.3",
            "detection_method": "SSH",
            "ssh_banner": "SSH-2.0-Yale_Lock_1.2.3"
        }
    }
'''
