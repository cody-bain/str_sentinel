import nmap
import time
import argparse
import os
import logging
import json


def run_discovery(target, output=None):

    '''
    Function designed to run ARP Passive Discovery Scan on Local STR Network.
    '''

    nm = nmap.PortScanner()
    logging.info(f"--- STR Sentinel Starting Discovery on {target} ---")
    try:
        # Host Discovery Scan
        nm.scan(hosts=target, arguments='-sn')
        hosts_list = []

        ## Add host infomration to hosts_list
        for x in nm.all_hosts():
            host_info = {
                "ip": x,
                "status": nm[x]['status']['state'],
                "hostname": nm[x].hostname() if 'hostname' in nm[x] else None,
                "mac": nm[x]['addresses'].get('mac') if 'addresses' in nm[x] and 'mac' in nm[x]['addresses'] else None
            }

            hosts_list.append(host_info)
            logging.info(f"Device Found! IP: {host_info['ip']} | Status: {host_info['status']} | Hostname: {host_info['hostname']} | MAC: {host_info['mac']}")

        if not hosts_list:
            logging.warning("No hosts found. Check your network settings!")

        # Dump hosts_list json to specified output file
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
