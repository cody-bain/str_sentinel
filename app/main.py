import nmap
import time
import argparse
import os
import logging
import json
# Protocol Handlers
from protocol_handlers.mdns_handler import run_mdns_scan
from protocol_handlers.http_handler import run_http_scan

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
                    
                    # Generate preliminary CPE
                    vendor = host['identity'].get('vendor', 'unknown').lower().replace(" ", "_")
                    model = host['identity'].get('model', 'unknown').lower().replace(" ", "_")
                    host['cpe_suggestion'] = f"cpe:2.3:h:{vendor}:{model}:*:*:*:*:*:*:*"
                    
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
                        
                        # Generate preliminary CPE
                        vendor = host['identity'].get('vendor', 'unknown').lower().replace(" ", "_")
                        model = host['identity'].get('model', 'unknown').lower().replace(" ", "_").replace("-", "_")
                        host['cpe_suggestion'] = f"cpe:2.3:h:{vendor}:{model}:*:*:*:*:*:*:*"
                        
                        logging.info(f"--> Identity Confirmed for {ip}: {host['identity']['vendor']} {host['identity']['model']}")
                    else:
                        # Merge HTTP data with existing identity
                        host['identity'].update(http_data[ip])

        # --- PHASE 4: PROTOCOL IDENTIFICATION (SSH) ---

        # --- PHASE 5: REPORTING (NEEDS DEVELOPMENT) ---
        if output:
            with open(output, 'w') as f:
                json.dump(hosts_list, f, indent=2)
            logging.info(f"Results written to {output}")

    except Exception as e:
        logging.error(f"Discovery failed: {e}")
    logging.info("--- Discovery Complete ---")


if __name__ == "__main__":
    ## Accept parameters from the command line
    parser = argparse.ArgumentParser(description="STR Sentinel Network Discovery")
    parser.add_argument('--subnet', type=str, default=os.getenv('STR_SUBNET', '172.20.0.0/24'), help='Target subnet to scan')
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