# Lead Automation System - Technical Specification

## Project Overview
- **Project Name**: LeadFlow Pro - Automated Lead Enrichment & Report System
- **Type**: Full-stack web application (Python Flask + HTML/CSS/JS)
- **Core Functionality**: Automated workflow that captures leads from web forms, enriches company data, generates personalized PDF reports, and delivers via email
- **Target Users**: Sales teams, business development professionals in B2B sectors

---

## Architecture

### Components
1. **Frontend**: HTML/CSS/JS lead intake form
2. **Backend**: Python Flask REST API
3. **Enrichment Service**: Company data enrichment using multiple sources
4. **PDF Generator**: Personalized audit report creation
5. **Email Service**: SMTP-based report delivery
6. **Google Sheets Integration**: Lead logging (bonus)
7. **Google Drive Integration**: PDF archival (bonus)

### Flow
```
Lead Form Submit → Backend API → Data Enrichment → PDF Generation → Email Delivery
                                          ↓
                                   Google Sheets (log)
                                   Google Drive (archive)
```

---

## UI/UX Specification

### Layout Structure
- **Header**: Fixed top navigation with logo and contact
- **Hero Section**: Value proposition and CTA
- **Lead Form Section**: Multi-field intake form
- **Features Section**: 3-column grid showing system capabilities
- **Footer**: Minimal footer with copyright

### Responsive Breakpoints
- Mobile: < 768px (single column)
- Tablet: 768px - 1024px (adjusted spacing)
- Desktop: > 1024px (full layout)

### Visual Design
- **Primary Color**: #0F172A (Deep navy)
- **Secondary Color**: #3B82F6 (Bright blue)
- **Accent Color**: #10B981 (Emerald green)
- **Background**: #F8FAFC (Light gray)
- **Text Primary**: #1E293B
- **Text Secondary**: #64748B
- **Card Background**: #FFFFFF

### Typography
- **Headings**: "Sora", sans-serif (Google Fonts)
- **Body**: "Inter", sans-serif (Google Fonts)
- **H1**: 48px, font-weight 700
- **H2**: 32px, font-weight 600
- **H3**: 24px, font-weight 600
- **Body**: 16px, font-weight 400

### Components
- **Form Input**: 48px height, 16px padding, 8px border-radius, 2px border (#E2E8F0), focus: 2px solid #3B82F6
- **Primary Button**: Background #3B82F6, text white, 48px height, 24px horizontal padding, 8px border-radius, hover: #2563EB
- **Secondary Button**: Background #10B981, text white, same dimensions
- **Success Message**: Green background (#D1FAE5), green text (#065F46), 16px padding, 8px border-radius
- **Error Message**: Red background (#FEE2E2), red text (#991B1B), same dimensions

### Animations
- Button hover: 0.2s ease transition
- Form submit: Fade in success/error message (0.3s)
- Card hover: Subtle lift with box-shadow (0.1s)

---

## Functionality Specification

### 1. Lead Intake Form
**Fields**:
- Full Name (required, text)
- Work Email (required, email validation)
- Company Name (required, text)
- Company Website (optional, URL validation)
- Industry (dropdown: Finance, Consulting, SaaS, Healthcare, Manufacturing, Retail, Technology, Other)
- Company Size (dropdown: 1-10, 11-50, 51-200, 201-500, 500+)
- Additional Notes (optional, textarea)

**Validation**:
- Email format validation via regex
- Required field validation
- Website URL format validation (if provided)

### 2. Data Enrichment Service
**Data Sources** (in priority order):
1. Clearbit API (company enrichment)
2. Website scraping (if website provided)
3. Fallback to basic info from form input

**Enriched Data Points**:
- Company name
- Company domain
- Industry
- Company size
- Location (city, country)
- Company description
- Social profiles (LinkedIn, Twitter)
- Logo URL
- Employee count range

**Fallback Strategy**:
- If API fails: Use form-provided data with manual research prompts
- If website scraping fails: Log warning, continue with available data

### 3. PDF Report Generation
**Report Sections**:
1. **Cover Page**: Company logo, report title, date, "Prepared for [Company Name]"
2. **Executive Summary**: 2-3 sentence overview of company position
3. **Company Profile**: Basic information, industry analysis
4. **Market Insights**: Industry trends, competitive landscape notes
5. **Tailored Recommendations**: 3-4 specific suggestions based on industry
6. **Next Steps**: Call-to-action with contact information

**Design**:
- A4 format (210mm x 297mm)
- Professional typography (Helvetica/Arial)
- Color scheme matching brand
- Company logo placement
- Page numbers
- Branded footer

### 4. Email Service
**Email Fields**:
- From: Configurable SMTP (default: system email)
- To: Prospect's work email
- Subject: "Your Personalized [Company Name] Business Audit Report"
- Body: HTML formatted with system branding

**Email Content**:
- Personalized greeting
- Brief summary of what report contains
- Call-to-action button linking to report (or attach PDF)
- Professional signature

### 5. Google Sheets Integration (Bonus)
**Spreadsheet Columns**:
- Timestamp (ISO format)
- Full Name
- Email
- Company Name
- Industry
- Company Size
- Website
- Report Status (Generated/Sent/Failed)
- Notes

**Implementation**: Google Sheets API v4 with service account authentication

### 6. Google Drive Integration (Bonus)
**Behavior**:
- Create folder "Lead Reports" if not exists
- Save PDF with naming convention: `[CompanyName]_[Date]_AuditReport.pdf`
- Share with service account

**Implementation**: Google Drive API v3 with service account authentication

---

## Technical Stack

### Backend
- Python 3.10+
- Flask 2.3+
- Flask-CORS
- Requests (HTTP calls)
- ReportLab (PDF generation)
- Google APIs (Sheets, Drive)

### Frontend
- HTML5
- CSS3 (custom + minimal framework)
- Vanilla JavaScript (fetch API)

### Configuration
- All config via config.py (no hardcoding)
- Environment variables for sensitive data

---

## API Endpoints

### POST /api/leads
Submit new lead and trigger automation workflow.

**Request Body**:
```json
{
  "fullName": "string",
  "email": "string",
  "companyName": "string",
  "website": "string (optional)",
  "industry": "string",
  "companySize": "string",
  "notes": "string (optional)"
}
```

**Response (202 Accepted)**:
```json
{
  "status": "success",
  "message": "Lead submitted successfully. Report will be sent to your email.",
  "leadId": "uuid"
}
```

### GET /api/health
Health check endpoint.

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "ISO timestamp"
}
```

---

## Error Handling

### Form Validation Errors
- Return 400 with specific field errors
- Show inline error messages on form

### API/Enrichment Errors
- Log error but continue with available data
- Generate report with partial data
- Mark status as "partial" in logs

### Email Failures
- Retry up to 3 times with exponential backoff
- Log failure and alert (console log for prototype)
- Mark as "failed" in tracking

### PDF Generation Failures
- Return 500 with error message
- Log full error for debugging

---

## File Structure
```
/simplifiq_assessment
├── app.py                 # Flask application
├── config.py              # Configuration management
├── requirements.txt      # Python dependencies
├── services/
│   ├── enrichment.py     # Company data enrichment
│   ├── pdf_generator.py  # PDF report creation
│   ├── email_service.py  # Email delivery
│   ├── sheets_service.py # Google Sheets (bonus)
│   └── drive_service.py  # Google Drive (bonus)
├── templates/
│   └── index.html        # Frontend form
├── static/
│   ├── style.css         # Styling
│   └── script.js         # Frontend logic
├── reports/             # Generated PDFs (temp)
└── README.md            # Setup instructions
```

---

## Acceptance Criteria

### Must Pass
1. [ ] Lead form submits and returns success response
2. [ ] Data enrichment attempts to fetch company info
3. [ ] PDF report generates with company-specific content
4. [ ] Email sends with PDF attachment
5. [ ] End-to-end flow completes without errors

### Should Pass
6. [ ] Form validation prevents invalid submissions
7. [ ] Graceful degradation when enrichment fails
8. [ ] Responsive design works on mobile
9. [ ] Code is well-structured and documented

### Bonus
10. [ ] Google Sheets logs new leads
11. [ ] Google Drive archives generated PDFs

---

## Security Considerations
- No credentials in code (use environment variables)
- Input sanitization on all form fields
- Rate limiting on API endpoints (basic)
- HTTPS in production (not for prototype)

---

## Assumptions
- Development environment with Python 3.10+
- Internet access for API calls and scraping
- Valid SMTP credentials for email (or use Mailtrap for testing)
- Google Cloud credentials for bonus features (optional)