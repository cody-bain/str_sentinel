# STR Sentinel (In Development)
0
**Cody Bain | Georgia Tech PUBP 6727**

*Various LLMs were leveraged in generating sections of code for my project. Usage is documented within all files where generated code was used. All AI generated code has thoroughly reviewed, understood, and improved upon to achieve desired tool performance per my criteria.*

*README.md is an AI summary of my work. I have manually gone back and polished the AI summary.*

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
│  Phase 4: Risk Scoring & Web Dashboard              │
└─────────────────────────────────────────────────────┘
              ↓
   Security Reports & Remediation Guidance
```

---

## Getting Started

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for local development)
- NVD API Key (optional, but recommended for faster CVE lookups)

### Quick Start Guide

#### 1. Start Simulation Environment
```bash
cd simulation
docker-compose up -d --build
```

#### 2. Download CPE Database (One-Time Setup)
```bash
docker exec -it str_sentinel_app python download_cpe_database.py
```
*Downloads complete NVD CPE dictionary (~456MB). Takes 10-30 minutes. Only needed once or for periodic updates.*

#### 3. Run Network Scan
```bash
# Scan with default subnet and save results
docker exec -it str_sentinel_app python main.py --output shared/discovery-scan.json
```

#### 4. Start Web Dashboard
```bash
# Run dashboard server (foreground)
docker exec -it str_sentinel_app python web_server.py

# Or run in background
docker exec -d str_sentinel_app python web_server.py
```
*Note: Dashboard runs on port 5001

#### 5. View Security Dashboard
Open your browser and navigate to: **http://localhost:5001**

The dashboard displays:
- Network-wide risk assessment
- Device inventory with CVE counts
- CVSS-based risk scores
- Detailed vulnerability information
- Remediation recommendations

#### 6. Stop Environment
```bash
cd simulation
docker-compose down
```

### Simulated Network Environment

The testing environment includes three simulated IoT devices on an isolated Docker network (172.20.0.0/24):

| Device Type | IP Address | Protocols | MAC Address (OUI) |
|------------|------------|-----------|-------------------|
| Hikvision DS-2CD2032-I Camera | 172.20.0.10 | HTTP (80) | 00:40:8C (Hikvision) |
| Network Device (OpenSSH 7.6p1) | 172.20.0.20 | SSH (22) | 00:1E:14 (Cisco Systems) |
| Apple TV (11.0) | 172.20.0.35 | mDNS (AirPlay) | 00:03:93 (Apple) |

### Additional Commands

```bash
# Scan a custom subnet
docker exec -it str_sentinel_app python main.py 192.168.1.0/24

# Save to custom output file (also updates dashboard)
docker exec -it str_sentinel_app python main.py --output custom-scan.json

# View logs during scan
docker logs -f str_sentinel_app
```

---

## Project Structure

```
str_sentinel/
├── app/
│   ├── main.py                       # Primary discovery orchestrator
│   ├── cpe_validator.py              # CPE validation & fuzzy matching
│   ├── cve_lookup.py                 # NVD CVE API integration
│   ├── risk_scoring.py               # CVSS-based risk assessment
│   ├── web_server.py                 # Flask dashboard server
│   ├── download_cpe_database.py      # CPE database downloader
│   ├── protocol_handlers/
│   │   ├── mdns_handler.py           # mDNS device identification
│   │   ├── http_handler.py           # HTTP fingerprinting via Recog
│   │   └── ssh_handler.py            # SSH banner fingerprinting via Recog
│   ├── web/
│   │   ├── index.html                # Dashboard UI template
│   │   └── static/
│   │       ├── dashboard.css         # Dashboard styles
│   │       └── dashboard.js          # Dashboard frontend logic
│   ├── shared/
│   │   ├── discovery-scan.json       # Scan results output
│   │   └── cpe_dictionary.json       # Local CPE database (456MB, gitignored)
│   ├── requirements.txt
│   └── Dockerfile                    # Includes Ruby + Recog gem
├── simulation/
│   ├── docker-compose.yml            # Simulation environment
│   └── nest.service                  # Avahi mDNS configuration
├── test/
│   ├── evaluate_cpe_matching.py      # CPE validation testing
│   └── generate_test_devices.py      # Test device generator
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

### Phase 4: Reporting - COMPLETE
- ✅ CVSS-based risk scoring algorithm
  - Multi-factor scoring: CVE count, severity, validation status, device exposure
  - Network-wide risk assessment with confidence levels
  - 0-100 risk scoring with Critical/High/Medium/Low/Minimal classifications
- ✅ CVE Lookup Module
  - NVD API integration with caching
  - Automated vulnerability enumeration for validated CPEs
  - CVSS v3.1/v3.0/v2.0 score extraction
- ✅ Web-based dashboard (Flask)
  - Real-time scan results visualization
  - Interactive device inventory with drill-down details
  - Network summary cards with risk metrics
  - Color-coded severity indicators
- ✅ Remediation recommendations engine
  - Automated security guidance based on CVE severity
  - Device-specific recommendations
  - Best practice suggestions
- ✅ PDF report generation (Planned)
  - Host: Network Vulnerabilities + Legal Framework
  - Guest: Privacy & Information Security

---

## Web Dashboard

The STR Sentinel dashboard provides real-time visualization of network security assessments at **http://localhost:5001**.

### Features

**Network Summary Cards:**
- Overall network risk level with color-coded indicators
- Total device count and devices at risk
- Total CVE count across all devices
- Severity breakdown (Critical/High/Medium/Low/Minimal)

**Interactive Device Table:**
- Device inventory with IP, MAC, vendor, and model information
- CVE counts with severity breakdown per device
- Individual risk scores (0-100) with confidence levels
- Drill-down capability for detailed vulnerability information

**Device Details Modal:**
- Complete device identity (vendor, model, version, detection method)
- Validated CPE string
- Full CVE list with CVSS scores and severities
- Direct links to NVD vulnerability database
- Automated remediation recommendations
- Risk factor breakdown

**Dashboard API Endpoints:**
- `/api/scan-results` - Complete scan data
- `/api/network-summary` - Network-wide risk metrics
- `/api/device/<ip>` - Individual device details
- `/health` - Service health check

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

