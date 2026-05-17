import os
import uuid
import io
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from api.config import Config


class PDFGenerator:
    def __init__(self):
        self.output_dir = '/tmp/reports'
        try:
            os.makedirs(self.output_dir, exist_ok=True)
        except:
            pass
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=28,
            textColor=colors.Color(0.06, 0.09, 0.16),
            spaceAfter=20,
            alignment=TA_CENTER
        )

        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.Color(0.06, 0.09, 0.16),
            spaceAfter=12,
            spaceBefore=20
        )

        self.subheading_style = ParagraphStyle(
            'CustomSubheading',
            parent=self.styles['Heading3'],
            fontSize=13,
            textColor=colors.Color(0.23, 0.29, 0.36),
            spaceAfter=8,
            spaceBefore=12
        )

        self.body_style = ParagraphStyle(
            'CustomBody',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.Color(0.23, 0.29, 0.36),
            spaceAfter=10,
            alignment=TA_JUSTIFY,
            leading=16
        )

        self.caption_style = ParagraphStyle(
            'Caption',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.Color(0.5, 0.5, 0.5),
            spaceAfter=5
        )

    def generate_report(self, lead_data, enriched_data):
        filename = f"{enriched_data.get('name', lead_data['companyName']).replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}_{str(uuid.uuid4())[:8]}.pdf"
        
        try:
            filepath = os.path.join(self.output_dir, filename)
            return self._build_pdf(filepath, lead_data, enriched_data, filename)
        except:
            buffer, fn = self.generate_report_in_memory(lead_data, enriched_data)
            return fn, buffer

    def generate_report_in_memory(self, lead_data, enriched_data):
        filename = f"{enriched_data.get('name', lead_data['companyName']).replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}_{str(uuid.uuid4())[:8]}.pdf"
        
        buffer = io.BytesIO()
        self._build_pdf(buffer, lead_data, enriched_data, filename)
        buffer.seek(0)
        
        return filename, buffer

    def _build_pdf(self, output, lead_data, enriched_data, filename):
        if isinstance(output, str):
            doc = SimpleDocTemplate(
                output,
                pagesize=A4,
                rightMargin=50,
                leftMargin=50,
                topMargin=50,
                bottomMargin=50
            )
        else:
            doc = SimpleDocTemplate(
                output,
                pagesize=A4,
                rightMargin=50,
                leftMargin=50,
                topMargin=50,
                bottomMargin=50
            )

        story = []
        story.extend(self._create_cover_page(lead_data, enriched_data))
        story.append(PageBreak())
        story.extend(self._create_executive_summary(lead_data, enriched_data))
        story.extend(self._create_company_profile(lead_data, enriched_data))
        story.extend(self._create_market_insights(enriched_data.get('industry', 'Other')))
        story.extend(self._create_recommendations(enriched_data.get('industry', 'Other')))
        story.extend(self._create_next_steps(lead_data))
        story.append(PageBreak())
        story.extend(self._create_footer())

        doc.build(story)
        
        if isinstance(output, io.BytesIO):
            return filename, output
        return output, filename

    def _create_cover_page(self, lead_data, enriched_data):
        elements = []
        elements.append(Spacer(1, 80))
        logo_text = Paragraph(
            "<b>LeadFlow</b> <span color='#3B82F6'>Pro</span>",
            ParagraphStyle('Logo', fontSize=24, textColor=colors.Color(0.06, 0.09, 0.16), alignment=TA_CENTER)
        )
        elements.append(logo_text)
        elements.append(Spacer(1, 40))
        company_name = enriched_data.get('name', lead_data['companyName'])
        report_title = Paragraph("Business Audit Report", self.title_style)
        elements.append(report_title)
        elements.append(Spacer(1, 30))
        subtitle = Paragraph(
            f"Prepared for <b>{company_name}</b>",
            ParagraphStyle('Subtitle', fontSize=16, textColor=colors.Color(0.4, 0.4, 0.4), alignment=TA_CENTER, spaceAfter=10)
        )
        elements.append(subtitle)
        date_text = Paragraph(
            datetime.now().strftime('%B %d, %Y'),
            ParagraphStyle('Date', fontSize=12, textColor=colors.Color(0.5, 0.5, 0.5), alignment=TA_CENTER, spaceAfter=40)
        )
        elements.append(date_text)
        contact_box = Table(
            [[Paragraph("<b>Prepared by:</b><br/>LeadFlow Pro Analytics", self.body_style)]],
            colWidths=[250], hAlign='CENTER'
        )
        contact_box.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.Color(0.9, 0.9, 0.9)),
            ('BACKGROUND', (0, 0), (-1, -1), colors.Color(0.98, 0.98, 0.99)),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 20),
            ('RIGHTPADDING', (0, 0), (-1, -1), 20),
            ('TOPPADDING', (0, 0), (-1, -1), 15),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
        ]))
        elements.append(contact_box)
        return elements

    def _create_executive_summary(self, lead_data, enriched_data):
        elements = []
        elements.append(Paragraph("Executive Summary", self.heading_style))
        company_name = enriched_data.get('name', lead_data['companyName'])
        industry = enriched_data.get('industry', 'Business')
        summary_text = f"This personalized business audit has been prepared for <b>{company_name}</b>, a {industry.lower()} company. Based on our analysis of your company's profile and industry positioning, we have identified key opportunities for operational improvement and strategic growth."
        elements.append(Paragraph(summary_text, self.body_style))
        elements.append(Spacer(1, 15))
        return elements

    def _create_company_profile(self, lead_data, enriched_data):
        elements = []
        elements.append(Paragraph("Company Profile", self.heading_style))
        company_name = enriched_data.get('name', lead_data['companyName'])
        profile_data = [
            ['Company Name:', enriched_data.get('name', lead_data['companyName'])],
            ['Industry:', enriched_data.get('industry', 'Not specified')],
            ['Company Size:', enriched_data.get('employee_count', lead_data.get('companySize', 'Not specified'))],
            ['Location:', enriched_data.get('location', 'Not specified')],
            ['Domain:', enriched_data.get('domain', 'Not available')],
        ]
        if enriched_data.get('description'):
            profile_data.append(['Description:', enriched_data['description'][:150] + '...'])
        profile_table = Table(profile_data, colWidths=[120, 280], hAlign='LEFT')
        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.Color(0.96, 0.96, 0.98)),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.Color(0.3, 0.3, 0.3)),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.Color(0.23, 0.29, 0.36)),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.Color(0.9, 0.9, 0.9)),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ])
        profile_table.setStyle(table_style)
        elements.append(profile_table)
        return elements

    def _create_market_insights(self, industry):
        from api.services.enrichment import get_industry_insights
        elements = []
        elements.append(Paragraph("Market Insights", self.heading_style))
        insights = get_industry_insights(industry)
        elements.append(Paragraph("Current Industry Trends:", self.subheading_style))
        for i, trend in enumerate(insights['trends'], 1):
            trend_text = f"<b>{i}.</b> {trend}"
            elements.append(Paragraph(trend_text, self.body_style))
        elements.append(Spacer(1, 10))
        return elements

    def _create_recommendations(self, industry):
        from api.services.enrichment import get_industry_insights
        elements = []
        elements.append(Paragraph("Tailored Recommendations", self.heading_style))
        insights = get_industry_insights(industry)
        elements.append(Paragraph("Strategic Initiatives for Your Business:", self.subheading_style))
        for i, rec in enumerate(insights['recommendations'], 1):
            rec_text = f"<b>Recommendation {i}:</b> {rec}"
            elements.append(Paragraph(rec_text, self.body_style))
            elements.append(Spacer(1, 8))
        return elements

    def _create_next_steps(self, lead_data):
        elements = []
        elements.append(Paragraph("Next Steps", self.heading_style))
        next_steps_text = "We believe these insights provide a strong foundation for your business growth. To discuss these findings in detail or explore how we can support your implementation, we invite you to schedule a consultation."
        elements.append(Paragraph(next_steps_text, self.body_style))
        elements.append(Spacer(1, 20))
        cta_text = "<b>Ready to take the next step?</b> Contact us to schedule a personalized strategy session."
        elements.append(Paragraph(cta_text, self.body_style))
        return elements

    def _create_footer(self):
        elements = []
        elements.append(Spacer(1, 30))
        disclaimer = "<i>Disclaimer: This report has been automatically generated based on publicly available information and industry trends.</i>"
        elements.append(Paragraph(disclaimer, ParagraphStyle('Disclaimer', fontSize=8, textColor=colors.Color(0.6, 0.6, 0.6), spaceAfter=20, alignment=TA_JUSTIFY)))
        footer_text = Paragraph("Generated by LeadFlow Pro | Automated Business Intelligence", self.caption_style)
        elements.append(footer_text)
        return elements