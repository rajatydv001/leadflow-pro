import os
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from config import Config


class SheetsService:
    def __init__(self):
        self.enabled = Config.GOOGLE_SHEETS_ENABLED
        self.spreadsheet_id = Config.GOOGLE_SHEETS_SPREADSHEET_ID
        self.credentials_file = Config.GOOGLE_CREDENTIALS_FILE
        self.service = None

        if self.enabled:
            self._initialize_service()

    def _initialize_service(self):
        if not self.enabled:
            print("Google Sheets integration is disabled")
            return

        if not self.spreadsheet_id:
            print("Google Sheets Spreadsheet ID not configured")
            self.enabled = False
            return

        if not os.path.exists(self.credentials_file):
            print(f"Google credentials file not found: {self.credentials_file}")
            self.enabled = False
            return

        try:
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_file,
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )

            self.service = build('sheets', 'v4', credentials=credentials)
            print("Google Sheets service initialized successfully")

        except Exception as e:
            print(f"Error initializing Google Sheets service: {e}")
            self.enabled = False

    def append_lead(self, lead_data, report_status="Generated"):
        if not self.enabled or not self.service:
            print("Google Sheets service not available")
            return False

        try:
            timestamp = datetime.now().isoformat()

            row = [
                timestamp,
                lead_data.get('fullName', ''),
                lead_data.get('email', ''),
                lead_data.get('companyName', ''),
                lead_data.get('industry', ''),
                lead_data.get('companySize', ''),
                lead_data.get('website', ''),
                report_status,
                lead_data.get('notes', '')
            ]

            body = {
                'values': [row]
            }

            result = self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range='Sheet1!A:I',
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()

            print(f"Lead logged to Google Sheets: {lead_data.get('email', 'unknown')}")
            return True

        except Exception as e:
            print(f"Error appending to Google Sheets: {e}")
            return False

    def update_lead_status(self, email, new_status):
        if not self.enabled or not self.service:
            return False

        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range='Sheet1!A:I'
            ).execute()

            values = result.get('values', [])

            for i, row in enumerate(values, start=1):
                if len(row) > 2 and row[2] == email:
                    range_update = f'Sheet1!H{i}'

                    self.service.spreadsheets().values().update(
                        spreadsheetId=self.spreadsheet_id,
                        range=range_update,
                        valueInputOption='USER_ENTERED',
                        body={'values': [new_status]}
                    ).execute()

                    print(f"Updated lead status in Sheets: {email} -> {new_status}")
                    return True

            print(f"Lead not found in Sheets: {email}")
            return False

        except Exception as e:
            print(f"Error updating Google Sheets: {e}")
            return False