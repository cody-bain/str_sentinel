from zeroconf import Zeroconf, ServiceBrowser
import socket
import time

class IdentityListener:
    def __init__(self):
        self.results = {}

    def add_service(self, zc, type_, name):
        info = zc.get_service_info(type_, name)
        if info:
            ip = socket.inet_ntoa(info.addresses[0])
            # Extract the 'md' (Model) from TXT records
            props = {k.decode(): v.decode() for k, v in info.properties.items()}
            self.results[ip] = {
                "model": props.get('md', 'Unknown'),
                "version": props.get('ve', 'unknown'),
                "method": "mDNS"
            }

def probe_mdns(timeout=3):
    zc = Zeroconf()
    listener = IdentityListener()
    # Looking for Google/Nest style broadcasts
    browser = ServiceBrowser(zc, "_googlecast._tcp.local.", listener)
    time.sleep(timeout)
    zc.close()
    return listener.results