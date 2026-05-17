import os
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from config import Config


class DriveService:
    def __init__(self):
        self.enabled = Config.GOOGLE_DRIVE_ENABLED
        self.folder_id = Config.GOOGLE_DRIVE_FOLDER_ID
        self.credentials_file = Config.GOOGLE_CREDENTIALS_FILE
        self.service = None
        self.folder_name = "Lead Reports"

        if self.enabled:
            self._initialize_service()

    def _initialize_service(self):
        if not self.enabled:
            print("Google Drive integration is disabled")
            return

        if not os.path.exists(self.credentials_file):
            print(f"Google credentials file not found: {self.credentials_file}")
            self.enabled = False
            return

        try:
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_file,
                scopes=['https://www.googleapis.com/auth/drive.file']
            )

            self.service = build('drive', 'v3', credentials=credentials)

            if not self.folder_id:
                self.folder_id = self._get_or_create_folder()

            if self.folder_id:
                print(f"Google Drive service initialized successfully. Folder ID: {self.folder_id}")
            else:
                print("Could not find or create Drive folder")
                self.enabled = False

        except Exception as e:
            print(f"Error initializing Google Drive service: {e}")
            self.enabled = False

    def _get_or_create_folder(self):
        try:
            results = self.service.files().list(
                q=f"name='{self.folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false",
                fields="files(id, name)"
            ).execute()

            folders = results.get('files', [])

            if folders:
                return folders[0]['id']

            file_metadata = {
                'name': self.folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }

            folder = self.service.files().create(
                body=file_metadata,
                fields='id'
            ).execute()

            print(f"Created new Drive folder: {self.folder_name}")
            return folder.get('id')

        except Exception as e:
            print(f"Error creating Drive folder: {e}")
            return None

    def upload_pdf(self, pdf_path, company_name):
        if not self.enabled or not self.service:
            print("Google Drive service not available")
            return None

        if not os.path.exists(pdf_path):
            print(f"PDF file not found: {pdf_path}")
            return None

        try:
            date_str = datetime.now().strftime('%Y%m%d')
            filename = f"{company_name.replace(' ', '_')}_{date_str}_AuditReport.pdf"

            file_metadata = {
                'name': filename,
                'parents': [self.folder_id]
            }

            media = MediaFileUpload(
                pdf_path,
                mimetype='application/pdf',
                resumable=True
            )

            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, webViewLink'
            ).execute()

            self.service.permissions().create(
                fileId=file.get('id'),
                body={
                    'type': 'anyone',
                    'role': 'reader'
                }
            ).execute()

            print(f"PDF uploaded to Google Drive: {filename}")
            return {
                'file_id': file.get('id'),
                'web_view_link': file.get('webViewLink')
            }

        except Exception as e:
            print(f"Error uploading to Google Drive: {e}")
            return None