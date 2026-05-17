# LeadFlow Pro - Automated Lead Enrichment System

A complete automation system that captures leads from a web form, enriches company data, generates personalized PDF reports, and delivers them via email.

## Features

- **Lead Intake Form**: Professional web form with validation
- **Company Data Enrichment**: Automatic company research using Clearbit API and web scraping
- **PDF Report Generation**: Branded, personalized business audit documents
- **Email Delivery**: Automatic email delivery with PDF attachment
- **Google Sheets Integration** (Bonus): Logs leads to a spreadsheet
- **Google Drive Integration** (Bonus): Archives generated PDFs

## Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

## Installation

1. **Clone or extract the project**:
   ```bash
   cd simplifiq_assessment
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On macOS/Linux
   # or
   venv\Scripts\activate     # On Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

### Basic Setup (No API Keys Required)

The system works with basic configuration. Data enrichment will use fallback logic.

### Email Configuration (Optional for Testing)

Create a `.env` file in the project root with your SMTP settings:

```env
# Email (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=your-email@gmail.com
SMTP_FROM_NAME=LeadFlow Pro
```

**Note**: For Gmail, use an [App Password](https://support.google.com/accounts/answer/185833).

### Clearbit API (Optional for Enhanced Enrichment)

```env
CLEARBIT_API_KEY=your_clearbit_api_key
```

### Google Sheets Integration (Bonus)

1. Create a Google Cloud project and enable the Sheets API
2. Create a service account and download credentials as `credentials.json`
3. Create a Google Sheet and share edit access with the service account email

```env
GOOGLE_SHEETS_ENABLED=true
GOOGLE_SHEETS_SPREADSHEET_ID=your_spreadsheet_id
```

### Google Drive Integration (Bonus)

```env
GOOGLE_DRIVE_ENABLED=true
GOOGLE_DRIVE_FOLDER_ID=your_drive_folder_id
```

## Running the Application

```bash
python app.py
```

The server will start at `http://localhost:5001` (port 5000 is often used by macOS AirPlay).

## Testing the Workflow

1. Open your browser to `http://localhost:5000`
2. Fill out the lead intake form with test data:
   - **Full Name**: John Doe
   - **Work Email**: john@example.com (use a real email to test delivery)
   - **Company Name**: Example Corp
   - **Website**: example.com (optional)
   - **Industry**: Technology
   - **Company Size**: 11-50

3. Submit the form
4. Check your email for the generated report

## API Endpoints

### POST /api/leads
Submit a new lead and trigger the automation workflow.

**Request**:
```json
{
  "fullName": "John Doe",
  "email": "john@company.com",
  "companyName": "Acme Corp",
  "website": "acme.com",
  "industry": "Technology",
  "companySize": "11-50",
  "notes": "Interested in optimization"
}
```

**Response** (202 Accepted):
```json
{
  "status": "success",
  "message": "Lead submitted successfully. Report will be sent to your email shortly.",
  "leadId": "uuid-here"
}
```

### GET /api/health
Health check endpoint.

## Project Structure

```
simplifiq_assessment/
├── app.py                 # Flask application
├── config.py              # Configuration
├── requirements.txt       # Dependencies
├── services/
│   ├── enrichment.py      # Company data enrichment
│   ├── pdf_generator.py  # PDF report generation
│   ├── email_service.py  # Email delivery
│   ├── sheets_service.py # Google Sheets (bonus)
│   └── drive_service.py  # Google Drive (bonus)
├── templates/
│   └── index.html         # Frontend form
├── static/
│   ├── style.css          # Styling
│   └── script.js          # Frontend logic
└── reports/               # Generated PDFs
```

## Assumptions & Limitations

1. **Data Enrichment**: Without Clearbit API, enrichment uses basic info and website scraping
2. **Email**: Without SMTP credentials, emails won't send but PDFs are still generated
3. **Google APIs**: Without credentials, bonus features are skipped gracefully
4. **PDF Storage**: Generated PDFs are stored locally in `reports/` folder
5. **Validation**: Basic field validation is implemented client-side and server-side

## Security Considerations

- Input sanitization on all form fields
- No sensitive data stored in code (uses environment variables)
- Error handling with graceful degradation

## Troubleshooting

### Email not sending
- Check SMTP credentials in `.env`
- For Gmail, ensure App Password is used (not regular password)
- Check spam folder

### Enrichment not working
- Clearbit API key may be invalid or rate-limited
- Website scraping may be blocked by some sites

### Google Sheets/Drive not working
- Verify credentials.json exists and is valid
- Check API is enabled in Google Cloud Console
- Ensure proper permissions on shared resources