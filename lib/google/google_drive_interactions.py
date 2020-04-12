from __future__ import print_function
import pickle
import os.path
import requests
from json import JSONDecodeError
from httplib2 import ServerNotFoundError
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from lib import LOGGER

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive']


def try_request_until_success(func):
    def wrapper(*args, **kwargs):
        while True:
            try:
                return func(*args, **kwargs)
            except JSONDecodeError as err:
                LOGGER.warning(f"Oops, sth bad happenned:\n{str(err)}")
            except requests.exceptions.ConnectTimeout:
                LOGGER.warning(f"Oops, we have a timeout error")
            except requests.exceptions.ConnectionError:
                LOGGER.warning(f"Oops, we have a connection error")
            except ServerNotFoundError:
                LOGGER.warning(f"Oops, it's a httplib2 connection error")
    return wrapper


class GoogleDriveInteractions:
    def __init__(self, cred_path, token_path, api_key):
        LOGGER.info("Setting up google drive service...")
        self.service = self.get_google_drive_service(cred_path, token_path)
        self.sheets_service = self.get_google_sheets_service(cred_path, token_path)
        self.key = api_key
        LOGGER.info("Done")

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
        LOGGER.info(f"Downloading to {local_file_path}")
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

    @staticmethod
    @try_request_until_success
    def execute_request(request):
        response = request.execute()
        LOGGER.debug(response)

    @try_request_until_success
    def download_sheet_ids(self, remote_file_id):
        content = requests.get(f"https://sheets.googleapis.com/v4/spreadsheets/{remote_file_id}"
                               f"?fields=sheets(properties)"
                               f"&key={self.key}", timeout=5)
        sheet_id_dict = {sheet_info["properties"]["title"]: sheet_info["properties"]["sheetId"]
                         for sheet_info in content.json()['sheets']}
        return sheet_id_dict

    @try_request_until_success
    def batch_update(self, remote_file_id, body):
        request = self.sheets_service.spreadsheets().batchUpdate(spreadsheetId=remote_file_id,
                                                                 body=body)
        self.execute_request(request)

    @try_request_until_success
    def get_cell_value(self, remote_file_id, cell):
        content = requests.get(f"https://sheets.googleapis.com/v4/spreadsheets/{remote_file_id}"
                               f"/values/{cell}"
                               f"?key={self.key}", timeout=5).json()
        if "values" in content:
            return content["values"][0][0]

    def clear_cell_range(self, remote_file_id, cell_range):
        request = self.sheets_service.spreadsheets().values().clear(spreadsheetId=remote_file_id,
                                                                    range=cell_range)
        self.execute_request(request)

    def update_sheet_formatting(self, remote_file_id, formatting_request):
        body = {
            "requests": formatting_request
        }
        self.batch_update(remote_file_id, body)

    def update_sheet(self, remote_file_id, sheet_name, csv_content, formatting=None):
        body = {
            'values': csv_content
        }
        request = self.sheets_service.spreadsheets().values().update(spreadsheetId=remote_file_id,
                                                                     range=sheet_name,
                                                                     valueInputOption="RAW",
                                                                     body=body)
        self.execute_request(request)
        if formatting:
            self.update_sheet_formatting(remote_file_id, formatting)

    @try_request_until_success
    def get_range_value(self, remote_file_id, cell_range):
        content = requests.get(f"https://sheets.googleapis.com/v4/spreadsheets/{remote_file_id}"
                               f"/values/{cell_range}"
                               f"?key={self.key}", timeout=5)
        LOGGER.debug(content)
        return content.json()["values"]
