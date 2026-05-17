import os
import sys
import json
import re
import uuid
import io
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ['GOOGLE_SHEETS_ENABLED'] = 'false'
os.environ['GOOGLE_DRIVE_ENABLED'] = 'false'

def handler(event, context):
    path = event.get('path', '/')
    method = event.get('httpMethod', 'GET')
    headers = event.get('headers', {})
    
    cors_headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
    }
    
    if method == 'OPTIONS':
        return '', 204, cors_headers
    
    response_headers = {**cors_headers, 'Content-Type': 'application/json'}
    
    if path == '/':
        try:
            with open('templates/index.html', 'r') as f:
                content = f.read()
            return content, 200, {**cors_headers, 'Content-Type': 'text/html'}
        except:
            return json.dumps({'error': 'Template not found'}), 500, response_headers
    
    if path == '/api/health':
        return json.dumps({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'services': {
                'sheets_enabled': False,
                'drive_enabled': False,
                'vercel_deployment': True
            }
        }), 200, response_headers
    
    if path == '/api/leads' and method == 'POST':
        try:
            body = event.get('body', '')
            if isinstance(body, str):
                data = json.loads(body) if body else {}
            else:
                data = body
        except:
            data = {}
        
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
            return json.dumps({
                'status': 'error',
                'message': 'Validation failed',
                'errors': errors
            }), 400, response_headers
        
        lead_id = str(uuid.uuid4())
        
        try:
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from api.services.enrichment import CompanyEnrichmentService
            from api.services.pdf_generator import PDFGenerator
            from api.services.email_service import EmailService
            
            enrichment_service = CompanyEnrichmentService()
            pdf_generator = PDFGenerator()
            email_service = EmailService()
            
            enriched_data = enrichment_service.enrich_company(
                data['companyName'],
                data.get('website')
            )
            
            pdf_buffer = io.BytesIO()
            try:
                pdf_filename, pdf_buffer = pdf_generator.generate_report_in_memory(data, enriched_data)
                pdf_buffer.seek(0)
            except Exception as e:
                print(f"PDF generation failed: {e}")
                pdf_buffer = None
            
            email_sent = email_service.send_report_email_with_buffer(
                data['email'],
                data['fullName'],
                enriched_data.get('name', data['companyName']),
                pdf_buffer,
                pdf_filename
            )
            
            status = "Sent" if email_sent else "Generated (Email not configured)"
            
        except Exception as e:
            print(f"Processing error: {e}")
            status = "Generated (Processing failed)"
        
        return json.dumps({
            'status': 'success',
            'message': 'Lead submitted successfully. Report will be sent to your email shortly.',
            'leadId': lead_id
        }), 202, response_headers
    
    static_files = {
        '/static/style.css': ('text/css', 'static/style.css'),
        '/static/script.js': ('application/javascript', 'static/script.js'),
    }
    
    if path in static_files:
        mime, filepath = static_files[path]
        try:
            with open(filepath, 'r') as f:
                content = f.read()
            return content, 200, {**cors_headers, 'Content-Type': mime}
        except:
            return 'Not found', 404, response_headers
    
    return json.dumps({'error': 'Not found'}), 404, response_headers