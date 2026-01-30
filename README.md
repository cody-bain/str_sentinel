# STR Sentinel

**Cody Bain | Georgia Tech PUBP 6727**

> An automated IoT security scanner for short-term rental (STR) properties that discovers network devices, identifies vulnerabilities, and generates actionable security reports for hosts and guests.

## 🎯 Project Overview

STR Sentinel performs automated security assessments of IoT devices in rental properties by:
1. **Discovery** - Identifies all devices on the local network using nmap
2. **Fingerprinting** - Identifies device models and versions via mDNS, HTTP, SSH
3. **Vulnerability Analysis** - Matches devices against NIST NVD for known CVEs
4. **Reporting** - Generates security assessment reports with remediation guidance

## 🏗️ Architecture

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

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for local development)

### Running the Simulation

Start all services (IoT device simulations + Sentinel scanner):

```bash
docker-compose -f simulation/docker-compose.yml up -d --build
```

### Simulated Network Environment

The testing environment includes three simulated IoT devices:

| Device Type | IP Address | Protocols | MAC Address (OUI) |
|------------|------------|-----------|-------------------|
| Hikvision Camera | 172.20.0.10 | HTTP (8081) | 00:40:8C (Hikvision) |
| Yale Smart Lock | 172.20.0.20 | SSH (2222) | 00:17:7A (Yale) |
| Nest Thermostat | 172.20.0.35 | mDNS (Google Cast) | 18:B4:30 (Nest Labs) |

### Running a Discovery Scan

Access the Sentinel container and run a scan:

```bash
# Run with default subnet (172.20.0.0/24)
docker exec -it str_sentinel_app python main.py

# Or specify a custom subnet
docker exec -it str_sentinel_app python main.py --subnet 192.168.1.0/24

# With optional output file
docker exec -it str_sentinel_app python main.py --output custom-scan.json
```

Results are saved to `app/shared/discovery-scan.json`

## 📂 Project Structure

```
str_sentinel/
├── app/
│   ├── main.py                    # Primary discovery orchestrator
│   ├── protocol_handlers/
│   │   └── mdns_handler.py        # mDNS device identification
│   ├── shared/
│   │   └── discovery-scan.json    # Scan results output
│   └── requirements.txt
├── simulation/
│   ├── docker-compose.yml         # Simulation environment
│   └── nest.service               # Avahi mDNS configuration
└── README.md
```

## 🔧 Development Setup

### Local Development (Without Docker)

1. Create and activate a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate  # On macOS/Linux
```

2. Install dependencies:
```bash
pip install -r app/requirements.txt
```

3. Configure Python interpreter in VS Code:
   - `Cmd+Shift+P` → "Python: Select Interpreter"
   - Select `.venv/bin/python`

## 📊 Current Status

**Phase 1 (Discovery):** ✅ Complete
- Nmap host discovery operational
- MAC address and IP detection working

**Phase 2 (Fingerprinting):** 🚧 In Progress
- ✅ mDNS handler complete (Google Cast/Nest detection)
- ⏳ HTTP handler (planned)
- ⏳ SSH banner grabbing (planned)

**Phase 3 (Vulnerability Analysis):** ⏳ Planned
- CPE string generation
- NVD API integration
- CVE matching

**Phase 4 (Reporting):** ⏳ Planned
- Web dashboard
- PDF report generation

---

---

## 🛠️ Work Log

### Week of January 26 - February 1, 2026

**Friday, 1/30/26**
- Fixed XML declaration issue in `nest.service` - mDNS service was failing to load due to comments before XML declaration
- Avahi daemon now successfully loads Nest thermostat mDNS advertisement
- `mdns_handler.py` now accurately detects device model and version
- CPE string generation improved: `cpe:2.3:h:google:nest_learning_thermostat:3.0:*:*:*:*:*:*`

**Thursday, 1/29/26**
- Implemented `mdns_handler.py` for device fingerprinting via mDNS protocol
- Added property extraction for TXT records (md, ve, id fields)
- Enhanced code to support multiple property key variations across manufacturers
- Initial testing revealed model detection issues (resolved 1/30)

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

## 🎯 Future Work

### Immediate Priorities
- [ ] **HTTP Fingerprinting Handler** - Identify devices via web interfaces, headers, banners
- [ ] **SSH Banner Grabbing** - Extract device information from SSH handshakes
- [ ] **Enhanced CPE Matching** - Integrate MAC OUI lookups for better vendor identification

### Phase 3: Vulnerability Analysis
- [ ] Build CPE matching engine using NIST NVD API
- [ ] Implement CVE lookup for hardware devices
- [ ] Implement CVE lookup for software/firmware versions
- [ ] Risk scoring algorithm based on CVSS scores

### Phase 4: Reporting & Dashboard
- [ ] Web-based dashboard for scan results visualization
- [ ] PDF report generation with executive summary
- [ ] Network topology visualization
- [ ] Remediation recommendations engine

### Research & Enhancement
- [ ] Generic protocol defense scripts (brand-agnostic testing)
  - Example: MQTT security assessment applicable to any MQTT-enabled device
- [ ] Expand device signature database
- [ ] ARP spoofing detection/mitigation research
  - Relevant for local network operation where ICMP blocking is ineffective

---

## 📚 Technical Notes

**mDNS Protocol Coverage:** Not all IoT devices use mDNS. Discovery strategy employs a two-phase approach:
1. **Nmap** finds all devices (passive/active scanning)
2. **Protocol handlers** add identity data for devices that advertise

**Security Considerations:** 
- Simulation operates on isolated Docker network
- Potential attack vectors being considered: ARP spoofing on local STR networks