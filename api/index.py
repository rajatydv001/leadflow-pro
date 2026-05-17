import json
import re
import uuid
import io
import sys
import os

os.environ.setdefault('GOOGLE_SHEETS_ENABLED', 'false')
os.environ.setdefault('GOOGLE_DRIVE_ENABLED', 'false')

from flask import Flask, jsonify, Response

app = Flask(__name__)

@app.route('/')
def index():
    try:
        with open('templates/index.html', 'r') as f:
            content = f.read()
        return Response(content, mimetype='text/html')
    except:
        return '<html><body><h1>LeadFlow Pro</h1><p>Form at /api/leads</p></body></html>'

@app.route('/api/health')
def health():
    from datetime import datetime
    from api.config import Config
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'services': {
            'sheets_enabled': Config.GOOGLE_SHEETS_ENABLED,
            'drive_enabled': Config.GOOGLE_DRIVE_ENABLED,
            'vercel_deployment': True,
            'sheetdb_endpoint': os.environ.get('SHEETDB_ENDPOINT', 'NOT SET')
        }
    })

@app.route('/api/leads', methods=['POST'])
def submit_lead():
    from flask import request
    
    data = request.get_json() or {}
    
    errors = {}
    if not data.get('fullName') or not data.get('fullName').strip():
        errors['fullName'] = 'Full name is required'
    if not data.get('email') or not data.get('email').strip():
        errors['email'] = 'Email is required'
    elif not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', data.get('email', '')):
        errors['email'] = 'Invalid email format'
    if not data.get('companyName') or not data.get('companyName').strip():
        errors['companyName'] = 'Company name is required'
    
    if errors:
        return jsonify({
            'status': 'error',
            'message': 'Validation failed',
            'errors': errors
        }), 400
    
    lead_id = str(uuid.uuid4())
    status = "Generated"
    
    try:
        from api.services.enrichment import CompanyEnrichmentService
        from api.services.pdf_generator import PDFGenerator
        from api.services.email_service import EmailService
        from api.services.sheets_service import SheetsService
        
        enrichment_service = CompanyEnrichmentService()
        pdf_generator = PDFGenerator()
        email_service = EmailService()
        sheets_service = SheetsService()
        
        if sheets_service.enabled:
            sheets_service.append_lead(data, "Processing")
        
        enriched_data = enrichment_service.enrich_company(
            data['companyName'],
            data.get('website')
        )
        
        pdf_filename, pdf_buffer = pdf_generator.generate_report_in_memory(data, enriched_data)
        pdf_buffer.seek(0)
        
        email_sent = email_service.send_report_email_with_buffer(
            data['email'],
            data['fullName'],
            enriched_data.get('name', data['companyName']),
            pdf_buffer,
            pdf_filename
        )
        
        status = "Sent" if email_sent else "Generated"
        
        if sheets_service.enabled:
            sheets_service.update_lead_status(data['email'], status)
        
    except Exception as e:
        print(f"Processing error: {e}")
        status = "Failed"
    
    return jsonify({
        'status': 'success',
        'message': 'Lead submitted successfully. Report will be sent to your email shortly.',
        'leadId': lead_id
    }), 202

@app.route('/static/<path:filename>')
def static_files(filename):
    try:
        if filename.endswith('.js'):
            with open('static/script.js', 'r') as f:
                content = f.read()
            return Response(content, mimetype='application/javascript')
        elif filename.endswith('.css'):
            with open('static/style.css', 'r') as f:
                content = f.read()
            return Response(content, mimetype='text/css')
    except:
        return 'Not found', 404

