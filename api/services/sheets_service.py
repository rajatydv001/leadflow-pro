import os
import requests
from datetime import datetime
from api.config import Config


class SheetsService:
    def __init__(self):
        self.enabled = Config.GOOGLE_SHEETS_ENABLED
        self.sheetdb_endpoint = os.environ.get('SHEETDB_ENDPOINT', '')
        self.service = None

    def append_lead(self, lead_data, report_status="Generated"):
        if not self.enabled:
            print("Google Sheets integration is disabled")
            return False

        if not self.sheetdb_endpoint:
            print("SheetDB endpoint not configured")
            return False

        try:
            timestamp = datetime.now().isoformat()

            data = {
                'timestamp': timestamp,
                'fullName': lead_data.get('fullName', ''),
                'email': lead_data.get('email', ''),
                'companyName': lead_data.get('companyName', ''),
                'industry': lead_data.get('industry', ''),
                'companySize': lead_data.get('companySize', ''),
                'website': lead_data.get('website', ''),
                'status': report_status,
                'notes': lead_data.get('notes', '')
            }

            response = requests.post(self.sheetdb_endpoint, json=data, timeout=10)
            
            if response.status_code in [200, 201]:
                print(f"Lead logged to SheetDB: {lead_data.get('email', 'unknown')}")
                return True
            else:
                print(f"SheetDB error: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            print(f"Error logging to SheetDB: {e}")
            return False

    def update_lead_status(self, email, new_status):
        if not self.enabled:
            return False

        if not self.sheetdb_endpoint:
            return False

        try:
            search_url = f"{self.sheetdb_endpoint}/search?email={email}"
            response = requests.get(search_url, timeout=10)
            
            if response.status_code == 200:
                results = response.json()
                if results and len(results) > 0:
                    row_id = results[0].get('id')
                    update_url = f"{self.sheetdb_endpoint}/{row_id}"
                    requests.patch(update_url, json={'status': new_status})
                    print(f"Updated lead status: {email} -> {new_status}")
                    return True
            
            print(f"Lead not found in SheetDB: {email}")
            return False

        except Exception as e:
            print(f"Error updating SheetDB: {e}")
            return False