import logging
from datetime import datetime

'''
CODE GENERATED WITH ASSISTANCE FROM VARIOUS AI TOOLS.
ALL AI-GENERATED CONTENT WAS REVIEWED, REVISED, AND ADAPTED TO MEET STR SENTINEL REQUIREMENTS.
'''

def calculate_device_risk_score(device_data):
    """
    Calculate a comprehensive risk score for a device based on CVE data, CVSS scores,
    validation status, and device characteristics.
    
    Args:
        device_data: Dictionary containing device info including:
            - cve_results: CVE query results from cve_lookup
            - cpe_validation_status: 'validated' or 'unvalidated'
            - identity: Device identity information
    
    Returns:
        Dictionary containing:
        - 'risk_score': Overall risk score (0-100)
        - 'risk_level': 'Critical', 'High', 'Medium', 'Low', or 'Unknown'
        - 'confidence': Confidence level in the assessment
        - 'factors': Breakdown of risk factors
    """
    risk_score = 0
    factors = {}
    
    # Get CVE results
    cve_results = device_data.get('cve_results', {})
    cve_count = cve_results.get('cve_count', 0)
    cves = cve_results.get('cves', [])
    
    # Factor 1: CVE Count (max 30 points)
    if cve_count == 0:
        cve_points = 0
    elif cve_count <= 5:
        cve_points = 10
    elif cve_count <= 20:
        cve_points = 20
    else:
        cve_points = 30
    
    risk_score += cve_points
    factors['cve_count'] = {
        'count': cve_count,
        'points': cve_points,
        'weight': '30%'
    }
    
    # Factor 2: CVSS Severity Distribution (max 50 points)
    severity_points = 0
    critical_count = 0
    high_count = 0
    medium_count = 0
    low_count = 0
    
    for cve in cves:
        cvss_score = cve.get('cvss_score')
        severity = (cve.get('cvss_severity') or 'UNKNOWN').upper()
        
        if severity == 'CRITICAL' or (cvss_score and cvss_score >= 9.0):
            severity_points += 10
            critical_count += 1
        elif severity == 'HIGH' or (cvss_score and cvss_score >= 7.0):
            severity_points += 5
            high_count += 1
        elif severity == 'MEDIUM' or (cvss_score and cvss_score >= 4.0):
            severity_points += 2
            medium_count += 1
        elif severity == 'LOW' or (cvss_score and cvss_score > 0):
            severity_points += 1
            low_count += 1
    
    # Cap at 50 points
    severity_points = min(severity_points, 50)
    risk_score += severity_points
    
    factors['cvss_severity'] = {
        'critical': critical_count,
        'high': high_count,
        'medium': medium_count,
        'low': low_count,
        'points': severity_points,
        'weight': '50%'
    }
    
    # Factor 3: Validation Status (affects confidence, adds 10 points if unvalidated)
    validation_status = device_data.get('cpe_validation_status', 'unvalidated')
    validation_penalty = 0
    confidence = 'High'
    
    if validation_status == 'unvalidated':
        validation_penalty = 10  # Penalty for unvalidated CPE (uncertainty risk)
        confidence = 'Medium'
    
    risk_score += validation_penalty
    factors['validation'] = {
        'status': validation_status,
        'penalty': validation_penalty,
        'weight': '10%'
    }
    
    # Factor 4: Device Type (network-exposed devices are higher risk) - max 10 points
    identity = device_data.get('identity', {})
    device_type_points = 0
    
    # Check detection method and device characteristics
    detection_method = identity.get('detection_method', 'Unknown')
    model = (identity.get('model') or '').lower()
    
    # Network cameras, IoT devices, and exposed SSH services are higher risk
    if 'camera' in model or 'hikvision' in model or 'dahua' in model:
        device_type_points = 10  # Cameras are common attack targets
    elif detection_method == 'SSH' and identity.get('service') == 'ssh':
        device_type_points = 8  # Exposed SSH is a risk
    elif detection_method == 'HTTP':
        device_type_points = 6  # Web-exposed devices
    elif detection_method == 'mDNS':
        device_type_points = 4  # Local network discovery
    else:
        device_type_points = 2
    
    risk_score += device_type_points
    factors['device_exposure'] = {
        'type': detection_method,
        'points': device_type_points,
        'weight': '10%'
    }
    
    # Cap final score at 100
    risk_score = min(risk_score, 100)
    
    # Determine risk level based on final score
    if risk_score >= 80:
        risk_level = 'Critical'
    elif risk_score >= 60:
        risk_level = 'High'
    elif risk_score >= 40:
        risk_level = 'Medium'
    elif risk_score >= 20:
        risk_level = 'Low'
    else:
        risk_level = 'Minimal'
    
    # If no CVEs found, set to Unknown unless device is validated
    if cve_count == 0:
        if validation_status == 'validated':
            risk_level = 'Minimal'
            confidence = 'High'
        else:
            risk_level = 'Unknown'
            confidence = 'Low'
    
    return {
        'risk_score': round(risk_score, 1),
        'risk_level': risk_level,
        'confidence': confidence,
        'factors': factors
    }


def calculate_network_risk_summary(devices_list):
    """
    Calculate overall network risk summary from all scanned devices.
    
    Args:
        devices_list: List of device dictionaries with risk assessments
    
    Returns:
        Dictionary with network-wide risk metrics
    """
    total_devices = len(devices_list)
    
    if total_devices == 0:
        return {
            'total_devices': 0,
            'devices_at_risk': 0,
            'total_cves': 0,
            'average_risk_score': 0,
            'network_risk_level': 'Unknown',
            'severity_breakdown': {
                'critical': 0,
                'high': 0,
                'medium': 0,
                'low': 0,
                'minimal': 0,
                'unknown': 0
            }
        }
    
    total_cves = 0
    total_risk_score = 0
    devices_at_risk = 0
    
    severity_breakdown = {
        'critical': 0,
        'high': 0,
        'medium': 0,
        'low': 0,
        'minimal': 0,
        'unknown': 0
    }
    
    for device in devices_list:
        risk_assessment = device.get('risk_assessment', {})
        risk_level = risk_assessment.get('risk_level', 'Unknown').lower()
        risk_score = risk_assessment.get('risk_score', 0)
        
        cve_results = device.get('cve_results', {})
        device_cve_count = cve_results.get('cve_count', 0)
        
        total_cves += device_cve_count
        total_risk_score += risk_score
        
        # Count devices with non-minimal risk
        if risk_level not in ['minimal', 'unknown']:
            devices_at_risk += 1
        
        # Update severity breakdown
        severity_breakdown[risk_level] = severity_breakdown.get(risk_level, 0) + 1
    
    average_risk_score = total_risk_score / total_devices
    
    # Determine overall network risk level
    critical_ratio = severity_breakdown['critical'] / total_devices
    high_ratio = severity_breakdown['high'] / total_devices
    
    if critical_ratio >= 0.3 or average_risk_score >= 80:
        network_risk_level = 'Critical'
    elif critical_ratio >= 0.1 or high_ratio >= 0.3 or average_risk_score >= 60:
        network_risk_level = 'High'
    elif average_risk_score >= 40:
        network_risk_level = 'Medium'
    elif average_risk_score >= 20:
        network_risk_level = 'Low'
    else:
        network_risk_level = 'Minimal'
    
    return {
        'total_devices': total_devices,
        'devices_at_risk': devices_at_risk,
        'total_cves': total_cves,
        'average_risk_score': round(average_risk_score, 1),
        'network_risk_level': network_risk_level,
        'severity_breakdown': severity_breakdown
    }


def generate_recommendations(device_data):
    """
    Generate remediation recommendations based on device risk assessment.
    
    Args:
        device_data: Device dictionary with risk assessment
    
    Returns:
        List of recommendation strings
    """
    recommendations = []
    
    risk_assessment = device_data.get('risk_assessment', {})
    risk_level = risk_assessment.get('risk_level', 'Unknown')
    cve_results = device_data.get('cve_results', {})
    identity = device_data.get('identity', {})
    
    # Critical/High severity CVEs
    factors = risk_assessment.get('factors', {})
    severity_data = factors.get('cvss_severity', {})
    critical_count = severity_data.get('critical', 0)
    high_count = severity_data.get('high', 0)
    
    if critical_count > 0:
        recommendations.append(f"⚠️ URGENT: {critical_count} critical vulnerabilities detected - patch immediately or isolate device")
    
    if high_count > 0:
        recommendations.append(f"⚠️ {high_count} high-severity vulnerabilities - update firmware/software as soon as possible")
    
    # Unvalidated CPE
    if device_data.get('cpe_validation_status') == 'unvalidated':
        recommendations.append("Verify device model and version - CPE could not be validated against NVD database")
    
    # Device-specific recommendations
    model = (identity.get('model') or '').lower()
    vendor = (identity.get('vendor') or '').lower()
    
    if 'camera' in model or 'hikvision' in vendor or 'dahua' in vendor:
        recommendations.append("Network camera detected - ensure it's on an isolated VLAN and change default credentials")
    
    if identity.get('detection_method') == 'SSH':
        recommendations.append("SSH service exposed - disable password authentication and use key-based auth only")
    
    # General best practices
    if risk_level in ['Critical', 'High']:
        recommendations.append("Consider network segmentation to isolate high-risk devices")
        recommendations.append("Enable automatic security updates if supported")
    
    if not recommendations:
        recommendations.append("✓ No immediate action required - continue monitoring for new vulnerabilities")
    
    return recommendations
