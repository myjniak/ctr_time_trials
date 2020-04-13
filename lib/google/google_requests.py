from xlsxwriter import utility
from .google_drive_interactions import GoogleDriveInteractions
from .google_sheets_request_preparator import GoogleSheetsRequestPreparator
from . import LOGGER


class GoogleRequests(GoogleDriveInteractions, GoogleSheetsRequestPreparator):

    def __init__(self, cred_path, token_path, api_key):
        super().__init__(cred_path=cred_path, token_path=token_path, api_key=api_key)

    def update_ranking(self, remote_file_id, sheets_raw, sheet_ids):
        for sheet in sheets_raw:
            sheet_name = sheet.league_name
            if sheet.content[1:] == sheet.old_content[1:] and sheet.content[0][1:] == sheet.old_content[0][1:]:
                LOGGER.info(f"No changes in {sheet_name}, skipping")
                continue
            LOGGER.info(f"Updating {sheet_name}")
            csv_content = sheet.content
            sheet_id = sheet_ids[sheet_name]
            formatting_request = self.prepare_sheet_formatting_request(sheet_id, sheet.formatting)
            range_to_clear = self.get_range_to_clear(csv_content)
            self.update_sheet(remote_file_id, sheet_name, csv_content, formatting_request, range_to_clear)

    def update_sheet_ids(self, remote_file_id, sheets_raw, sheet_ids):
        for sheet in sheets_raw:
            if sheet.league_name not in sheet_ids:
                LOGGER.info(f"No sheet_id for {sheet.league_name}! Creating...")
                self.add_sheet(remote_file_id, sheet.league_name)
                sheet_ids = self.download_sheet_ids(remote_file_id)
        for sheet_name in sheet_ids:
            new_sheet_name_list = [sheet.league_name for sheet in sheets_raw]
            if sheet_name not in new_sheet_name_list:
                LOGGER.info(f"Escessive sheet_id detected! Deleting {sheet_name}...")
                self.delete_sheet(sheet_ids[sheet_name])
                sheet_ids = self.download_sheet_ids(remote_file_id)
        return sheet_ids

    @staticmethod
    def get_range_to_clear(csv_content):
        last_col = utility.xl_col_to_name(len(csv_content[0]))
        last_col_plus_10 = utility.xl_col_to_name(len(csv_content[0]) + 10)
        last_row = len(csv_content)
        range_to_clear = last_col + "1:" + last_col_plus_10 + last_row
        return range_to_clear

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

