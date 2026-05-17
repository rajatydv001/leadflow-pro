import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from api.config import Config


class EmailService:
    def __init__(self):
        self.smtp_host = Config.SMTP_HOST
        self.smtp_port = Config.SMTP_PORT
        self.username = Config.SMTP_USERNAME
        self.password = Config.SMTP_PASSWORD
        self.from_email = Config.SMTP_FROM_EMAIL or Config.SMTP_USERNAME
        self.from_name = Config.SMTP_FROM_NAME

    def send_report_email(self, recipient_email, recipient_name, company_name, pdf_path):
        if not self.username or not self.password:
            print("SMTP credentials not configured. Email not sent.")
            print(f"Would have sent email to: {recipient_email}")
            return False

        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = recipient_email
            msg['Subject'] = f"Your Personalized {company_name} Business Audit Report"

            html_content = self._get_html_email_template(recipient_name, company_name)
            text_content = self._get_text_email_template(recipient_name, company_name)

            msg.attach(MIMEText(text_content, 'plain'))
            msg.attach(MIMEText(html_content, 'html'))

            if os.path.exists(pdf_path):
                self._attach_pdf(msg, pdf_path, company_name)

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)

            print(f"Email sent successfully to {recipient_email}")
            return True

        except Exception as e:
            print(f"Error sending email: {e}")
            return False

    def send_report_email_with_buffer(self, recipient_email, recipient_name, company_name, pdf_buffer, pdf_filename):
        if not self.username or not self.password:
            print("SMTP credentials not configured. Email not sent.")
            print(f"Would have sent email to: {recipient_email}")
            return False

        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = recipient_email
            msg['Subject'] = f"Your Personalized {company_name} Business Audit Report"

            html_content = self._get_html_email_template(recipient_name, company_name)
            text_content = self._get_text_email_template(recipient_name, company_name)

            msg.attach(MIMEText(text_content, 'plain'))
            msg.attach(MIMEText(html_content, 'html'))

            if pdf_buffer:
                self._attach_pdf_from_buffer(msg, pdf_buffer, pdf_filename, company_name)

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)

            print(f"Email sent successfully to {recipient_email}")
            return True

        except Exception as e:
            print(f"Error sending email: {e}")
            return False

    def _attach_pdf_from_buffer(self, msg, pdf_buffer, filename, company_name):
        try:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(pdf_buffer.read())
            encoders.encode_base64(part)
            filename_clean = f"{company_name.replace(' ', '_')}_Business_Audit_Report.pdf"
            part.add_header('Content-Disposition', f'attachment; filename= {filename_clean}')
            msg.attach(part)
            print(f"PDF attached: {filename_clean}")
        except Exception as e:
            print(f"Error attaching PDF: {e}")

    def _attach_pdf(self, msg, pdf_path, company_name):
        try:
            with open(pdf_path, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            encoders.encode_base64(part)
            filename = f"{company_name.replace(' ', '_')}_Business_Audit_Report.pdf"
            part.add_header('Content-Disposition', f'attachment; filename= {filename}')
            msg.attach(part)
            print(f"PDF attached: {filename}")
        except Exception as e:
            print(f"Error attaching PDF: {e}")

    def _get_html_email_template(self, recipient_name, company_name):
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f8fafc;">
            <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f8fafc; padding: 40px 20px;">
                <tr>
                    <td align="center">
                        <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.07);">
                            <tr>
                                <td style="background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%); padding: 30px 40px; text-align: center;">
                                    <h1 style="color: #ffffff; margin: 0; font-size: 28px; font-weight: 600;">
                                        <span style="font-weight: 400;">LeadFlow</span><span style="color: #3B82F6;">Pro</span>
                                    </h1>
                                    <p style="color: #94a3b8; margin: 10px 0 0 0; font-size: 14px;">Automated Business Intelligence</p>
                                </td>
                            </tr>
                            <tr>
                                <td style="padding: 40px;">
                                    <h2 style="color: #0F172A; margin: 0 0 20px 0; font-size: 24px;">Your Business Audit Report</h2>
                                    <p style="color: #64748b; font-size: 16px; line-height: 1.6; margin: 0 0 20px 0;">
                                        Dear <strong>{recipient_name}</strong>,
                                    </p>
                                    <p style="color: #64748b; font-size: 16px; line-height: 1.6; margin: 0 0 30px 0;">
                                        Thank you for your interest in <strong>{company_name}</strong>. We have prepared a personalized business audit report with industry insights and tailored recommendations.
                                    </p>
                                    <p style="color: #94a3b8; font-size: 14px; margin: 30px 0 0 0;">
                                        Have questions? Reply to this email or contact our team.
                                    </p>
                                </td>
                            </tr>
                            <tr>
                                <td style="background-color: #f1f5f9; padding: 20px 40px; text-align: center;">
                                    <p style="color: #94a3b8; font-size: 12px; margin: 0;">
                                        &copy; 2026 LeadFlow Pro. All rights reserved.
                                    </p>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """

    def _get_text_email_template(self, recipient_name, company_name):
        return f"""
Dear {recipient_name},

Thank you for your interest in {company_name}. We have prepared a personalized business audit report with industry insights and tailored recommendations.

Please find the report attached. If you have any questions, feel free to reply to this email.

Best regards,
LeadFlow Pro Analytics Team
        """