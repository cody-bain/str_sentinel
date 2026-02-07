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
| Hikvision Camera | 172.20.0.10 | HTTP (80) | 00:40:8C (Hikvision) |
| Network Device (OpenSSH) | 172.20.0.20 | SSH (22) | 00:1E:14 (Cisco Systems) |
| Nest Thermostat | 172.20.0.35 | mDNS (Google Cast) | 18:B4:30 (Nest Labs) |

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

### Phase 3: Vulnerability Analysis - IN PROGRESS
- NVD-compatible CPE generation (In Progress)
  - Model extraction from HTTP titles (DS-2CD2042WD-I from Hikvision)
  - Version formatting for CPE 
  - Smart application vs hardware detection
- CPE-Fuzzing (planned)
  - To more consistently ensure a match

- NVD API integration (planned)
- CVE matching (planned)

### Phase 4: Reporting - PLANNED
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

## Work Log

### Week of February 2 - February 8, 2026

**Tuesday, 2/3/26**

- **Enhanced CPE Generation Enhanced:**
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

---

## Technical Challenges & Solutions

### Challenge 1: HTTP Fingerprinting Accuracy
**Problem:** Generic nmap service detection only identified "nginx 1.29.4" while missing the actual Hikvision camera identity.

**Solution:** Integrated Rapid7's Recog framework with 680+ professional fingerprint patterns. Used Ruby subprocess calls to native `recog_match` command. Smart header parsing prioritizes device-specific patterns over generic web servers.

### Challenge 2: Multi-Value HTTP Headers
**Problem:** Simulation sent `Server: nginx, Hikvision-Webs` but Recog matched only the first value (nginx), missing the IoT device.

**Solution:** Implemented comma-separated header parsing with priority logic:
1. Try full header string first
2. If match is generic (nginx, Apache), parse each comma-separated value
3. Return first non-generic match (ex. Hikvision Web Server)

### Challenge 3: CPE Type Classification
**Problem:** Initial logic hardcoded `['OpenSSH', 'SSH']` to determine application vs hardware, failing for other SSH servers or generic web servers detected via HTTP.

**Solution:** Refactored to use detection_method field and software indicators list. SSH detection → always application. Generic software (nginx, Apache) → application even via HTTP. Device-specific models → hardware. Scales to any future protocol.

### Challenge 4: NVD-Compatible CPE Strings
**Problem:** Generated CPEs like `cpe:2.3:h:hikvision:hikvision_web_server:*` contained no model/version info, preventing NVD CVE lookups.

**Solution:** Enhanced CPE generator to:
- Extract actual model numbers from HTTP titles via regex (`DS-2CD2042WD-I`)
- Include detected versions (not wildcards) when available
- Format patch levels per CPE spec (`7.6p1` → `7.6:p1`)
Result: Real CPEs like `cpe:2.3:a:openbsd:openssh:7.6:p1:*:*:*:*:*:*:*` ready for NVD queries.

### Challenge 5: Simulation vs Real-World Behavior
**Problem:** Initial simulation used custom `X-Hikvision-Model` header that real devices don't send. This created detection that only worked in curated environments.

**Solution:** Research into actual Hikvision device behavior revealed they send `Server: Hikvision-Webs` (already in Recog database). Updated simulation to use authentic headers, enabling detection via industry-standard patterns rather than custom workarounds.

---

## Planned Development

### Immediate Priorities
- Enhance CPE matching. Potentially use fuzzing to improve match rate with NIST NVD API.

### Phase 3: Vulnerability Analysis
- NVD API integration using nvdlib
- CPE-to-CVE matching engine
- CVSS-based risk scoring algorithm
- Vulnerability report generation

### Phase 4: Reporting & Dashboard
- Web-based dashboard for scan results visualization
- PDF report generation with executive summary for both guests and hosts
- Network topology visualization
- Remediation recommendations engine

### Research & Enhancement
- Expand SSH & HTTP model patterns for more IoT device fingerprinting capability

---

## Other Technical Notes

**Multi-Protocol Strategy:** Not all IoT devices use mDNS. Discovery employs a layered approach where nmap finds all hosts (passive ARP scanning) and protocol handlers enrich with identity data for devices that advertise via HTTP, mDNS, or SSH.

**Simulation Realism:** Environment uses vendor-specific MAC OUIs (00:40:8C for Hikvision, 18:B4:30 for Nest Labs, 00:1E:14 for Cisco) and authentic protocol behaviors to ensure detection methods work on real hardware, not just in test environments.