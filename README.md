# STR Sentinel (In Development)

**Cody Bain | Georgia Tech PUBP 6727**

An automated IoT security scanner for short-term rental (STR) properties that discovers network devices, identifies vulnerabilities, and generates actionable security reports.

---

## Project Overview

STR Sentinel performs automated security assessments of IoT devices in rental properties through a four-phase approach:

1. **Discovery** - Identifies all devices on the local network using nmap
2. **Fingerprinting** - Identifies device models and versions via mDNS, HTTP, and SSH protocols
3. **Vulnerability Analysis** - Matches devices against NIST NVD for known CVEs
4. **Reporting** - Generates security assessment reports with remediation guidance

### System Architecture

```
┌─────────────────────────────────────────────────────┐
│                   STR Sentinel                       │
├─────────────────────────────────────────────────────┤
│  Phase 1: Network Discovery (nmap)                  │
│  Phase 2: Protocol Fingerprinting (mDNS/HTTP/SSH)   │
│  Phase 3: CPE Matching & CVE Lookup (NVD)           │
│  Phase 4: Risk Scoring & Reporting                  │
└─────────────────────────────────────────────────────┘
```

---

## Getting Started

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for local development)

### Running the Simulation Environment

Start Simulated Environment:

```bash
docker-compose -f simulation/docker-compose.yml up -d --build
```

### Simulated Network Environment

The testing environment includes three simulated IoT devices on an isolated Docker network (172.20.0.0/24):

| Device Type | IP Address | Protocols | MAC Address (OUI) |
|------------|------------|-----------|-------------------|
| Hikvision DS-2CD2032-I Camera | 172.20.0.10 | HTTP (80) | 00:40:8C (Hikvision) |
| Network Device (OpenSSH 7.6p1) | 172.20.0.20 | SSH (22) | 00:1E:14 (Cisco Systems) |
| Apple TV (11.0) | 172.20.0.35 | mDNS (AirPlay) | 00:03:93 (Apple) |

### Running a Discovery Scan

Execute a network scan from the Sentinel container:

```bash
# Run with default docker subnet (172.20.0.0/24), output file, and log file
docker exec -it str_sentinel_app python main.py --output shared/discovery-scan.json 

# Specify a custom subnet
docker exec -it str_sentinel_app python main.py --subnet 192.168.1.0/24

# With optional output file
docker exec -it str_sentinel_app python main.py --output custom-scan.json
```

Scan results are saved to `app/shared/discovery-scan.json`

---

## Project Structure

```
str_sentinel/
├── app/
│   ├── main.py                    # Primary discovery orchestrator
│   ├── protocol_handlers/
│   │   ├── mdns_handler.py        # mDNS device identification
│   │   ├── http_handler.py        # HTTP fingerprinting via Recog
│   │   └── ssh_handler.py         # SSH banner fingerprinting via Recog
│   ├── shared/
│   │   └── discovery-scan.json    # Scan results output
│   ├── requirements.txt
│   └── Dockerfile                 # Includes Ruby + Recog gem
├── simulation/
│   ├── docker-compose.yml         # Simulation environment
│   └── nest.service               # Avahi mDNS configuration
└── README.md
```

---

## Implementation Status

### Phase 1: Network Discovery - COMPLETE
- ✅ Nmap host discovery operational (`-sn` flag for ARP scanning)
- ✅ MAC address and IP detection working
- ✅ Vendor-specific MAC OUIs tracked

### Phase 2: Protocol Fingerprinting - COMPLETE
- ✅ mDNS handler complete (Google Cast/Nest detection via Zeroconf)
- ✅ HTTP handler complete (Rapid7 Recog integration)
  - 680+ professional-grade fingerprint patterns
  - Detects web servers, IoT devices, embedded systems
  - Intelligent priority: specific device patterns before generic servers
- ✅ SSH handler complete (Banner fingerprinting via Recog)
  - 152 SSH server patterns for device identification
  - Protocol prefix stripping before pattern matching
  - Version extraction with CPE formatting

### Phase 3: Vulnerability Analysis - COMPLETE
- ✅ NVD-compatible CPE generation
  - Model extraction from HTTP titles (DS-2CD2032-I from Hikvision)
  - Version formatting for CPE 2.3 specification
  - Smart application vs hardware detection
- ✅ Local CPE Database (1.5M+ entries)
  - Downloaded complete NVD CPE dictionary (456MB)
  - In-memory search (<1 second vs 4+ minutes API pagination)
  - Offline operation capability
- ✅ Fuzzy CPE Matching Algorithm
  - 65% similarity threshold with fallback
- ✅ NVD API Integration
  - CVE count queries for validated CPEs
  - API key support with rate limiting
- ✅ **Validation Testing: 95% accuracy on 100 diverse devices**

### Phase 4: Reporting - PLANNED
- CVSS-based risk scoring algorithm
- Vulnerability report generation
- Web-based dashboard for scan results visualization
- PDF report generation with executive summary for both guests and hosts
- Network topology visualization
- Remediation recommendations engine
- Web dashboard
- PDF report generation
  - Host: Network Vulnerabilities + Legal Framework
  - Guest: Privacy & Information Security


---

## Technical Architecture

### Fingerprinting Strategy

STR Sentinel uses a **hybrid detection approach** combining multiple protocols to maximize device identification:

**Multi-Protocol Detection Pipeline:**
```
┌──────────────────────────────────────────────────────────┐
│ Phase 1: nmap Host Discovery (-sn ARP scan)             │
│  └─> Returns: IP, MAC, hostname                         │
└──────────────────────────────────────────────────────────┘
                      ↓
┌──────────────────────────────────────────────────────────┐
│ Phase 2: Protocol Fingerprinting (Parallel)             │
│  ├─> mDNS: Zeroconf service browser (TXT records)       │
│  ├─> HTTP: Recog gem (Server headers, WWW-Auth)         │
│  └─> SSH: Banner grabbing + Recog gem                   │
└──────────────────────────────────────────────────────────┘
                      ↓
┌──────────────────────────────────────────────────────────┐
│ Phase 3: Data Correlation & CPE Generation              │
│  └─> Merge protocol results by IP address               │
└──────────────────────────────────────────────────────────┘
```

### Recog Integration

Rather than writing custom regex patterns, STR Sentinel leverages **Rapid7's Recog framework** via Ruby subprocess calls:

- **Industry-Standard Patterns:** 680+ fingerprints maintained by security professionals
- **Ruby Integration:** Calls native `recog_match` command via Python subprocess
- **XML Databases:** Uses official Recog gem installation (http_servers.xml, http_wwwauth.xml, ssh_banners.xml)
- **Smart Parsing:** Handles comma-separated Server headers, prioritizes specific devices over generic servers

---

## Testing

## CPE to CVE Validation 

### Methodology

To validate the CPE fuzzy matching algorithm's accuracy, we conducted systematic testing against 100 diverse devices from the NVD CPE database.

**Testing Scripts:**
- `test/generate_test_devices.py` - Generates 100 STR-relevant IoT test devices from CPE database
- `test/evaluate_cpe_matching.py` - Executes validation test with CVE queries against NVD
- Results saved to `test/cpe-matching-report.json`

**Running the Tests:**
```bash
# Generate test devices (re-run for new random selection)
docker exec str_sentinel_app python /test/generate_test_devices.py

# Run CPE matching evaluation (~60 seconds with API key, ~10 minutes without)
docker exec str_sentinel_app python /test/evaluate_cpe_matching.py

# View results
cat test/cpe-matching-report.json
```

**Test Design:**
1. **Device Selection:** 100 IoT devices commonly found in short-term rental properties
2. **Vendor Focus:** Security cameras, network equipment, smart home devices, printers, streaming devices
3. **Ground Truth:** Each device's official CPE from NVD serves as expected match
4. **Device Simulation:** Formatted as discovery-scan.json with vendor/model/version, assigned realistic detection protocols (HTTP for cameras/printers, SSH for routers/NAS, mDNS for streaming devices)
5. **Validation Process:** Each device undergoes full CPE generation → fuzzy matching → NVD validation
6. **CVE Verification:** Validated CPEs queried against NVD CVE API for vulnerability counts

**Metrics Assessed:**
- **Validation Rate:** Percentage of devices successfully matched to NVD CPE database
- **Exact Match Rate:** Percentage where vendor AND product match ground truth
- **Vendor Match Rate:** Percentage with correct vendor identification
- **Product Match Rate:** Percentage with correct product identification
- **CVE Coverage:** Number of devices with known vulnerabilities

### Results (February 11, 2026)

```
Total Devices Tested:        100 (STR-relevant IoT devices)
Validation Rate:             91.0%
Exact Match Rate:            88.0% (vendor + product)
Vendor Match Rate:           89.0%
Product Match Rate:          94.0%
Version Match Rate:          97.0%

Devices with CVEs:           86 / 91 validated (94.5%)
Total CVEs Found:            271
Average CVEs per Device:     3.0
```

**Device Categories Tested:**

- Security Cameras & NVRs (Hikvision, Amcrest, Dahua, Wyze, Ring, Lorex)
- Network Equipment (Cisco, Ubiquiti, Netgear, TP-Link, ASUS, Aruba)
- Smart Home Devices (Google, Amazon, August smart locks)
- Media/Streaming (Roku, Sony, Vizio, LG)
- Printers (Canon, Brother, Samsung)
- Smart Lighting (Lutron, Philips)

**Failed Validations (9 devices):**
Devices that did not validate typically had:

- Extremely specific or niche product variants not in NVD
- Non-standard vendor name formats
- Products discontinued before NVD CPE standardization

---

## Work Log

### Week of February 2 - February 8, 2026

**Wednesday, 2/11/26**

* **Validation Testing Infrastructure:**
  - Created automated testing framework in `/test` directory
  - `test/generate_test_devices.py` - Generates STR-relevant IoT test devices
  - `test/evaluate_cpe_matching.py` - Runs validation with CVE queries
  - **Tested 100 STR-relevant IoT devices from NVD database**
  - **Results: 91% validation accuracy, 86 devices with CVEs (271 total vulnerabilities)**
  - Test focuses on cameras, routers, smart home devices detectable via HTTP/SSH/mDNS
  - CVE counts verified against NVD API for each validated device
  - Comprehensive metrics: validation rate, exact match rate, vendor/product accuracy, CVE coverage

**Tuesday, 2/10/26**

- **CPE Fuzzy Matching Algorithm Complete:**
  - Returns single best match per device (highest score above 65% threshold)
    - Fallback logic: exact vendor match → fuzzy vendor
- **Local CPE Database Implementation:**
  - Downloaded complete NVD CPE database (1,575,700 entries, 456MB)
  - Search performance: <1 second to query 1.5M CPEs vs 4+ minutes API pagination

**Saturday, 2/7/26**

- **Drafted Progress Report Update #2**
- **Code Documentation:**
  - Added AI attribution disclaimers to all Python files (main.py, mdns_handler.py, http_handler.py, ssh_handler.py)
  - Statement: "Some code snippets developed with assistance from generative AI tools. All AI-generated content was reviewed, revised, and adapted to meet STR Sentinel requirements."
- **Repository Maintenance:**
  - Updated .gitignore to exclude course progress report files
  - Consolidated and committed SSH handler and CPE generation work

**Tuesday, 2/4/26**

- **Enhanced CPE Generation:**
  - Fixed model extraction from HTTP titles (DS-2CD2042WD-I from Hikvision web interface)
  - Version formatting for CPE spec: `7.6p1` → `7.6:p1` (patch level requires colon)
  - Smart CPE type detection:
    - SSH-detected services → Application (`a`)
    - Generic software (nginx, Apache) → Application (`a`)
    - Device-specific models → Hardware (`h`)
- **Simulation Updates:**
  - Changed device from Yale lock to generic OpenSSH router/gateway

**Monday, 2/2/26**

- Built `ssh_handler.py` using Recog's 152 SSH banner patterns
- Socket-based banner extraction (port 22)
- Protocol prefix stripping: `SSH-2.0-OpenSSH_7.6p1` → `OpenSSH_7.6p1` for Recog matching
- Returns vendor (OpenBSD), model (OpenSSH), version (7.6p1) from single banner string
- Integrated into main.py

### Week of January 26 - February 1, 2026

**Saturday, 1/31/26**

- **Recog Integration Complete:** Ruby Recog gem via subprocess
  - Updated Dockerfile to include Ruby + Recog gem installation
  - Uses official Recog XML databases from gem installation (680+ patterns)

- Smart header parsing: prioritizes specific device fingerprints over generic web servers
- HTTP/HTTPS services now detected via authentic protocol headers, not simulation-specific workarounds

**Friday, 1/30/26**
- **mDNS Service Fix:** Resolved XML declaration issue in `nest.service` - Avahi was failing due to comments before XML declaration
- Moved `<?xml version="1.0"?>` to line 1 per XML specification
- Avahi daemon now successfully loads Nest thermostat mDNS advertisement
- `mdns_handler.py` accurately detects device model (Nest Learning Thermostat) and version (3.0)
- CPE string generation working: `cpe:2.3:h:google:nest_learning_thermostat:3.0:*:*:*:*:*:*`

**Thursday, 1/29/26**
- Implemented `mdns_handler.py` for device fingerprinting via mDNS protocol
- Added Zeroconf library integration for service browser functionality
- Property extraction for TXT records (md=model, ve=version, id=device ID)
- Enhanced code to support multiple property key variations across manufacturers
- 5-second active listener captures broadcast advertisements
- Initial testing revealed model detection issues (XML formatting - resolved 1/30)

**Monday, 1/26/26**
- Active fingerprinting research phase initiated
- Deployed Avahi-based mDNS responders in simulation environment
- Configured standard TXT record keys (md, ve) matching Google Nest hardware specifications
- Enables testing of discovery engine against industry-standard broadcast signatures

### Week of January 19 - 25, 2026

**Saturday, 01/24/26**
- Refactored and cleaned `main.py` codebase
- Completed Progress Report 01 for course submission
- Initial GitHub repository commit

**Friday 01/23/26**
- Completed network discovery scan implementation
- Nmap ARP-based host discovery (`-sn` flag) operational on local subnet
- Implemented logging system - creates `discovery.log` in `/app`
- Successfully detecting live hosts and MAC addresses

**Thursday, 01/22/26**
- Built Docker-based IoT testing environment
- Deployed three simulated devices: Hikvision camera, Nest thermostat, Yale smart lock
- Configured isolated Docker network (172.20.0.0/24)
- Assigned vendor-specific MAC addresses using legitimate OUIs

