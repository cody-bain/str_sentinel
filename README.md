# STR Sentinel

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
| Hikvision Camera | 172.20.0.10 | HTTP (8081) | 00:40:8C (Hikvision) |
| Yale Smart Lock | 172.20.0.20 | SSH (2222) | 00:17:7A (Yale) |
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
│   │   └── http_handler.py        # HTTP fingerprinting via Recog
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
- SSH banner grabbing (in progress)

### Phase 3: Vulnerability Analysis - IN PROGRESS
- CPE string generation implemented
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
│  └─> SSH: Banner grabbing (planned)                     │
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

Example: `Server: nginx, Hikvision-Webs` → Correctly identifies as **Hikvision DVR** (not nginx)

---

## Work Log

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
**Problem:** Generic nmap service detection only identified "nginx 1.29.4" - missing the actual Hikvision camera identity.

**Solution:** Integrated Rapid7's Recog framework with 680+ professional fingerprint patterns. Rather than building a custom XML parser (267 lines), used Ruby subprocess calls to native `recog_match` command (~30 lines). Smart header parsing prioritizes device-specific patterns over generic web servers.

### Challenge 2: Multi-Value HTTP Headers
**Problem:** Simulation sent `Server: nginx, Hikvision-Webs` but Recog matched only the first value (nginx), missing the IoT device.

**Solution:** Implemented comma-separated header parsing with priority logic:
1. Try full header string first
2. If match is generic (nginx, Apache), parse each comma-separated value
3. Return first non-generic match (Hikvision Web Server)

### Challenge 3: mDNS Service Loading Failure
**Problem:** Avahi daemon failed to load nest.service with error "XML_ParseBuffer() failed at line 5"

**Solution:** XML declaration must be on line 1 per specification. Moved `<?xml version="1.0"?>` before all comments. Avahi now successfully broadcasts Nest thermostat via Google Cast protocol.

### Challenge 4: Simulation vs Real-World Behavior
**Problem:** Initial simulation used custom `X-Hikvision-Model` header that real devices don't send. This created detection that only worked in curated environments.

**Solution:** Research into actual Hikvision device behavior revealed they send `Server: Hikvision-Webs` (already in Recog database). Updated simulation to use authentic headers, enabling detection via industry-standard patterns rather than custom workarounds.

### Challenge 5: Python vs Ruby Ecosystem
**Problem:** Recog is Ruby-native with 680+ XML patterns. Choices were: (a) write Python XML parser from scratch, (b) find unmaintained Python port, or (c) integrate Ruby.

**Solution:** Installed Ruby + recog gem in Docker container and called via subprocess. More maintainable than custom parser, uses official patterns, stays up-to-date with Recog releases.

---

## Planned Development

### Immediate Priorities
- SSH banner grabbing handler - Extract device information from SSH handshakes (Yale lock identification)
- Enhanced CPE matching - Integrate MAC OUI lookups for better vendor identification

### Phase 3: Vulnerability Analysis
- NVD API integration using nvdlib (already in requirements.txt)
- CPE-to-CVE matching engine
- CVSS-based risk scoring algorithm
- Vulnerability report generation

### Phase 4: Reporting & Dashboard
- Web-based dashboard for scan results visualization
- PDF report generation with executive summary
- Network topology visualization
- Remediation recommendations engine

### Research & Enhancement
- Generic protocol defense scripts (brand-agnostic MQTT/CoAP testing)
- Expand SSH fingerprint coverage for more lock manufacturers
- Investigate UPnP/SSDP discovery for additional device types

---

## Technical Notes

**Multi-Protocol Strategy:** Not all IoT devices use mDNS. Discovery employs a layered approach where nmap finds all hosts (passive ARP scanning) and protocol handlers enrich with identity data for devices that advertise via HTTP, mDNS, or SSH.

**Recog Integration Benefits:**
- **Professional Patterns:** Maintained by Rapid7's security research team
- **Coverage:** 680+ fingerprints across web servers, IoT devices, embedded systems
- **Updates:** Gem updates bring new patterns automatically
- **Authenticity:** Uses same tool employed by Metasploit and nexpose scanners

**Simulation Realism:** Environment uses vendor-specific MAC OUIs (00:40:8C for Hikvision, 18:B4:30 for Nest Labs, 00:17:7A for Yale) and authentic protocol behaviors to ensure detection methods work on real hardware, not just in test environments.