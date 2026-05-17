import os
import uuid
import io
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, PageBreakIfNotEmpty
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
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
        self._setup_fonts()
        self.page_count = 0

    def _setup_fonts(self):
        try:
            pdfmetrics.registerFont(TTFont('Inter', 'Inter-Regular.ttf'))
            pdfmetrics.registerFont(TTFont('Inter-Bold', 'Inter-Bold.ttf'))
        except:
            pass

    def _setup_custom_styles(self):
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=32,
            textColor=colors.Color(0.06, 0.09, 0.16),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )

        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=18,
            textColor=colors.Color(0.06, 0.09, 0.16),
            spaceAfter=15,
            spaceBefore=20,
            fontName='Helvetica-Bold'
        )

        self.subheading_style = ParagraphStyle(
            'CustomSubheading',
            parent=self.styles['Heading3'],
            fontSize=13,
            textColor=colors.Color(0.23, 0.29, 0.36),
            spaceAfter=8,
            spaceBefore=10,
            fontName='Helvetica-Bold'
        )

        self.body_style = ParagraphStyle(
            'CustomBody',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.Color(0.23, 0.29, 0.36),
            spaceAfter=12,
            alignment=TA_JUSTIFY,
            leading=18
        )

        self.caption_style = ParagraphStyle(
            'Caption',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.Color(0.5, 0.5, 0.5),
            spaceAfter=5,
            alignment=TA_CENTER
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
        self.page_count = 0
        
        if isinstance(output, str):
            doc = SimpleDocTemplate(
                output,
                pagesize=A4,
                rightMargin=50,
                leftMargin=50,
                topMargin=50,
                bottomMargin=50,
                onFirstPage=self._on_page,
                onLaterPages=self._on_page
            )
        else:
            doc = SimpleDocTemplate(
                output,
                pagesize=A4,
                rightMargin=50,
                leftMargin=50,
                topMargin=50,
                bottomMargin=50,
                onFirstPage=self._on_page,
                onLaterPages=self._on_page
            )

        story = []
        
        # Page 1: Cover Page
        story.extend(self._create_cover_page(lead_data, enriched_data))
        story.append(PageBreak())
        self.page_count += 1
        
        # Page 2: Executive Summary + Company Profile
        story.extend(self._create_executive_summary(lead_data, enriched_data))
        story.extend(self._create_company_profile(lead_data, enriched_data))
        story.append(PageBreak())
        self.page_count += 1
        
        # Page 3: Market Insights
        story.extend(self._create_market_insights(enriched_data.get('industry', 'Other')))
        story.append(PageBreak())
        self.page_count += 1
        
        # Page 4: Recommendations + Next Steps
        story.extend(self._create_recommendations(enriched_data.get('industry', 'Other')))
        story.extend(self._create_next_steps(lead_data))
        story.append(PageBreak())
        self.page_count += 1
        
        # Page 5: Footer
        story.extend(self._create_footer())
        
        doc.build(story)
        
        if isinstance(output, io.BytesIO):
            return filename, output
        return output, filename

    def _on_page(self, canvas, doc):
        canvas.saveState()
        self.page_count += 1
        canvas.setFont('Helvetica', 9)
        canvas.setFillColor(colors.Color(0.5, 0.5, 0.5))
        footer_text = f"Page {self.page_count} | Generated by LeadFlow Pro | Automated Business Intelligence"
        canvas.drawCentredString(297.5, 20, footer_text)
        
        canvas.setStrokeColor(colors.Color(0.9, 0.9, 0.9))
        canvas.line(50, 30, 545, 30)
        canvas.restoreState()

    def _create_cover_page(self, lead_data, enriched_data):
        elements = []
        
        # Company Name as main title
        company_name = enriched_data.get('name', lead_data['companyName'])
        if company_name:
            company_title = Paragraph(
                company_name.upper(),
                ParagraphStyle(
                    'CompanyTitle',
                    fontSize=36,
                    textColor=colors.Color(0.06, 0.09, 0.16),
                    alignment=TA_CENTER,
                    spaceAfter=40,
                    fontName='Helvetica-Bold'
                )
            )
            elements.append(company_title)
        
        # Report Title
        report_title = Paragraph(
            "Business Audit Report",
            ParagraphStyle(
                'ReportTitle',
                fontSize=28,
                textColor=colors.Color(0.23, 0.29, 0.36),
                alignment=TA_CENTER,
                spaceAfter=50,
                fontName='Helvetica'
            )
        )
        elements.append(report_title)
        
        # Prepared for
        subtitle = Paragraph(
            f"Prepared for <b>{company_name}</b>",
            ParagraphStyle(
                'Subtitle',
                fontSize=16,
                textColor=colors.Color(0.4, 0.4, 0.4),
                alignment=TA_CENTER,
                spaceAfter=30
            )
        )
        elements.append(subtitle)
        
        # Date
        date_text = Paragraph(
            datetime.now().strftime('%B %d, %Y'),
            ParagraphStyle(
                'Date',
                fontSize=14,
                textColor=colors.Color(0.5, 0.5, 0.5),
                alignment=TA_CENTER,
                spaceAfter=50
            )
        )
        elements.append(date_text)
        
        # Prepared by box
        elements.append(Spacer(1, 30))
        
        contact_box = Table(
            [[Paragraph("<b>Prepared by:</b><br/>LeadFlow Pro Analytics<br/><i>Automated Business Intelligence</i>", self.body_style)]],
            colWidths=[280],
            hAlign='CENTER'
        )
        contact_box.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 2, colors.Color(0.06, 0.09, 0.16)),
            ('BACKGROUND', (0, 0), (-1, -1), colors.Color(0.98, 0.98, 0.99)),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 30),
            ('RIGHTPADDING', (0, 0), (-1, -1), 30),
            ('TOPPADDING', (0, 0), (-1, -1), 25),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 25),
        ]))
        elements.append(contact_box)
        
        # Confidential note
        elements.append(Spacer(1, 50))
        confidential = Paragraph(
            "<i>This report is confidential and intended for the recipient only.</i>",
            ParagraphStyle(
                'Confidential',
                fontSize=10,
                textColor=colors.Color(0.6, 0.6, 0.6),
                alignment=TA_CENTER
            )
        )
        elements.append(confidential)
        
        return elements

    def _create_executive_summary(self, lead_data, enriched_data):
        elements = []
        elements.append(Paragraph("Executive Summary", self.heading_style))
        
        company_name = enriched_data.get('name', lead_data['companyName'])
        industry = enriched_data.get('industry', 'Business')
        location = enriched_data.get('location', '')
        
        summary_text = f"""
        This personalized business audit has been prepared for <b>{company_name}</b>, a leading company in the <b>{industry}</b> industry{', located in ' + location if location else ''}. 
        Based on our comprehensive analysis of your company's profile, market positioning, and industry trends, 
        we have identified key opportunities for operational improvement, strategic growth, and competitive advantage.
        This report provides actionable insights and tailored recommendations to help you leverage your strengths 
        and address potential challenges in the current business landscape.
        """
        
        elements.append(Paragraph(summary_text, self.body_style))
        elements.append(Spacer(1, 20))
        
        # Key highlights
        elements.append(Paragraph("Key Highlights:", self.subheading_style))
        
        highlights = [
            f"Industry: {industry} sector with significant growth potential",
            f"Company Size: {enriched_data.get('employee_count', lead_data.get('companySize', 'Not specified'))} employees",
            f"Location: {enriched_data.get('location', 'Not specified')}",
            f"Domain: {enriched_data.get('domain', 'Not available')}"
        ]
        
        for highlight in highlights:
            elements.append(Paragraph(f"• {highlight}", self.body_style))
        
        elements.append(Spacer(1, 20))
        return elements

    def _create_company_profile(self, lead_data, enriched_data):
        elements = []
        elements.append(Paragraph("Company Profile", self.heading_style))
        
        company_name = enriched_data.get('name', lead_data['companyName'])
        
        employee_count = enriched_data.get('employee_count', lead_data.get('companySize', 'Not specified'))
        if employee_count and employee_count != 'Not specified':
            if isinstance(employee_count, int):
                employee_count = f"{employee_count}+ employees"
            elif isinstance(employee_count, str) and employee_count.isdigit():
                employee_count = f"{employee_count}+ employees"
            elif employee_count == 'Not specified':
                employee_count = lead_data.get('companySize', 'Not specified')
        
        location_parts = []
        if enriched_data.get('city'):
            location_parts.append(enriched_data.get('city'))
        if enriched_data.get('country'):
            location_parts.append(enriched_data.get('country'))
        location = ', '.join(location_parts) if location_parts else 'Not specified'
        
        profile_data = [
            ['Company Name:', enriched_data.get('name', lead_data['companyName'])],
            ['Industry:', enriched_data.get('industry', 'Not specified')],
            ['Company Size:', str(employee_count)],
            ['Location:', location],
            ['Domain:', enriched_data.get('domain', 'Not available')],
        ]
        
        if enriched_data.get('founded'):
            profile_data.append(['Founded:', enriched_data.get('founded', '')])
        
        if enriched_data.get('phone'):
            profile_data.append(['Phone:', enriched_data.get('phone', '')])
        
        profile_table = Table(profile_data, colWidths=[130, 270], hAlign='LEFT')
        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.Color(0.96, 0.96, 0.98)),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.Color(0.3, 0.3, 0.3)),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.Color(0.23, 0.29, 0.36)),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.Color(0.9, 0.9, 0.9)),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ])
        profile_table.setStyle(table_style)
        elements.append(profile_table)
        
        # Full Description
        if enriched_data.get('description'):
            elements.append(Spacer(1, 20))
            elements.append(Paragraph("About the Company", self.subheading_style))
            description = enriched_data.get('description', '')
            if len(description) > 500:
                description = description[:500] + "..."
            elements.append(Paragraph(description, self.body_style))
        
        # Social Links
        if enriched_data.get('linkedin_url') or enriched_data.get('twitter_url'):
            elements.append(Spacer(1, 15))
            elements.append(Paragraph("Online Presence", self.subheading_style))
            
            if enriched_data.get('linkedin_url'):
                elements.append(Paragraph(f"LinkedIn: {enriched_data['linkedin_url']}", self.caption_style))
            if enriched_data.get('twitter_url'):
                elements.append(Paragraph(f"Twitter: {enriched_data['twitter_url']}", self.caption_style))
        
        return elements

    def _create_market_insights(self, industry):
        from api.services.enrichment import get_industry_insights
        
        elements = []
        elements.append(Paragraph("Market Insights", self.heading_style))
        
        # Industry Overview
        elements.append(Paragraph(f"Industry Overview: {industry}", self.subheading_style))
        
        industry_intro = {
            'Technology': "The technology sector continues to evolve rapidly with innovations in AI, cloud computing, and cybersecurity. Companies are increasingly focusing on digital transformation and automation to stay competitive.",
            'Finance': "The financial services industry is undergoing significant transformation with fintech innovations, blockchain adoption, and shifting regulatory requirements. Digital banking and personalized services are becoming the norm.",
            'Healthcare': "Healthcare is experiencing a shift towards telemedicine, AI-powered diagnostics, and patient-centric care models. Data security and interoperability remain critical priorities.",
            'Consulting': "The consulting industry is adapting to remote work trends, with firms specializing in digital transformation, sustainability, and data analytics. Client expectations for measurable outcomes are increasing.",
            'Retail': "Retail is evolving through omnichannel strategies, AI-powered personalization, and sustainability initiatives. E-commerce continues to grow while in-store experiences are being reimagined.",
            'Manufacturing': "Manufacturing is embracing Industry 4.0 with IoT, AI, and automation. Smart factories and supply chain digitalization are becoming essential for competitiveness.",
            'SaaS': "SaaS companies are focusing on product-led growth, customer success, and integration ecosystems. Usage-based pricing and freemium models are gaining traction.",
            'Other': "Businesses across all industries are increasingly focusing on digital transformation, customer experience, and operational efficiency to remain competitive."
        }
        
        intro = industry_intro.get(industry, industry_intro['Other'])
        elements.append(Paragraph(intro, self.body_style))
        
        elements.append(Spacer(1, 20))
        
        # Current Trends
        elements.append(Paragraph("Current Industry Trends:", self.subheading_style))
        
        insights = get_industry_insights(industry)
        
        for i, trend in enumerate(insights['trends'], 1):
            trend_text = f"<b>{i}.</b> {trend}"
            elements.append(Paragraph(trend_text, self.body_style))
        
        elements.append(Spacer(1, 15))
        
        return elements

    def _create_recommendations(self, industry):
        from api.services.enrichment import get_industry_insights
        
        elements = []
        elements.append(Paragraph("Tailored Recommendations", self.heading_style))
        
        elements.append(Paragraph("Strategic Initiatives for Your Business:", self.subheading_style))
        
        insights = get_industry_insights(industry)
        
        for i, rec in enumerate(insights['recommendations'], 1):
            rec_text = f"""
            <b>Recommendation {i}:</b> {rec}
            """
            elements.append(Paragraph(rec_text, self.body_style))
            elements.append(Spacer(1, 8))
        
        elements.append(Spacer(1, 20))
        
        return elements

    def _create_next_steps(self, lead_data):
        elements = []
        elements.append(Paragraph("Next Steps", self.heading_style))
        
        next_steps_text = """
        We believe these insights provide a strong foundation for your business growth and competitive positioning. 
        To discuss these findings in detail or explore how we can support your implementation, we invite you to 
        schedule a consultation with our team. We can help you prioritize these recommendations based on your 
        specific timeline, budget, and strategic objectives.
        """
        
        elements.append(Paragraph(next_steps_text, self.body_style))
        elements.append(Spacer(1, 25))
        
        cta_text = """
        <b>Ready to take the next step?</b><br/><br/>
        Contact us to schedule a personalized strategy session and receive a detailed implementation roadmap 
        tailored to your company's needs.
        """
        elements.append(Paragraph(cta_text, self.body_style))
        
        return elements

    def _create_footer(self):
        elements = []
        elements.append(Spacer(1, 50))
        
        disclaimer_title = Paragraph(
            "Disclaimer",
            ParagraphStyle(
                'DisclaimerTitle',
                fontSize=12,
                textColor=colors.Color(0.3, 0.3, 0.3),
                fontName='Helvetica-Bold',
                spaceAfter=10
            )
        )
        elements.append(disclaimer_title)
        
        disclaimer = """
        <i>This report has been automatically generated based on publicly available information and industry trends. 
        The insights provided are for informational purposes only and should not be considered as professional 
        business advice. Data accuracy depends on source availability. LeadFlow Pro does not guarantee the 
        accuracy or completeness of the information contained in this report.</i>
        """
        
        elements.append(Paragraph(disclaimer, ParagraphStyle(
            'Disclaimer',
            fontSize=9,
            textColor=colors.Color(0.5, 0.5, 0.5),
            spaceAfter=20,
            alignment=TA_JUSTIFY,
            leading=14
        )))
        
        elements.append(Spacer(1, 20))
        
        footer_text = Paragraph(
            "Generated by LeadFlow Pro | Automated Business Intelligence | © 2026",
            self.caption_style
        )
        elements.append(footer_text)
        
        return elements