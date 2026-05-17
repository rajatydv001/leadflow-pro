import os
import re
import uuid
import threading
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from datetime import datetime

from api.config import Config
from api.services.enrichment import CompanyEnrichmentService
from api.services.pdf_generator import PDFGenerator
from api.services.email_service import EmailService
from api.services.sheets_service import SheetsService
from api.services.drive_service import DriveService

app = Flask(__name__)
CORS(app)

enrichment_service = CompanyEnrichmentService()
pdf_generator = PDFGenerator()
email_service = EmailService()
sheets_service = SheetsService()
drive_service = DriveService()


def validate_lead_data(data):
    errors = {}

    if not data.get('fullName') or not data.get('fullName').strip():
        errors['fullName'] = 'Full name is required'

    if not data.get('email') or not data.get('email').strip():
        errors['email'] = 'Email is required'
    elif not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', data['email']):
        errors['email'] = 'Invalid email format'

    if not data.get('companyName') or not data.get('companyName').strip():
        errors['companyName'] = 'Company name is required'

    website = data.get('website', '').strip()
    if website and not re.match(r'^(https?://)?([\da-z\.-]+)\.([a-z\.]{2,6})([/\w \.-]*)*\/?$', website, re.IGNORECASE):
        errors['website'] = 'Invalid website URL'

    valid_industries = ['Finance', 'Consulting', 'SaaS', 'Healthcare', 'Manufacturing', 'Retail', 'Technology', 'Other']
    if data.get('industry') and data['industry'] not in valid_industries:
        errors['industry'] = 'Invalid industry selection'

    valid_sizes = ['1-10', '11-50', '51-200', '201-500', '500+']
    if data.get('companySize') and data['companySize'] not in valid_sizes:
        errors['companySize'] = 'Invalid company size selection'

    return errors


def process_lead_async(lead_data):
    try:
        print(f"Processing lead: {lead_data.get('email')}")

        enriched_data = enrichment_service.enrich_company(
            lead_data['companyName'],
            lead_data.get('website')
        )

        print(f"Enriched data sources: {enriched_data.get('sources', [])}")

        pdf_path, filename = pdf_generator.generate_report(lead_data, enriched_data)
        print(f"PDF generated: {filename}")

        if Config.GOOGLE_SHEETS_ENABLED:
            sheets_service.append_lead(lead_data, "Generated")

        if Config.GOOGLE_DRIVE_ENABLED:
            drive_result = drive_service.upload_pdf(pdf_path, enriched_data.get('name', lead_data['companyName']))
            if drive_result:
                print(f"PDF archived to Drive: {drive_result.get('web_view_link')}")

        email_sent = email_service.send_report_email(
            lead_data['email'],
            lead_data['fullName'],
            enriched_data.get('name', lead_data['companyName']),
            pdf_path
        )

        if email_sent:
            status = "Sent"
        else:
            status = "Generated (Email failed)"

        if Config.GOOGLE_SHEETS_ENABLED:
            sheets_service.update_lead_status(lead_data['email'], status)

        print(f"Lead processing completed: {status}")

    except Exception as e:
        print(f"Error processing lead: {e}")
        if Config.GOOGLE_SHEETS_ENABLED:
            sheets_service.append_lead(lead_data, "Failed")


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'services': {
            'sheets_enabled': Config.GOOGLE_SHEETS_ENABLED,
            'drive_enabled': Config.GOOGLE_DRIVE_ENABLED
        }
    })


@app.route('/api/leads', methods=['POST'])
def submit_lead():
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No data provided'
            }), 400

        validation_errors = validate_lead_data(data)

        if validation_errors:
            return jsonify({
                'status': 'error',
                'message': 'Validation failed',
                'errors': validation_errors
            }), 400

        lead_id = str(uuid.uuid4())

        thread = threading.Thread(target=process_lead_async, args=(data,))
        thread.daemon = True
        thread.start()

        return jsonify({
            'status': 'success',
            'message': 'Lead submitted successfully. Report will be sent to your email shortly.',
            'leadId': lead_id
        }), 202

    except Exception as e:
        print(f"Error submitting lead: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Internal server error'
        }), 500


if __name__ == '__main__':
    app.run(
        host=Config.FLASK_HOST,
        port=Config.FLASK_PORT,
        debug=Config.FLASK_DEBUG
    )