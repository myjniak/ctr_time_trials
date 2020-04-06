from __future__ import print_function
import pickle
import os.path
import requests
from .logger import log
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive']


class GoogleDriveInteractions:
    def __init__(self, cred_path, token_path, api_key):
        log("Setting up google drive service...")
        self.service = self.get_google_drive_service(cred_path, token_path)
        self.sheets_service = self.get_google_sheets_service(cred_path, token_path)
        self.key = api_key
        log("Done")

    @staticmethod
    def auth_setup(cred_path, token_path):
        """Shows basic usage of the Drive v3 API.
        Prints the names and ids of the first 10 files the user has access to.
        """
        creds = None
        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(cred_path, SCOPES)
                creds = flow.run_local_server(port=0)
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)

        return creds

    def get_google_drive_service(self, cred_path, token_path):
        credentials = self.auth_setup(cred_path=cred_path, token_path=token_path)
        service = build('drive', 'v3', credentials=credentials)
        return service

    def get_google_sheets_service(self, cred_path, token_path):
        credentials = self.auth_setup(cred_path=cred_path, token_path=token_path)
        service = build('sheets', 'v4', credentials=credentials)
        return service

    def download_file(self, local_file_path, remote_file_id):
        request = self.service.files().export_media(
            fileId=remote_file_id,
            mimeType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        with open(local_file_path, 'wb') as f:
            downloader = MediaIoBaseDownload(f, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()

    def upload_file(self, local_file_path, remote_file_id):
        file_metadata = {'name': "CTR Time Trial Ranking Polska"}
        media = MediaFileUpload(local_file_path,
                                mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        self.service.files().update(body=file_metadata,
                                    media_body=media,
                                    fileId=remote_file_id,
                                    fields='id').execute()

    def download_sheet_ids(self, remote_file_id):
        content = requests.get(f"https://sheets.googleapis.com/v4/spreadsheets/{remote_file_id}"
                               f"?fields=sheets(properties)"
                               f"&key={self.key}")
        sheet_id_dict = {sheet_info["properties"]["title"]: sheet_info["properties"]["sheetId"]
                         for sheet_info in content.json()['sheets']}
        return sheet_id_dict

    def protect_first_column(self, remote_file_id, master_email):
        sheet_id_dict = self.download_sheet_ids(remote_file_id)
        first_sheet_id = list(sheet_id_dict.values())[0]
        json_post = {
            "requests": [
                {
                    "addProtectedRange": {
                        "protectedRange": {
                            "range": {
                                "sheetId": first_sheet_id,
                                "startColumnIndex": 0,
                                "endColumnIndex": 1,
                                "startRowIndex": 1
                            },
                            "description": "Protecting track names",
                            "editors": {
                                "users": [master_email]
                            }
                        }
                    }
                }
            ]
        }
        request = self.sheets_service.spreadsheets().batchUpdate(spreadsheetId=remote_file_id,
                                                                 body=json_post)
        response = request.execute()
        log(response)

    def get_cell_value(self, remote_file_id, cell):
        content = requests.get(f"https://sheets.googleapis.com/v4/spreadsheets/{remote_file_id}"
                               f"/values/{cell}"
                               f"?key={self.key}").json()
        if "values" in content:
            return content["values"][0][0]

    def clear_cell_range(self, remote_file_id, cell_range):
        request = self.sheets_service.spreadsheets().values().clear(spreadsheetId=remote_file_id,
                                                                    range=cell_range)
        response = request.execute()
        log(response)
