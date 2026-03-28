// CODE GENERATED WITH ASSISTANCE FROM VARIOUS AI TOOLS.
// ALL AI-GENERATED CONTENT WAS REVIEWED, REVISED, AND ADAPTED TO MEET STR SENTINEL REQUIREMENTS.


let scanData = null;
let currentTab = 'admin';

// CSF 2.0 Compliance Checklist Data
const complianceData = [
    { function: "GOVERN (GV)", category: "Organizational Context (GV.OC)", nistDescription: "The organizational mission is understood and informs cybersecurity risk management", task: "Sign STR Sentinel's \"Host Mission Statement\" Document", sentinel: true },
    { function: "GOVERN (GV)", category: "Organizational Context (GV.OC)", nistDescription: "Internal and external stakeholders are understood, and their needs and expectations regarding cybersecurity risk management are understood and considered", task: "Audit HOA bylaws and regulation for any surveillance regulation.", sentinel: false },
    { function: "GOVERN (GV)", category: "Organizational Context (GV.OC)", nistDescription: "Legal, regulatory, and contractual requirements regarding cybersecurity - including privacy and civil liberties obligations - are understood and managed", task: "Document mandatory camera disclosures IAW Airbnb, VRBO, etc. regulation.", sentinel: false },
    { function: "GOVERN (GV)", category: "Organizational Context (GV.OC)", nistDescription: "Critical objectives, capabilities, and services that external stakeholders depend on or expect from the organization are understood and communicated", task: "Disclose active IT/IoT to guests in rental listing.", sentinel: false },
    { function: "GOVERN (GV)", category: "Organizational Context (GV.OC)", nistDescription: "Outcomes, capabilities, and services that the organization depends on are understood and communicated", task: "Develop plan to repair, replace, or accept risk and downtime if IT/IoT in STR fails.", sentinel: false },
    { function: "GOVERN (GV)", category: "Risk Management Strategy (GV.RM)", nistDescription: "Risk management objectives are established and agreed to by organizational stakeholders", task: "Define \"essential\" and \"non-essential\" IT/IoT required to operate rental business.", sentinel: false },
    { function: "GOVERN (GV)", category: "Risk Management Strategy (GV.RM)", nistDescription: "Risk appetite and risk tolerance statements are established, communicated, and maintained", task: "Define risk tolerance threshold, such as number of open critical/high vulnerabilities, for IT/IoT devices.", sentinel: false },
    { function: "GOVERN (GV)", category: "Risk Management Strategy (GV.RM)", nistDescription: "Strategic direction that describes appropriate risk response options is established and communicated", task: "Define procedure to remove and isolate critically vulnerable devices from the network.", sentinel: false },
    { function: "GOVERN (GV)", category: "Risk Management Strategy (GV.RM)", nistDescription: "Lines of communication across the organization are established for cybersecurity risks, including risks from suppliers and other third parties", task: "Maintain communication lines (text, private messaging, etc) for guests to report security concerns.", sentinel: false },
    { function: "GOVERN (GV)", category: "Risk Management Strategy (GV.RM)", nistDescription: "A standardized method for calculating, documenting, categorizing, and prioritizing cybersecurity risks is established and communicated", task: "Covered via STR Sentinel Dashboard.", sentinel: true },
    { function: "GOVERN (GV)", category: "Roles, Responsibilities, and Authorities (GV.RR)", nistDescription: "Organizational leadership is responsible and accountable for cybersecurity risk and fosters a culture that is risk-aware, ethical, and continually improving", task: "Periodically review STR Sentinel Dashboard, open risks, and associated risk score.", sentinel: true },
    { function: "GOVERN (GV)", category: "Roles, Responsibilities, and Authorities (GV.RR)", nistDescription: "Roles, responsibilities, and authorities related to cybersecurity risk management are established, communicated, understood, and enforced", task: "Set guest permissions in any shared IT/IoT services (ex. Streaming Accounts on Smart TV). Keep separate admin accounts & permissions.", sentinel: false },
    { function: "GOVERN (GV)", category: "Roles, Responsibilities, and Authorities (GV.RR)", nistDescription: "Adequate resources are allocated commensurate with the cybersecurity risk strategy, roles, responsibilities, and policies", task: "Define budget line item for IT/IoT update expenses.", sentinel: false },
    { function: "GOVERN (GV)", category: "Policy (GV.PO)", nistDescription: "Policy for managing cybersecurity risks is established based on organizational context, cybersecurity strategy, and priorities and is communicated and enforced", task: "Include a \"Tech\" section inside the guest \"House Rules\" document.", sentinel: false },
    { function: "GOVERN (GV)", category: "Policy (GV.PO)", nistDescription: "Policy for managing cybersecurity risks is reviewed, updated, communicated, and enforced to reflect changes in requirements, threats, technology, and organizational mission", task: "When new technology is installed, review default security rules and settings.", sentinel: false },
    { function: "GOVERN (GV)", category: "Oversight (GV.OV)", nistDescription: "Organizational cybersecurity risk management performance is evaluated and reviewed for adjustments needed", task: "Audit quarterly any smart lock access logs & network activity logs to ensure only verified guests have had physical and network access to the property.", sentinel: false },
    { function: "GOVERN (GV)", category: "Cybersecurity Supply Chain Risk Management (GV.SC)", nistDescription: "The risks posed by a supplier, their products and services, and other third parties are understood, recorded, prioritized, assessed, responded to, and monitored over the course of the relationship", task: "Before procurement, review device security risk in NIST database. After procurement, review open vulnerabilities in STR Sentinel dashboard.", sentinel: true },
    { function: "GOVERN (GV)", category: "Cybersecurity Supply Chain Risk Management (GV.SC)", nistDescription: "Cybersecurity supply chain risk management plans include provisions for activities that occur after the conclusion of a partnership or service agreement", task: "Develop hardware disposition plans. This should include factory resetting all technology before sale or destruction.", sentinel: false },
    { function: "IDENTIFY (ID)", category: "Asset Management (ID.AM)", nistDescription: "Inventories of hardware managed by the organization are maintained", task: "ID all hardware on network. This task is managed automatically by the STR Sentinel Engine.", sentinel: true },
    { function: "IDENTIFY (ID)", category: "Asset Management (ID.AM)", nistDescription: "Inventories of software, services, and systems managed by the organization are maintained", task: "ID all software on network. This task is a future automatic feature of the STR Sentinel Engine.", sentinel: true },
    { function: "IDENTIFY (ID)", category: "Asset Management (ID.AM)", nistDescription: "Representations of the organization's authorized network communication and internal and external network data flows are maintained", task: "Create a network diagram to understand how data flows within the STR rental. This is a future feature of the STR Sentinel Engine.", sentinel: true },
    { function: "IDENTIFY (ID)", category: "Asset Management (ID.AM)", nistDescription: "Inventories of services provided by suppliers are maintained", task: "Track all services paid for (Internet Service Provider, Cloud Storage, etc).", sentinel: false },
    { function: "IDENTIFY (ID)", category: "Asset Management (ID.AM)", nistDescription: "Assets are prioritized based on classification, criticality, resources, and impact on the mission", task: "STR Sentinel currently classifies devices on NIST risk. Future iterations shall classify on NIST NVD vulnerabilities AND device type (i.e. an IP camera vs a smart light).", sentinel: true },
    { function: "IDENTIFY (ID)", category: "Asset Management (ID.AM)", nistDescription: "Inventories of data and corresponding metadata for designated data types are maintained", task: "Understand where any guest data (video, audio, data) is stored. Cloud or local.", sentinel: false },
    { function: "IDENTIFY (ID)", category: "Asset Management (ID.AM)", nistDescription: "Systems, hardware, software, services, and data are managed throughout their life cycles", task: "Log \"date of commission\" to track aging technology and update when outdated.", sentinel: false },
    { function: "IDENTIFY (ID)", category: "Risk Assessment (ID.RA)", nistDescription: "Vulnerabilities in assets are identified, validated, and recorded", task: "Run vulnerability scan on network and track outdated firmware or open ports. Covered via STR Sentinel Dashboard.", sentinel: true },
    { function: "IDENTIFY (ID)", category: "Risk Assessment (ID.RA)", nistDescription: "Cyber threat intelligence is received from information sharing forums and sources", task: "Subscribe to IoT security alerts and newsletters.", sentinel: false },
    { function: "IDENTIFY (ID)", category: "Risk Assessment (ID.RA)", nistDescription: "Internal and external threats to the organization are identified and recorded", task: "Create a network diagram to understand how data flows within the STR rental. This is a future feature of the STR Sentinel Engine.", sentinel: true },
    { function: "IDENTIFY (ID)", category: "Risk Assessment (ID.RA)", nistDescription: "Processes for receiving, analyzing, and responding to vulnerability disclosures are established", task: "Establish process to receive and respond to guest security & privacy concerns.", sentinel: false },
    { function: "IDENTIFY (ID)", category: "Improvement (ID.IM)", nistDescription: "Improvements are identified from evaluations", task: "Update procedures for incident response following any incident / privacy breach.", sentinel: false },
    { function: "PROTECT (PR)", category: "Identity Management, Authentication, and Access Control (PR.AA)", nistDescription: "Identities and credentials for authorized users, services, and hardware are managed by the organization", task: "Audit host & admin accounts to ensure non-default passwords set. Utilize MFA if possible.", sentinel: false },
    { function: "PROTECT (PR)", category: "Identity Management, Authentication, and Access Control (PR.AA)", nistDescription: "Identities are proofed and bound to credentials based on the context of interactions", task: "Reset smart lock passwords to a unique code for each guest's stay.", sentinel: false },
    { function: "PROTECT (PR)", category: "Identity Management, Authentication, and Access Control (PR.AA)", nistDescription: "Physical access to assets is managed, monitored, and enforced commensurate with risk", task: "Install routers, servers, and any admin devices inside a locked cabinet.", sentinel: false },
    { function: "PROTECT (PR)", category: "Awareness and Training (PR.AT)", nistDescription: "Personnel are provided with awareness and training so that they possess the knowledge and skills to perform general tasks with cybersecurity risks in mind", task: "Create a user guide for guests on approved behaviors on the STR network.", sentinel: false },
    { function: "PROTECT (PR)", category: "Data Security (PR.DS)", nistDescription: "The confidentiality, integrity, and availability of data-at-rest are protected", task: "Ensure recording devices use encrypted local storage.", sentinel: false },
    { function: "PROTECT (PR)", category: "Data Security (PR.DS)", nistDescription: "The confidentiality, integrity, and availability of data-in-transit are protected", task: "Verify WPA3 or WPA2-AES encryption standards are active on network.", sentinel: false },
    { function: "PROTECT (PR)", category: "Data Security (PR.DS)", nistDescription: "Backups of data are created, protected, maintained, and tested", task: "Ensure recording devices and smart logs generate logs. Backup and export logs routinely.", sentinel: false },
    { function: "PROTECT (PR)", category: "Platform Security (PR.PS)", nistDescription: "Configuration management practices are established and applied", task: "Review configuration of IoT devices and verify the most secure settings and protocols are selected.", sentinel: false },
    { function: "PROTECT (PR)", category: "Platform Security (PR.PS)", nistDescription: "Software is maintained, replaced, and removed commensurate with risk", task: "Routinely verify hardware and software firmware / software is current and updated.", sentinel: false },
    { function: "PROTECT (PR)", category: "Platform Security (PR.PS)", nistDescription: "Log records are generated and made available for continuous monitoring", task: "Verify logs are created for login attempts to IT devices and smart locks.", sentinel: false },
    { function: "PROTECT (PR)", category: "Platform Security (PR.PS)", nistDescription: "Installation and execution of unauthorized software are prevented", task: "Enable guest accounts for IT and Smart TVs.", sentinel: false },
    { function: "PROTECT (PR)", category: "Technology Infrastructure Resilience (PR.IR)", nistDescription: "Networks and environments are protected from unauthorized logical access and usage", task: "Isolate guest and admin networks by creating separate VLANs.", sentinel: false },
    { function: "PROTECT (PR)", category: "Technology Infrastructure Resilience (PR.IR)", nistDescription: "The organization's technology assets are protected from environmental threats", task: "Install Universal Power Supply (UPS) devices on critical IoT/IT assets.", sentinel: false },
    { function: "PROTECT (PR)", category: "Technology Infrastructure Resilience (PR.IR)", nistDescription: "Mechanisms are implemented to achieve resilience requirements in normal and adverse situations", task: "Test smart lock and critical IoT/IT functionality in power outage scenario. Ensure necessary STR functionality remains active.", sentinel: false },
    { function: "DETECT (DE)", category: "Continuous Monitoring (DE.CM)", nistDescription: "Networks and network services are monitored to find potentially adverse events", task: "Monitor new devices joining the network via STR Sentinel dashboard. Monitor for suspicious and persistent devices.", sentinel: true },
    { function: "DETECT (DE)", category: "Continuous Monitoring (DE.CM)", nistDescription: "The physical environment is monitored to find potentially adverse events", task: "Install surveillance cameras on STR perimeter as permitted by STR platform code.", sentinel: false },
    { function: "DETECT (DE)", category: "Continuous Monitoring (DE.CM)", nistDescription: "Personnel activity and technology usage are monitored to find potentially adverse events", task: "FUTURE STR SENTINEL FEATURE: Detect high-bandwidth usage devices and suspicious IP access.", sentinel: true },
    { function: "DETECT (DE)", category: "Continuous Monitoring (DE.CM)", nistDescription: "External service provider activities and services are monitored to find potentially adverse events", task: "FUTURE STR SENTINEL FEATURE: Monitor ISP downtime.", sentinel: true },
    { function: "DETECT (DE)", category: "Continuous Monitoring (DE.CM)", nistDescription: "Computing hardware and software, runtime environments, and their data are monitored to find potentially adverse events", task: "Install endpoint security programs on any local servers or publicly accessible workstations for guests.", sentinel: false },
    { function: "DETECT (DE)", category: "Adverse Event Analysis (DE.AE)", nistDescription: "Potentially adverse events are analyzed to better understand associated activities", task: "Query an LLM on any logged suspicious activity. Include information consolidated and correlated from all sources to help determine source of potential malicious activity and potential effects.", sentinel: false },
    { function: "DETECT (DE)", category: "Adverse Event Analysis (DE.AE)", nistDescription: "Cyber threat intelligence and other contextual information are integrated into the analysis", task: "FUTURE STR SENTINEL FEATURE: Monitor IP traffic against known malicious/bad IPs.", sentinel: true },
    { function: "RESPOND (RS)", category: "Incident Management (RS.MA)", nistDescription: "The incident response plan is executed in coordination with relevant third parties once an incident is declared", task: "Create an \"Emergency Technology Support\" checklist for potential adverse events.", sentinel: false },
    { function: "RESPOND (RS)", category: "Incident Analysis (RS.AN)", nistDescription: "Analysis is performed to establish what has taken place during an incident and the root cause of the incident", task: "Review STR Sentinel logs and applicable IoT/IT logs whenever a guest reports a potential incident or privacy violation to determine potential cause.", sentinel: false },
    { function: "RESPOND (RS)", category: "Incident Mitigation (RS.MI)", nistDescription: "Incidents are contained", task: "Inside the \"Emergency Technology Support\" document, include procedure for wiping and resetting passwords for devices affected by a security incident or compromise.", sentinel: false },
    { function: "RECOVER (RC)", category: "Incident Recovery Plan Execution (RC.RP)", nistDescription: "The recovery portion of the incident response plan is executed once initiated from the incident response process", task: "Inside the \"Emergency Technology Support\" document, create a factory reset and clean install procedure guide for routers, switches, servers, and other technology that may be required to get STR guests back online.", sentinel: false },
    { function: "RECOVER (RC)", category: "Incident Recovery Plan Execution (RC.RP)", nistDescription: "The integrity of backups and other restoration assets is verified before using them for restoration", task: "Test backup recovery procedures documented inside the \"Emergency Technology Support\" document at least once per year.", sentinel: false },
    { function: "RECOVER (RC)", category: "Incident Recovery Plan Execution (RC.RP)", nistDescription: "The integrity of restored assets is verified, systems and services are restored, and normal operating status is confirmed", task: "Covered via RC.RP-03.", sentinel: false },
    { function: "RECOVER (RC)", category: "Incident Recovery Communication (RC.CO)", nistDescription: "Recovery activities and progress in restoring operational capabilities are communicated to designated internal and external stakeholders", task: "Keep guests informed via STR platform messaging systems on IoT/IT statuses as issues are resolved.", sentinel: false }
];

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', () => {
    loadDashboard();
});

// Switch between admin and guest tabs
function switchTab(tab) {
    currentTab = tab;

    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');

    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });

    if (tab === 'admin') {
        document.getElementById('admin-view').classList.add('active');
    } else if (tab === 'guest') {
        document.getElementById('guest-view').classList.add('active');
        // Render guest view if not already rendered
        if (scanData) {
            renderGuestView(scanData);
        }
    }
}

// Load dashboard data from API
async function loadDashboard() {
    try {
        // Fetch scan results
        const response = await fetch('/api/scan-results');

        if (!response.ok) {
            throw new Error('No scan results available');
        }

        scanData = await response.json();

        // Render dashboard sections
        renderNetworkSummary(scanData.network_summary);
        renderScanInfo(scanData.scan_info);
        renderDevicesTable(scanData.devices);

        // If guest view is active, render it too
        if (currentTab === 'guest') {
            renderGuestView(scanData);
        }

    } catch (error) {
        showError(error.message);
    }
}

// Show loading state
function showLoading() {
    const content = document.getElementById('dashboard-content');
    content.innerHTML = `
        <div class="loading">
            <div class="spinner"></div>
            <p>Loading scan results...</p>
        </div>
    `;
}

// Hide loading and show content
function hideLoading() {
    // Content is already rendered, just ensure it's visible
}

// Show error message
function showError(message) {
    const summaryContainer = document.getElementById('network-summary');
    const devicesContainer = document.getElementById('devices-table');
    const scanInfo = document.getElementById('scan-info');

    // Clear existing content
    summaryContainer.innerHTML = '';
    devicesContainer.innerHTML = '';
    scanInfo.innerHTML = '';

    // Show error in summary area
    summaryContainer.innerHTML = `
        <div class="error-message" style="grid-column: 1 / -1;">
            <h2>⚠️ Error</h2>
            <p>${message}</p>
            <p>Please run a network scan first to generate results.</p>
        </div>
    `;
}

// Render network summary cards
function renderNetworkSummary(summary) {
    const container = document.getElementById('network-summary');

    const html = `
        <div class="summary-card">
            <h3>Network Risk Level</h3>
            <div class="value">
                <span class="risk-badge risk-${summary.network_risk_level.toLowerCase()}">${summary.network_risk_level}</span>
            </div>
            <div class="label">Average Score: ${summary.average_risk_score}/100</div>
        </div>
        
        <div class="summary-card">
            <h3>Total Devices</h3>
            <div class="value">${summary.total_devices}</div>
            <div class="label">${summary.devices_at_risk} at risk</div>
        </div>
        
        <div class="summary-card">
            <h3>Total CVEs</h3>
            <div class="value ${summary.total_cves > 0 ? 'cve-count has-cves' : 'cve-count'}">${summary.total_cves}</div>
            <div class="label">Known vulnerabilities</div>
        </div>
        
        <div class="summary-card">
            <h3>Severity Breakdown</h3>
            <div class="value" style="font-size: 1rem; line-height: 1.8;">
                ${summary.severity_breakdown.critical > 0 ? `<span class="risk-badge risk-critical" style="font-size: 0.8rem; padding: 4px 10px;">Critical: ${summary.severity_breakdown.critical}</span><br>` : ''}
                ${summary.severity_breakdown.high > 0 ? `<span class="risk-badge risk-high" style="font-size: 0.8rem; padding: 4px 10px;">High: ${summary.severity_breakdown.high}</span><br>` : ''}
                ${summary.severity_breakdown.medium > 0 ? `<span class="risk-badge risk-medium" style="font-size: 0.8rem; padding: 4px 10px;">Medium: ${summary.severity_breakdown.medium}</span><br>` : ''}
                ${summary.severity_breakdown.low > 0 ? `<span class="risk-badge risk-low" style="font-size: 0.8rem; padding: 4px 10px;">Low: ${summary.severity_breakdown.low}</span><br>` : ''}
                ${summary.severity_breakdown.minimal > 0 ? `<span class="risk-badge risk-minimal" style="font-size: 0.8rem; padding: 4px 10px;">Minimal: ${summary.severity_breakdown.minimal}</span>` : ''}
            </div>
        </div>
    `;

    container.innerHTML = html;
}

// Render scan information
function renderScanInfo(scanInfo) {
    const container = document.getElementById('scan-info');

    const scanTime = new Date(scanInfo.timestamp).toLocaleString();

    container.innerHTML = `
        Last scan: ${scanTime} | Subnet: ${scanInfo.subnet} | Duration: ${scanInfo.duration || 'N/A'}
    `;
}

// Render devices table
function renderDevicesTable(devices) {
    const container = document.getElementById('devices-table');

    if (!devices || devices.length === 0) {
        container.innerHTML = '<p>No devices found in scan.</p>';
        return;
    }

    let tableHTML = `
        <table class="devices-table">
            <thead>
                <tr>
                    <th>Device</th>
                    <th>Vendor</th>
                    <th>Model/Version</th>
                    <th>CVE Count</th>
                    <th>Risk Level</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
    `;

    devices.forEach(device => {
        const identity = device.identity || {};
        const riskAssessment = device.risk_assessment || {};
        const cveResults = device.cve_results || {};

        const vendor = identity.vendor || 'Unknown';
        const model = identity.model || 'Unknown';
        const version = identity.version || '';
        const cveCount = cveResults.cve_count || 0;
        const riskLevel = riskAssessment.risk_level || 'Unknown';
        const riskScore = riskAssessment.risk_score || 0;

        // Get CVE severity breakdown
        const factors = riskAssessment.factors || {};
        const cvss = factors.cvss_severity || {};
        const critical = cvss.critical || 0;
        const high = cvss.high || 0;
        const medium = cvss.medium || 0;
        const low = cvss.low || 0;

        let breakdown = '';
        if (cveCount > 0) {
            const parts = [];
            if (critical > 0) parts.push(`${critical} critical`);
            if (high > 0) parts.push(`${high} high`);
            if (medium > 0) parts.push(`${medium} medium`);
            if (low > 0) parts.push(`${low} low`);
            breakdown = `<div class="cve-breakdown">${parts.join(', ')}</div>`;
        }

        tableHTML += `
            <tr>
                <td>
                    <div class="device-info">
                        <div class="device-ip">${device.ip}</div>
                        <div class="device-vendor">${device.mac || 'No MAC'}</div>
                    </div>
                </td>
                <td>${vendor}</td>
                <td>${model}${version ? ' ' + version : ''}</td>
                <td>
                    <div class="cve-count ${cveCount > 0 ? 'has-cves' : ''}">${cveCount}</div>
                    ${breakdown}
                </td>
                <td>
                    <span class="risk-badge risk-${riskLevel.toLowerCase()}">${riskLevel}</span>
                    <div style="font-size: 0.85rem; color: var(--text-secondary); margin-top: 5px;">Score: ${riskScore}/100</div>
                </td>
                <td>
                    <button class="btn" onclick="showDeviceDetails('${device.ip}')">View Details</button>
                </td>
            </tr>
        `;
    });

    tableHTML += `
            </tbody>
        </table>
    `;

    container.innerHTML = tableHTML;
}

// Show device details modal
function showDeviceDetails(ip) {
    const device = scanData.devices.find(d => d.ip === ip);
    if (!device) return;

    const modal = document.getElementById('device-modal');
    const content = document.getElementById('modal-device-content');

    const identity = device.identity || {};
    const riskAssessment = device.risk_assessment || {};
    const cveResults = device.cve_results || {};
    const recommendations = device.recommendations || [];

    let html = `
        <h2>Device Details: ${ip}</h2>
        
        <div style="margin: 20px 0;">
            <h3>Identity</h3>
            <p><strong>Vendor:</strong> ${identity.vendor || 'Unknown'}</p>
            <p><strong>Model:</strong> ${identity.model || 'Unknown'}</p>
            <p><strong>Version:</strong> ${identity.version || 'Unknown'}</p>
            <p><strong>Detection Method:</strong> ${identity.detection_method || 'Unknown'}</p>
            <p><strong>MAC Address:</strong> ${device.mac || 'Unknown'}</p>
            <p><strong>CPE:</strong> <code>${device.cpe_suggestion || 'N/A'}</code></p>
            <p><strong>CPE Validation:</strong> ${device.cpe_validation_status || 'N/A'}</p>
        </div>
        
        <div style="margin: 20px 0;">
            <h3>Risk Assessment</h3>
            <p><strong>Risk Level:</strong> <span class="risk-badge risk-${riskAssessment.risk_level?.toLowerCase()}">${riskAssessment.risk_level || 'Unknown'}</span></p>
            <p><strong>Risk Score:</strong> ${riskAssessment.risk_score || 0}/100</p>
            <p><strong>Confidence:</strong> ${riskAssessment.confidence || 'Unknown'}</p>
        </div>
    `;

    // CVE List
    if (cveResults.cves && cveResults.cves.length > 0) {
        html += `
            <div style="margin: 20px 0;">
                <h3>Vulnerabilities (${cveResults.cve_count} CVEs)</h3>
                <div class="cve-list">
        `;

        cveResults.cves.forEach(cve => {
            const severity = (cve.cvss_severity || 'unknown').toLowerCase();
            html += `
                <div class="cve-item ${severity}">
                    <div class="cve-id">
                        <a href="${cve.url}" target="_blank">${cve.id}</a>
                        ${cve.cvss_score ? `<span class="cve-score risk-badge risk-${severity}">${cve.cvss_score} (${cve.cvss_severity})</span>` : ''}
                    </div>
                    <div class="cve-description">${cve.description}</div>
                    ${cve.cvss_vector ? `<div style="font-size: 0.85rem; color: var(--text-secondary); margin-top: 5px;">Vector: ${cve.cvss_vector}</div>` : ''}
                </div>
            `;
        });

        html += `
                </div>
            </div>
        `;
    } else {
        html += `<p style="margin: 20px 0;">✓ No known vulnerabilities found</p>`;
    }

    // Recommendations
    if (recommendations && recommendations.length > 0) {
        html += `
            <div class="recommendations">
                <h3>Recommendations</h3>
                <ul>
        `;

        recommendations.forEach(rec => {
            html += `<li>${rec}</li>`;
        });

        html += `
                </ul>
            </div>
        `;
    }

    content.innerHTML = html;
    modal.classList.add('active');
}

// Close modal
function closeModal() {
    const modal = document.getElementById('device-modal');
    modal.classList.remove('active');
}

// Close modal when clicking outside
window.onclick = function (event) {
    const modal = document.getElementById('device-modal');
    if (event.target === modal) {
        closeModal();
    }
};

// Guest View Rendering
function renderGuestView(data) {
    renderGuestScanInfo(data.scan_info);
    renderGuestSummary(data);
    renderGuestDevicesList(data.devices);
    renderGuestVulnerabilitiesList(data.devices);
}

function renderGuestScanInfo(scanInfo) {
    const container = document.getElementById('guest-scan-info');
    const scanTime = new Date(scanInfo.timestamp).toLocaleString();
    container.innerHTML = `
        Last network scan: ${scanTime}
    `;
}

function renderGuestSummary(data) {
    const container = document.getElementById('guest-summary');
    const totalDevices = data.devices.length;

    // Count high/critical vulnerabilities
    let criticalCount = 0;
    let highCount = 0;

    data.devices.forEach(device => {
        const factors = device.risk_assessment?.factors?.cvss_severity || {};
        criticalCount += factors.critical || 0;
        highCount += factors.high || 0;
    });

    container.innerHTML = `
        <div class="guest-summary-card">
            <h3>Total Devices</h3>
            <div class="value">${totalDevices}</div>
        </div>
        <div class="guest-summary-card">
            <h3>Critical Vulnerabilities</h3>
            <div class="value critical-text">${criticalCount}</div>
        </div>
        <div class="guest-summary-card">
            <h3>High Vulnerabilities</h3>
            <div class="value high-text">${highCount}</div>
        </div>
    `;
}

function renderGuestDevicesList(devices) {
    const container = document.getElementById('guest-devices-list');

    if (!devices || devices.length === 0) {
        container.innerHTML = '<p>No devices found on network.</p>';
        return;
    }

    let html = '<div class="guest-devices-grid">';

    devices.forEach(device => {
        const identity = device.identity || {};
        const vendor = identity.vendor || 'Unknown';
        const model = identity.model || 'Unknown';
        const version = identity.version || '';
        const cveCount = device.cve_results?.cve_count || 0;

        html += `
            <div class="guest-device-card">
                <div class="guest-device-ip">${device.ip}</div>
                <div class="guest-device-info">
                    <strong>${vendor}</strong><br>
                    ${model}${version ? ' ' + version : ''}
                </div>
                ${cveCount > 0 ? `<div class="guest-device-cves">${cveCount} vulnerabilities</div>` : '<div class="guest-device-cves safe">No known vulnerabilities</div>'}
            </div>
        `;
    });

    html += '</div>';
    container.innerHTML = html;
}

async function renderGuestVulnerabilitiesList(devices) {
    const container = document.getElementById('guest-vulnerabilities-list');

    // Collect all high/critical CVEs across all devices
    const vulnerabilities = [];

    devices.forEach(device => {
        const cves = device.cve_results?.cves || [];

        cves.forEach(cve => {
            const severity = (cve.cvss_severity || '').toLowerCase();
            if (severity === 'critical' || severity === 'high') {
                vulnerabilities.push({
                    cve: cve,
                    device: device,
                    severity: severity
                });
            }
        });
    });

    if (vulnerabilities.length === 0) {
        container.innerHTML = '<p class="good-news">✓ No high or critical vulnerabilities detected on the network.</p>';
        return;
    }

    // Sort by severity (critical first) and then by CVSS score
    vulnerabilities.sort((a, b) => {
        if (a.severity === 'critical' && b.severity !== 'critical') return -1;
        if (a.severity !== 'critical' && b.severity === 'critical') return 1;
        return (b.cve.cvss_score || 0) - (a.cve.cvss_score || 0);
    });

    // Show loading state
    container.innerHTML = '<p class="loading-recommendations">🤖 AI Security Recommendations...</p>';

    // Fetch AI recommendations
    let aiRecommendations = {};
    try {
        const response = await fetch('/api/guest/bulk-recommendations');
        if (response.ok) {
            const data = await response.json();
            aiRecommendations = data.recommendations || {};
            console.log(`Loaded ${Object.keys(aiRecommendations).length} AI recommendations`);
        } else {
            console.warn('Could not load AI recommendations, using fallback');
        }
    } catch (error) {
        console.error('Error fetching recommendations:', error);
    }

    let html = '<div class="guest-vulnerabilities-list">';

    vulnerabilities.forEach(vuln => {
        const cve = vuln.cve;
        const device = vuln.device;
        const identity = device.identity || {};

        // Get AI recommendation for this CVE
        const recommendation = aiRecommendations[cve.id];

        html += `
            <div class="guest-vuln-card ${vuln.severity}">
                <div class="guest-vuln-header">
                    <div class="guest-vuln-id">
                        <a href="${cve.url}" target="_blank">${cve.id}</a>
                        <span class="risk-badge risk-${vuln.severity}">${cve.cvss_score} (${cve.cvss_severity})</span>
                    </div>
                    <div class="guest-vuln-device">
                        Affects: <strong>${device.ip}</strong> (${identity.vendor || 'Unknown'} ${identity.model || ''})
                    </div>
                </div>
                <div class="guest-vuln-suggestions">
                    <h4>🔒 Privacy & Safety Guidance:</h4>
                    ${renderRecommendation(recommendation, vuln.severity)}
                </div>
                <details class="guest-technical-details">
                    <summary>📋 Technical Details</summary>
                    <div class="technical-description">${cve.description}</div>
                </details>
            </div>
        `;
    });

    html += '</div>';
    container.innerHTML = html;
}

function renderRecommendation(recommendation, severity) {
    // If no AI recommendation available, show simple message
    if (!recommendation) {
        return `
            <div class="suggestion-fallback">
                <p><em>⚠️ AI recommendations not available</em></p>
            </div>
        `;
    }

    // Render AI-generated recommendation
    return `
        <div class="recommendation-ai">
            ${recommendation.summary ? `<p class="recommendation-summary"><strong>${recommendation.summary}</strong></p>` : ''}
            
            ${recommendation.immediate_actions && recommendation.immediate_actions.length > 0 ? `
                <div class="recommendation-section">
                    <h5>🤖 AI Recommendations:</h5>
                    <ul>
                        ${recommendation.immediate_actions.map(action => `<li>${action}</li>`).join('')}
                    </ul>
                </div>
            ` : ''}
            
            ${recommendation.best_practices && recommendation.best_practices.length > 0 ? `
                <div class="recommendation-section">
                    <h5>🏖️ During Your Stay:</h5>
                    <ul>
                        ${recommendation.best_practices.map(practice => `<li>${practice}</li>`).join('')}
                    </ul>
                </div>
            ` : ''}
            
            ${recommendation.risk_explanation ? `
                <div class="risk-explanation">
                    <strong>Privacy Risk:</strong> ${recommendation.risk_explanation}
                </div>
            ` : ''}
        </div>
    `;
}

// ===== Compliance Checklist =====

function getComplianceState() {
    try {
        return JSON.parse(localStorage.getItem('strSentinelCompliance')) || {};
    } catch {
        return {};
    }
}

function saveComplianceState(state) {
    localStorage.setItem('strSentinelCompliance', JSON.stringify(state));
}

let complianceRendered = false;

function toggleComplianceDropdown() {
    const body = document.getElementById('compliance-dropdown-body');
    const toggle = document.querySelector('.compliance-dropdown-toggle');
    const isOpen = body.classList.toggle('open');
    toggle.classList.toggle('open', isOpen);

    if (isOpen && !complianceRendered) {
        renderComplianceChecklist();
        complianceRendered = true;
    }
}

function renderComplianceChecklist() {
    const container = document.getElementById('compliance-checklist');
    const state = getComplianceState();

    // Group items by function
    const groups = {};
    complianceData.forEach((item, index) => {
        if (!groups[item.function]) {
            groups[item.function] = [];
        }
        groups[item.function].push({ ...item, index });
    });

    let html = '';

    for (const [func, items] of Object.entries(groups)) {
        // Determine function color class
        const funcClass = func.includes('GOVERN') ? 'govern' :
            func.includes('IDENTIFY') ? 'identify' :
                func.includes('PROTECT') ? 'protect' :
                    func.includes('DETECT') ? 'detect' :
                        func.includes('RESPOND') ? 'respond' :
                            func.includes('RECOVER') ? 'recover' : '';

        html += `<div class="compliance-group">`;
        html += `<div class="compliance-group-header ${funcClass}">${func}</div>`;

        items.forEach(item => {
            const isChecked = item.sentinel || state[item.index] === true;
            const isSentinel = item.sentinel;

            html += `
                <div class="compliance-item ${isChecked ? 'checked' : ''}">
                    <label class="compliance-checkbox-label">
                        <input type="checkbox" 
                               class="compliance-checkbox" 
                               data-index="${item.index}"
                               ${isChecked ? 'checked' : ''} 
                               ${isSentinel ? 'disabled' : ''}
                               onchange="toggleComplianceItem(${item.index}, this.checked)">
                        <span class="compliance-checkmark"></span>
                    </label>
                    <div class="compliance-content">
                        <div class="compliance-category">${item.category}</div>
                        <div class="compliance-task">${item.task}</div>
                        <div class="compliance-nist">${item.nistDescription}</div>
                        ${isSentinel ? '<span class="compliance-sentinel-badge">✓ STR Sentinel</span>' : ''}
                    </div>
                </div>
            `;
        });

        html += `</div>`;
    }

    container.innerHTML = html;
    updateComplianceProgress();
}

function toggleComplianceItem(index, checked) {
    const state = getComplianceState();
    if (checked) {
        state[index] = true;
    } else {
        delete state[index];
    }
    saveComplianceState(state);

    // Update visual state
    const item = document.querySelector(`.compliance-checkbox[data-index="${index}"]`).closest('.compliance-item');
    if (checked) {
        item.classList.add('checked');
    } else {
        item.classList.remove('checked');
    }

    updateComplianceProgress();
}

function updateComplianceProgress() {
    const state = getComplianceState();
    const total = complianceData.length;
    let completed = 0;

    complianceData.forEach((item, index) => {
        if (item.sentinel || state[index] === true) {
            completed++;
        }
    });

    const percent = Math.round((completed / total) * 100);
    const container = document.getElementById('compliance-progress');

    container.innerHTML = `
        <div class="progress-stats">${completed} of ${total} tasks completed (${percent}%)</div>
        <div class="progress-bar-track">
            <div class="progress-bar-fill" style="width: ${percent}%"></div>
        </div>
    `;
}
