import os
from dotenv import load_dotenv

load_dotenv()


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
            'trends': [
                'Digital transformation accelerating in banking sector',
                'AI and machine learning adoption for fraud detection',
                'Open banking regulations driving API adoption',
                'Blockchain adoption for cross-border payments'
            ],
            'recommendations': [
                'Implement AI-powered customer service chatbots',
                'Develop open banking API integration capabilities',
                'Enhance cybersecurity infrastructure',
                'Create mobile-first digital banking experiences'
            ]
        },
        'Consulting': {
            'trends': [
                'Remote consulting delivery gaining traction',
                'Specialization in digital transformation',
                'Data-driven decision making becoming standard',
                'Sustainability and ESG consulting demand surge'
            ],
            'recommendations': [
                'Build specialized digital transformation practice',
                'Invest in data analytics and visualization tools',
                'Develop remote delivery capabilities',
                'Create thought leadership content strategy'
            ]
        },
        'SaaS': {
            'trends': [
                'Product-led growth becoming dominant model',
                'Usage-based pricing gaining popularity',
                'Customer success becoming competitive differentiator',
                'Integration ecosystem expansion'
            ],
            'recommendations': [
                'Implement free trial and freemium models',
                'Build robust integration with popular tools',
                'Develop comprehensive customer success program',
                'Create product usage analytics dashboard'
            ]
        },
        'Healthcare': {
            'trends': [
                'Telehealth adoption continuing post-pandemic',
                'AI-assisted diagnostics becoming mainstream',
                'Data privacy and HIPAA compliance focus',
                'Interoperability standards gaining traction'
            ],
            'recommendations': [
                'Implement HIPAA-compliant telehealth platform',
                'Develop AI-powered diagnostic assistance tools',
                'Build patient data interoperability features',
                'Create secure messaging and collaboration tools'
            ]
        },
        'Manufacturing': {
            'trends': [
                'Industry 4.0 and smart factory adoption',
                'IoT and sensor technology integration',
                'Predictive maintenance becoming essential',
                'Supply chain digitalization'
            ],
            'recommendations': [
                'Implement IoT sensor network for monitoring',
                'Deploy predictive maintenance analytics',
                'Build supply chain visibility dashboard',
                'Create digital twin simulation capabilities'
            ]
        },
        'Retail': {
            'trends': [
                'Omnichannel commerce integration',
                'Personalization through AI/ML',
                'Social commerce and influencer marketing',
                'Inventory optimization with predictive analytics'
            ],
            'recommendations': [
                'Build unified commerce platform',
                'Implement AI-powered personalization engine',
                'Develop social commerce integration',
                'Create real-time inventory management system'
            ]
        },
        'Technology': {
            'trends': [
                'Cloud-native architecture adoption',
                'DevOps and CI/CD maturity',
                'Security-first development practices',
                'Remote and distributed team management'
            ],
            'recommendations': [
                'Migrate to cloud-native infrastructure',
                'Implement comprehensive DevOps practices',
                'Build security-first development culture',
                'Create distributed team collaboration tools'
            ]
        },
        'Other': {
            'trends': [
                'Digital transformation across all sectors',
                'Data-driven decision making adoption',
                'Remote work enablement',
                'Customer experience focus'
            ],
            'recommendations': [
                'Assess digital maturity and create roadmap',
                'Implement data analytics capabilities',
                'Build remote work infrastructure',
                'Create customer feedback and NPS systems'
            ]
        }
    }