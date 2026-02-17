from flask import Flask, render_template, jsonify, send_from_directory
import json
import os
import logging
from datetime import datetime

# Some code snippets developed with assistance from generative AI tools. All AI-generated content was reviewed, revised, and adapted to meet STR Sentinel requirements.

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
