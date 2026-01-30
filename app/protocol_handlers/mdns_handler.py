from zeroconf import ServiceBrowser, Zeroconf
import socket
import time
import logging

class MDNSCollector:
    def __init__(self):
        self.found_devices = {}

    # Do nothing when a device leaves the network
    def remove_service(self, zeroconf, type, name):
        pass
    
    # Function automatically called when a device broadcasts on network
    def add_service(self, zeroconf, type, name):
        try:
            info = zeroconf.get_service_info(type, name)
            if info:
                ip = socket.inet_ntoa(info.addresses[0]) # Convert binary IP to string
                
                # Extract TXT records (extra info like model & version)
                # Decode bytes to strings (e.g., b'md' -> 'md')
                properties = {}
                if info.properties:
                    for k, v in info.properties.items():
                        decoded_key = k.decode('utf-8') if isinstance(k, bytes) else k
                        decoded_val = v.decode('utf-8') if isinstance(v, bytes) else v
                        properties[decoded_key] = decoded_val

                logging.debug(f"[mDNS] Properties for {ip}: {properties}")

                # Store the identity in dictionary. Try multiple common device property keys
                self.found_devices[ip] = {
                    "mdns_name": name,
                    "service_type": type,
                    "model": properties.get('md') or properties.get('model') or properties.get('product') or 'Unknown',
                    "version": properties.get('ve') or properties.get('version') or properties.get('sw') or 'Unknown',
                    "id": properties.get('id') or properties.get('deviceid') or properties.get('uuid') or 'Unknown',
                    "all_properties": properties if properties else None  # Include all properties for analysis
                }

                logging.info(f"[mDNS] Found Identity at {ip}: {self.found_devices[ip]['model']}")

        except Exception as e:
            logging.error(f"[mDNS] Error parsing service {name}: {e}")

def run_mdns_scan(scan_duration=5):
    '''
    Listens for mDNS broadcasts for `scan_duration` seconds.
    Returns a dictionary keyed by IP address.
    '''
    logging.info(f"--- Starting mDNS Active Listener ({scan_duration}s) ---")
    
    zeroconf = Zeroconf()
    listener = MDNSCollector()
    
    # Listen specifically for Google Cast (Nest) and generic HTTP
    # *** ADD MORE SERVICES TO LIST LATER ***
    services_to_track = [
        "_googlecast._tcp.local.",  # Nest Thermostats / Google Home
        "_http._tcp.local.",        # Generic Web Devices
        "_ssh._tcp.local."          # Some IoT SSH devices
    ]
    
    browser = ServiceBrowser(zeroconf, services_to_track, listener) # Tell zeroconf to listen for 'services_to_track'
    
    time.sleep(scan_duration) # Wait & return devices
    
    zeroconf.close()
    return listener.found_devices

'''
1. Call run_mdns_scan()
2. run_mdns_scan() listens for mDNS broadcasts
3. When a 'service_to_track' broadcasts, add_service() is called and extracts IP, model, version
4. After 5 seconds, scanning stops.
5. Return dictionary formatted as follows:
    {
        "172.20.0.35": {
            "model": "Nest Learning Thermostat",
            "version": "3.0",
            ...
        }
    }
'''