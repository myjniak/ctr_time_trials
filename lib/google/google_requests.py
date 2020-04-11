from .google_drive_interactions import GoogleDriveInteractions
from .google_sheets_request_preparator import GoogleSheetsRequestPreparator
from . import LOGGER


class GoogleRequests(GoogleDriveInteractions, GoogleSheetsRequestPreparator):

    def __init__(self, cred_path, token_path, api_key):
        super().__init__(cred_path=cred_path, token_path=token_path, api_key=api_key)

    def update_ranking(self, remote_file_id, worksheet_dict, sheet_ids):
        for league, worksheet_data in worksheet_dict.items():
            LOGGER.debug(f"Updating {league}")
            sheet_id = sheet_ids[league]
            formatting = self.prepare_sheet_formatting_request(worksheet_data['format'], sheet_id)
            csv_content = worksheet_data['csv']
            self.update_sheet(remote_file_id, league, csv_content, formatting)

    def get_sheet_id(self, remote_file_id, sheet_name):
        sheet_id_dict = self.download_sheet_ids(remote_file_id)
        return sheet_id_dict[sheet_name]

    def protect_first_column(self, remote_file_id, master_email):
        sheet_id_dict = self.download_sheet_ids(remote_file_id)
        first_sheet_id = list(sheet_id_dict.values())[0]
        body = {
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
        self.batch_update(remote_file_id, body)
