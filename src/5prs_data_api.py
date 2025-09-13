#!/usr/bin/env python3
"""
5PRS Data API Server
Provides REST API endpoint for the 5PRS Dashboard to fetch data from Google Drive and local folders
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import logging
import subprocess

# Add parent directory for imports
sys.path.append(str(Path(__file__).parent.parent))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__, static_folder='../5PRS DASHBOARD')
CORS(app)  # Enable CORS for all routes

# Configuration
DATA_CACHE = {}
CACHE_DURATION = 300  # 5 minutes cache


@app.route('/api/5prs-data', methods=['GET'])
def get_5prs_data():
    """
    API endpoint to get 5PRS data
    Mimics the original /api/5prs-data endpoint expected by the dashboard
    """
    try:
        # Get month and year from query parameters (optional)
        month = request.args.get('month', datetime.now().strftime('%B').lower())
        year = request.args.get('year', datetime.now().year, type=int)
        
        # Check cache
        cache_key = f"{month}_{year}"
        if cache_key in DATA_CACHE:
            cached_data, cached_time = DATA_CACHE[cache_key]
            if (datetime.now() - cached_time).seconds < CACHE_DURATION:
                logger.info(f"Returning cached data for {month} {year}")
                return jsonify(cached_data)
        
        # Run the integration script to get fresh data
        logger.info(f"Fetching fresh data for {month} {year}")
        
        # Execute the integration script
        result = subprocess.run([
            sys.executable,
            'src/integrate_5prs_data.py',
            '--month', month,
            '--year', str(year),
            '--api-mode'
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)
        
        if result.returncode == 0:
            # Parse the output
            try:
                output = json.loads(result.stdout)
                if output['status'] == 'success':
                    # Read the generated JSON file
                    json_file = Path(output['file'])
                    if json_file.exists():
                        with open(json_file, 'r', encoding='utf-8') as f:
                            integrated_data = json.load(f)
                        
                        # Format data for dashboard consumption
                        response_data = format_for_dashboard(integrated_data)
                        
                        # Cache the data
                        DATA_CACHE[cache_key] = (response_data, datetime.now())
                        
                        return jsonify(response_data)
                    else:
                        return jsonify({
                            'status': 'error',
                            'message': 'Data file not found'
                        }), 404
                else:
                    return jsonify({
                        'status': 'error',
                        'message': output.get('message', 'Integration failed')
                    }), 500
            except json.JSONDecodeError:
                logger.error(f"Failed to parse integration output: {result.stdout}")
                return jsonify({
                    'status': 'error',
                    'message': 'Failed to parse integration output'
                }), 500
        else:
            logger.error(f"Integration script failed: {result.stderr}")
            return jsonify({
                'status': 'error',
                'message': 'Data integration failed'
            }), 500
            
    except Exception as e:
        logger.error(f"Error in get_5prs_data: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


def convert_to_float(value):
    """
    Safely convert a value to float, handling NaN, NaT, None, and string values
    """
    try:
        if value is None or value == '' or str(value).lower() in ['nan', 'nat', 'none']:
            return 0.0
        return float(value)
    except (ValueError, TypeError):
        return 0.0


def format_for_dashboard(integrated_data):
    """
    Format the integrated data for dashboard consumption
    The dashboard expects data in a specific format
    """
    try:
        # Extract raw data records
        raw_data = integrated_data.get('raw_data', [])
        
        # Standardize column names to match dashboard expectations
        formatted_records = []
        for record in raw_data:
            # Get validation qty with fallback to Pass Qty if Validation Qty is 0
            validation_qty_raw = convert_to_float(record.get('validation_qty', record.get('Validation Qty', record.get('Validation_Qty', 0))))
            pass_qty_raw = convert_to_float(record.get('pass_qty', record.get('Pass Qty', record.get('Pass_Qty', 0))))
            reject_qty_raw = convert_to_float(record.get('reject_qty', record.get('Reject Qty', record.get('Reject_Qty', 0))))
            
            # If Validation Qty is 0 but Pass Qty exists, use Pass Qty + Reject Qty as Validation Qty
            if validation_qty_raw == 0 and (pass_qty_raw > 0 or reject_qty_raw > 0):
                validation_qty_raw = pass_qty_raw + reject_qty_raw
            
            formatted_record = {
                'Inspection Date': record.get('date', record.get('Date', '')),
                'Inspector ID': record.get('inspector_id', record.get('Inspector ID', '')),
                'Inspector Name': record.get('inspector_name', record.get('Inspector Name', record.get('inspector_id', ''))),
                'Time': record.get('shift', record.get('Time', record.get('Shift', ''))),
                'Building': record.get('building', record.get('Building', record.get('Factory', ''))),
                'Line': record.get('line', record.get('Line', '')),
                'PO No': record.get('po_number', record.get('PO No', record.get('PO_Number', ''))),
                'PO Item': record.get('po_item', record.get('PO Item', record.get('PO_Item', ''))),
                'Model': record.get('model', record.get('Model', record.get('product', ''))),
                'TQC ID': record.get('tqc_id', record.get('TQC ID', record.get('QC_ID', ''))),
                'TQC Name': record.get('tqc_name', record.get('TQC Name', record.get('QC_Name', ''))),
                'Validation Qty': validation_qty_raw,
                'Pass Qty': pass_qty_raw,
                'Reject Qty': reject_qty_raw,
                'Error': record.get('defect_type', record.get('Error', record.get('Defect_Type', '')))
            }
            
            # Calculate reject rate
            validation_qty = formatted_record['Validation Qty']
            reject_qty = formatted_record['Reject Qty']
            if validation_qty > 0:
                formatted_record['Reject_Rate'] = round((reject_qty / validation_qty) * 100, 2)
            else:
                formatted_record['Reject_Rate'] = 0
            
            formatted_records.append(formatted_record)
        
        # Build response
        response = {
            'status': 'success',
            'data': formatted_records,
            'metadata': {
                'total_records': len(formatted_records),
                'source': 'Google Drive + Local Files',
                'timestamp': datetime.now().isoformat(),
                'statistics': integrated_data.get('statistics', {}),
                'charts': integrated_data.get('charts', {})
            }
        }
        
        return response
        
    except Exception as e:
        logger.error(f"Error formatting data: {e}")
        return {
            'status': 'error',
            'message': f'Data formatting error: {str(e)}',
            'data': []
        }


@app.route('/')
def serve_dashboard():
    """Serve the main dashboard HTML file"""
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/output_files/<path:path>')
def serve_output_files(path):
    """Serve files from the output_files directory"""
    output_dir = Path(__file__).parent.parent / 'output_files'
    return send_from_directory(str(output_dir), path)


@app.route('/<path:path>')
def serve_static(path):
    """Serve static files from the 5PRS DASHBOARD directory"""
    return send_from_directory(app.static_folder, path)


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'cache_size': len(DATA_CACHE)
    })


@app.route('/api/clear-cache', methods=['POST'])
def clear_cache():
    """Clear the data cache"""
    global DATA_CACHE
    DATA_CACHE = {}
    return jsonify({
        'status': 'success',
        'message': 'Cache cleared'
    })


if __name__ == '__main__':
    # Check if port is provided as command line argument
    import argparse
    parser = argparse.ArgumentParser(description='5PRS Data API Server')
    parser.add_argument('--port', type=int, default=5000, help='Port to run the server on')
    parser.add_argument('--host', type=str, default='127.0.0.1', help='Host to run the server on')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode')
    
    args = parser.parse_args()
    
    logger.info(f"Starting 5PRS Data API Server on {args.host}:{args.port}")
    logger.info(f"Dashboard will be available at http://{args.host}:{args.port}/")
    logger.info(f"API endpoint: http://{args.host}:{args.port}/api/5prs-data")
    
    app.run(host=args.host, port=args.port, debug=args.debug)