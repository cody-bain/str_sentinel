// CODE GENERATED WITH ASSISTANCE FROM VARIOUS AI TOOLS.
// ALL AI-GENERATED CONTENT WAS REVIEWED, REVISED, AND ADAPTED TO MEET STR SENTINEL REQUIREMENTS.


let scanData = null;
let currentTab = 'admin';

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
