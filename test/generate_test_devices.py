"""
Generate 100 test devices from CPE database for validation testing
Focus on IoT devices relevant to short-term rental properties
"""

import json
import random
import sys
import os
from collections import defaultdict

'''
CODE GENERATED WITH ASSISTANCE FROM VARIOUS AI TOOLS.
ALL AI-GENERATED CONTENT WAS REVIEWED, REVISED, AND ADAPTED TO MEET STR SENTINEL REQUIREMENTS.
'''

# Add app directory to path for imports
sys.path.insert(0, '/app')

# Load CPE database
with open('/app/shared/cpe_dictionary.json', 'r') as f:
    cpe_data = json.load(f)

cpes = cpe_data['cpes']

# STR-relevant IoT vendors and device types
STR_VENDORS = {
    # Security cameras
    'hikvision', 'axis', 'dahua', 'ubiquiti', 'arlo', 'nest', 'ring', 'wyze', 
    'lorex', 'amcrest', 'vivotek', 'hanwha', 'geovision', 'bosch', 'samsung',
    # Smart locks
    'august', 'yale', 'schlage', 'kwikset', 'lockly', 'ultraloq',
    # Smart home hubs & thermostats
    'google', 'amazon', 'apple', 'ecobee', 'honeywell', 'nest_labs',
    # Network equipment
    'cisco', 'ubnt', 'netgear', 'tp-link', 'tplink', 'linksys', 'dlink', 'd-link',
    'asus', 'unifi', 'mikrotik', 'aruba',
    # Streaming & media
    'roku', 'sonos', 'sony', 'lg', 'samsung', 'vizio', 'philips',
    # Smart lighting
    'philips', 'lutron', 'leviton', 'lifx', 'tp-link',
    # Voice assistants
    'amazon', 'google', 'apple',
    # NAS & storage
    'synology', 'qnap', 'western_digital', 'seagate',
    # Printers
    'hp', 'canon', 'epson', 'brother',
    # Other IoT
    'belkin', 'wemo', 'smartthings', 'hubitat', 'insteon'
}

# Device keywords that indicate STR-relevant IoT devices
STR_DEVICE_KEYWORDS = [
    'camera', 'nvr', 'dvr', 'surveillance', 'video', 'doorbell', 'ipcam',
    'lock', 'access_control',
    'thermostat', 'hvac',
    'router', 'switch', 'gateway', 'access_point', 'wireless_controller', 'wifi',
    'apple_tv', 'roku', 'chromecast', 'fire_tv', 'streaming_stick',
    'speaker', 'soundbar',
    'light', 'lighting', 'dimmer',
    'echo', 'alexa', 'homepod',
    'diskstation', 'nas',
    'printer', 'laserjet', 'officejet',
    'smart_plug', 'outlet', 'sensor', 'hub_controller', 'bridge',
    '_firmware', '_os'  # Underscore prefix to match firmware/os as whole words
]

# Vendors to EXCLUDE (catch-all for generic software)
EXCLUDE_KEYWORDS = [
    'project', 'wordpress', 'joomla', 'drupal', 'cms', 'plugin',
    'library', 'framework', 'sdk', 'api', 'node',
    'python', 'ruby', 'perl', 'php', 'java',
    'omniauth', 'oauth', 'chart', 'graph', 'maps'
]

# Group CPEs by vendor for diversity
vendor_cpes = defaultdict(list)
for cpe in cpes:
    cpe_name = cpe['cpeName']
    parts = cpe_name.split(':')
    if len(parts) >= 6:
        cpe_type = parts[2]  # h, a, or o
        vendor = parts[3]
        product = parts[4]
        version = parts[5]
        
        # Skip if deprecated or missing key fields
        if cpe.get('deprecated', False):
            continue
        if vendor in ['*', '-'] or product in ['*', '-']:
            continue
        
        # Filter for STR-relevant vendors
        vendor_lower = vendor.lower().replace('_', '').replace('-', '')
        if not any(str_vendor in vendor_lower for str_vendor in STR_VENDORS):
            continue
        
        # Filter OUT generic software/plugins
        product_lower = product.lower()
        if any(exclude in product_lower for exclude in EXCLUDE_KEYWORDS):
            continue
        
        # Filter FOR STR-relevant device types
        is_relevant = any(keyword in product_lower for keyword in STR_DEVICE_KEYWORDS)
        
        # For firmware/OS, be stricter
        if cpe_type == 'o':
            if 'firmware' in product_lower or product_lower.endswith('_os'):
                is_relevant = True
            else:
                is_relevant = False
        
        # For hardware, prioritize physical devices
        if cpe_type == 'h':
            is_relevant = True  # Most hardware CPEs are physical devices
        
        if not is_relevant:
            continue
            
        vendor_cpes[vendor].append({
            'cpe': cpe_name,
            'type': cpe_type,
            'vendor': vendor,
            'product': product,
            'version': version
        })

# Select diverse devices (max 5 per vendor for diversity)
test_devices = []
vendors_used = set()

# Prioritize getting variety
vendor_list = sorted(vendor_cpes.keys())
random.shuffle(vendor_list)

# First pass: Get devices from as many different vendors as possible
for vendor in vendor_list:
    if len(test_devices) >= 100:
        break
    if vendor_cpes[vendor]:
        # Prioritize hardware devices for IoT realism
        hardware = [d for d in vendor_cpes[vendor] if d['type'] == 'h']
        if hardware:
            device = random.choice(hardware)
        else:
            device = random.choice(vendor_cpes[vendor])
        test_devices.append(device)
        vendors_used.add(vendor)

# Second pass: Fill remaining slots with more devices from existing vendors
if len(test_devices) < 100:
    for vendor in vendors_used:
        if len(test_devices) >= 100:
            break
        remaining = [d for d in vendor_cpes[vendor] if d not in test_devices]
        for device in remaining[:4]:  # Add up to 4 more per vendor
            if len(test_devices) >= 100:
                break
            test_devices.append(device)

# Ensure we have at least 100 if possible
while len(test_devices) < 100 and len(vendor_cpes) > 0:
    for vendor in vendor_cpes:
        if len(test_devices) >= 100:
            break
        remaining = [d for d in vendor_cpes[vendor] if d not in test_devices]
        if remaining:
            test_devices.append(random.choice(remaining))

# Format as discovery-scan.json format
formatted_devices = []
for i, device in enumerate(test_devices[:100]):
    # Determine detection method based on device type and product
    product_lower = device['product'].lower()
    
    # SSH: network equipment, NAS
    if any(keyword in product_lower for keyword in ['router', 'switch', 'gateway', 'nas', 'diskstation', 'access_point', 'wireless_controller']):
        detection_method = 'SSH'
    # mDNS: streaming devices, smart speakers, thermostats
    elif any(keyword in product_lower for keyword in ['apple_tv', 'roku', 'chromecast', 'sonos', 'echo', 'homepod', 'nest', 'ecobee']):
        detection_method = 'mDNS'
    # HTTP: cameras, locks, printers, firmware - everything else
    else:
        detection_method = 'HTTP'
    
    # Format vendor/model/version for identity
    vendor_display = device['vendor'].replace('_', ' ').replace('-', ' ').title()
    product_display = device['product'].replace('_', ' ').replace('-', ' ')
    version_display = device['version'] if device['version'] not in ['*', '-'] else 'Unknown'
    
    formatted_device = {
        "ip": f"192.168.1.{i+10}",
        "status": "up",
        "hostname": None,
        "mac": f"00:11:22:33:{i//256:02x}:{i%256:02x}",
        "identity": {
            "vendor": vendor_display,
            "model": product_display,
            "version": version_display,
            "detection_method": detection_method
        },
        "cpe_suggestion": None,  # Will be generated by validation
        "cpe_validation_status": None,
        "expected_cpe": device['cpe']  # Ground truth for testing
    }
    formatted_devices.append(formatted_device)

# Save test dataset
output = {
    "test_date": "2026-02-11",
    "total_devices": len(formatted_devices),
    "description": "100 IoT devices relevant to short-term rental properties, detectable via HTTP/SSH/mDNS",
    "devices": formatted_devices
}

# Ensure /test directory exists
os.makedirs('/test', exist_ok=True)

with open('/test/test-devices.json', 'w') as f:
    json.dump(output, f, indent=2)

# Calculate statistics
http_count = sum(1 for d in formatted_devices if d['identity']['detection_method'] == 'HTTP')
ssh_count = sum(1 for d in formatted_devices if d['identity']['detection_method'] == 'SSH')
mdns_count = sum(1 for d in formatted_devices if d['identity']['detection_method'] == 'mDNS')
unique_vendors = len(set(d['vendor'] for d in test_devices))
type_counts = {'h': 0, 'a': 0, 'o': 0}
for d in test_devices:
    type_counts[d['type']] += 1

print(f"✅ Generated {len(formatted_devices)} STR-relevant IoT test devices")
print(f"📊 Vendor diversity: {unique_vendors} unique vendors")
print(f"📊 Detection methods: {http_count} HTTP, {ssh_count} SSH, {mdns_count} mDNS")
print(f"📊 Type breakdown: {type_counts['h']} hardware, {type_counts['a']} applications, {type_counts['o']} OS/firmware")
print(f"💾 Saved to /test/test-devices.json")
