from flask import Flask, render_template, jsonify, send_from_directory, request
import json
import os
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv('/app/.env')

from ai_recommendations import generate_bulk_recommendations

'''
CODE GENERATED WITH ASSISTANCE FROM VARIOUS AI TOOLS.
ALL AI-GENERATED CONTENT WAS REVIEWED, REVISED, AND ADAPTED TO MEET STR SENTINEL REQUIREMENTS.
'''

app = Flask(__name__, 
            template_folder='web',
            static_folder='web/static')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)

# Path to scan results
RESULTS_FILE = "/app/shared/discovery-scan.json"


@app.route('/')
def index():
    """Serve the main dashboard page"""
    return render_template('index.html')


@app.route('/api/scan-results')
def get_scan_results():
    """
    API endpoint to get the latest scan results.
    Returns JSON with device data, CVEs, and risk assessments.
    """
    try:
        if not os.path.exists(RESULTS_FILE):
            return jsonify({
                'error': 'No scan results available',
                'message': 'Run a scan first to see results'
            }), 404
        
        with open(RESULTS_FILE, 'r') as f:
            data = json.load(f)
        
        return jsonify(data)
    
    except Exception as e:
        logging.error(f"Error reading scan results: {e}")
        return jsonify({
            'error': 'Failed to load scan results',
            'message': str(e)
        }), 500


@app.route('/api/network-summary')
def get_network_summary():
    """
    API endpoint to get network-wide risk summary.
    """
    try:
        if not os.path.exists(RESULTS_FILE):
            return jsonify({
                'error': 'No scan results available'
            }), 404
        
        with open(RESULTS_FILE, 'r') as f:
            data = json.load(f)
        
        # Extract summary data
        summary = data.get('network_summary', {})
        scan_info = data.get('scan_info', {})
        
        return jsonify({
            'scan_info': scan_info,
            'network_summary': summary
        })
    
    except Exception as e:
        logging.error(f"Error reading network summary: {e}")
        return jsonify({
            'error': 'Failed to load network summary',
            'message': str(e)
        }), 500


@app.route('/api/device/<ip>')
def get_device_details(ip):
    """
    API endpoint to get detailed information for a specific device.
    """
    try:
        if not os.path.exists(RESULTS_FILE):
            return jsonify({
                'error': 'No scan results available'
            }), 404
        
        with open(RESULTS_FILE, 'r') as f:
            data = json.load(f)
        
        devices = data.get('devices', [])
        
        # Find device by IP
        device = next((d for d in devices if d.get('ip') == ip), None)
        
        if device:
            return jsonify(device)
        else:
            return jsonify({
                'error': 'Device not found',
                'ip': ip
            }), 404
    
    except Exception as e:
        logging.error(f"Error reading device details: {e}")
        return jsonify({
            'error': 'Failed to load device details',
            'message': str(e)
        }), 500


@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'STR Sentinel Dashboard'
    })


@app.route('/api/guest/recommendations', methods=['POST'])
def get_guest_recommendations():
    """
    API endpoint to generate AI-powered recommendations for guest vulnerabilities.
    Expects JSON with CVE and device information.
    """
    try:
        vulnerability_data = request.json
        
        if not vulnerability_data:
            return jsonify({
                'error': 'No vulnerability data provided'
            }), 400
        
        # Generate recommendation using bulk function with single item
        vulnerabilities = [{
            'cve_id': vulnerability_data.get('cve_id', ''),
            'description': vulnerability_data.get('description', ''),
            'cvss_score': vulnerability_data.get('cvss_score', 0),
            'cvss_severity': vulnerability_data.get('cvss_severity', 'UNKNOWN'),
            'device_ip': vulnerability_data.get('device_ip', 'unknown'),
            'device_vendor': vulnerability_data.get('device_vendor', 'unknown'),
            'device_model': vulnerability_data.get('device_model', 'unknown'),
        }]
        
        recommendations = generate_bulk_recommendations(vulnerabilities)
        cve_id = vulnerability_data.get('cve_id', '')
        recommendation = recommendations.get(cve_id, {})
        
        return jsonify(recommendation)
    
    except Exception as e:
        logging.error(f"Error generating recommendations: {e}")
        return jsonify({
            'error': 'Failed to generate recommendations',
            'message': str(e)
        }), 500


@app.route('/api/guest/bulk-recommendations', methods=['GET'])
def get_bulk_guest_recommendations():
    """
    API endpoint to generate AI-powered recommendations for all high/critical CVEs.
    Reads from scan results and generates recommendations for guest view.
    """
    try:
        if not os.path.exists(RESULTS_FILE):
            return jsonify({
                'error': 'No scan results available'
            }), 404
        
        with open(RESULTS_FILE, 'r') as f:
            data = json.load(f)
        
        devices = data.get('devices', [])
        
        # Collect all high/critical vulnerabilities
        vulnerabilities = []
        for device in devices:
            identity = device.get('identity', {})
            cves = device.get('cve_results', {}).get('cves', [])
            
            for cve in cves:
                severity = (cve.get('cvss_severity', '')).upper()
                if severity in ['CRITICAL', 'HIGH']:
                    vulnerabilities.append({
                        'cve_id': cve.get('id'),
                        'description': cve.get('description', ''),
                        'cvss_score': cve.get('cvss_score', 0),
                        'cvss_severity': severity,
                        'device_ip': device.get('ip', 'unknown'),
                        'device_vendor': identity.get('vendor', 'unknown'),
                        'device_model': identity.get('model', 'unknown'),
                        'device_location': device.get('location', 'unknown')
                    })
        
        # Generate recommendations
        logging.info(f"Generating recommendations for {len(vulnerabilities)} high/critical vulnerabilities")
        recommendations = generate_bulk_recommendations(vulnerabilities)
        
        return jsonify({
            'count': len(recommendations),
            'recommendations': recommendations
        })
    
    except Exception as e:
        logging.error(f"Error generating bulk recommendations: {e}")
        return jsonify({
            'error': 'Failed to generate recommendations',
            'message': str(e)
        }), 500


if __name__ == '__main__':
    # Run Flask development server
    # In production, use gunicorn or another WSGI server
    port = int(os.getenv('DASHBOARD_PORT', 5001))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    logging.info(f"Starting STR Sentinel Dashboard on port {port}")
    logging.info(f"Dashboard accessible at http://localhost:{port}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )
