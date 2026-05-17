import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    FLASK_PORT = int(os.getenv('FLASK_PORT', 5001))
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
    SMTP_FROM_EMAIL = os.getenv('SMTP_FROM_EMAIL', '')
    SMTP_FROM_NAME = os.getenv('SMTP_FROM_NAME', 'LeadFlow Pro')
    CLEARBIT_API_KEY = os.getenv('CLEARBIT_API_KEY', '')
    GOOGLE_SHEETS_ENABLED = os.getenv('GOOGLE_SHEETS_ENABLED', 'false').lower() == 'true'
    GOOGLE_SHEETS_SPREADSHEET_ID = os.getenv('GOOGLE_SHEETS_SPREADSHEET_ID', '')
    GOOGLE_DRIVE_ENABLED = os.getenv('GOOGLE_DRIVE_ENABLED', 'false').lower() == 'true'
    GOOGLE_DRIVE_FOLDER_ID = os.getenv('GOOGLE_DRIVE_FOLDER_ID', '')
    GOOGLE_CREDENTIALS_FILE = os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')
    REPORT_SENDER_NAME = os.getenv('REPORT_SENDER_NAME', 'LeadFlow Pro Analytics')
    REPORT_SENDER_TITLE = os.getenv('REPORT_SENDER_TITLE', 'Business Intelligence Team')

    INDUSTRY_INSIGHTS = {
        'Finance': {
            'trends': ['Digital transformation in banking', 'AI for fraud detection', 'Open banking regulations', 'Blockchain for payments'],
            'recommendations': ['AI-powered chatbots', 'Open banking APIs', 'Cybersecurity enhancement', 'Mobile-first banking']
        },
        'Consulting': {
            'trends': ['Remote consulting', 'Digital transformation specialization', 'Data-driven decisions', 'ESG consulting'],
            'recommendations': ['Digital practice', 'Analytics tools', 'Remote capabilities', 'Thought leadership']
        },
        'SaaS': {
            'trends': ['Product-led growth', 'Usage-based pricing', 'Customer success focus', 'Integration ecosystems'],
            'recommendations': ['Free trials', 'Integration APIs', 'Customer success programs', 'Usage analytics']
        },
        'Healthcare': {
            'trends': ['Telehealth adoption', 'AI diagnostics', 'HIPAA compliance', 'Interoperability'],
            'recommendations': ['Telehealth platform', 'AI diagnostics', 'Patient data interoperability', 'Secure messaging']
        },
        'Manufacturing': {
            'trends': ['Industry 4.0', 'IoT integration', 'Predictive maintenance', 'Supply chain digitalization'],
            'recommendations': ['IoT sensors', 'Predictive analytics', 'Supply chain visibility', 'Digital twins']
        },
        'Retail': {
            'trends': ['Omnichannel commerce', 'AI personalization', 'Social commerce', 'Inventory optimization'],
            'recommendations': ['Unified commerce', 'AI personalization', 'Social integration', 'Inventory management']
        },
        'Technology': {
            'trends': ['Cloud-native', 'DevOps maturity', 'Security-first', 'Distributed teams'],
            'recommendations': ['Cloud migration', 'DevOps practices', 'Security culture', 'Collaboration tools']
        },
        'Other': {
            'trends': ['Digital transformation', 'Data-driven decisions', 'Remote work', 'Customer experience'],
            'recommendations': ['Digital roadmap', 'Analytics capabilities', 'Remote infrastructure', 'NPS systems']
        }
    }