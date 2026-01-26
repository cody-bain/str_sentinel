# STR Sentinel

**Cody Bain, Georgia Tech PUBP 6727**

## Running STR Sentinel

Start all services (IoT Devices & Sentinel App) using Docker Compose to build the image via the Dockerfile inside /app:

```bash
docker-compose -f simulation/docker-compose.yml up -d --build
```

Re-build the Sentinel App without rebuilding IoT devices:

```bash
docker exec -it str_sentinel_app bash
```



- Simulated Network:
  - Hikvision Camera (mocked web service)
  - Smart Thermostat (Mocked MQTT service)
  - Linux Server (Representing a host media server or PC)

*Note: STR Sentinel is still in development. All network devices are simulated inside of Docker.*

## Work Log

**Monday, 1/26/26**

- Begin Active Fingerprinting Research
- Implemented mDNS responders that utilize standard **TXT Record keys (md, ve)** utilized by Google Nest hardware. Allows the Sentinel's Discover engine to be tested against standard broadcast signatures.

**Saturday, 01/24/26**
- Cleanup *main.py*
- Finalize Progress Report 01
- Initial GitHub Commit

**Friday 01/23/26**

- Completed Discovery Scan on local subnet. Complete via *main.py* code. 

  - ping scan (i.e. host discovery scan '-sn')
  - nmap sends ARP request (on local network) → device receives and responds

- Added logging to Discovery Scan script.

  - Creates discovery.log file inside /app.

**Thursday, 01/22/26**

- Built barebones IoT testing environment inside Docker.
  - HikVision Camera, Smart Thermostat, Linux Server (mock media server / PC)




## Future Work

- Build CPE Matching Engine:
  - Match hardware devices against NIST NVD to find technical security vulnerabilities.
  - Match software on devices against NIST NVD to find technical security vulnerabilities.
- Build Generic Protocol Defense Script
  - Test IoT protocols & services. Brand independent.
  - example: Any device that uses MQTT Services gets assessed against the MQTT Script.
- Prove concept that STR Sentinel is capable of handling any vulnerable device. You do not have an extensive database of 10,000 devices (yet), so prove the concept against a few with robust architecture.
  - Protocol based (Insecure MQTT)
  - Signature based (Hikvision Web Title)
  - Credential based (Default SSH for Yale Lock)
- ARP Spoofing
  - ICMP Blocking is N/A. We are operating on the *local STR network*
  - A sophisticated attacker could utilize ARP Spoffing to link attackers MAC address with the IP of a legitimate device.