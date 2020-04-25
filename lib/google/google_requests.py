from .google_drive_interactions import GoogleDriveInteractions
from .google_sheets_request_preparator import GoogleSheetsRequestPreparator
from . import LOGGER


class GoogleRequests(GoogleDriveInteractions, GoogleSheetsRequestPreparator):

    def __init__(self, cred_path, token_path, api_key):
        super().__init__(cred_path=cred_path, token_path=token_path, api_key=api_key)

    def update_grand_prix(self, remote_file_id, csv_content):
        LOGGER.info("Updating Grand Prix ranking")
        self.update_sheet(remote_file_id, "Grand Prix 1", csv_content)

    def update_leagues(self, remote_file_id, sheets_raw, sheet_ids):
        for sheet in sheets_raw:
            sheet_name = sheet.league_name
            no_changes = sheet.old_content and \
                         sheet.content[1:] == sheet.old_content[1:] and \
                         sheet.content[0][1:] == sheet.old_content[0][1:]
            if no_changes:
                LOGGER.info(f"No changes in {sheet_name}, skipping")
                continue
            LOGGER.info(f"Updating {sheet_name}")
            csv_content = sheet.content
            sheet_id = sheet_ids[sheet_name]
            formatting_request = self.prepare_sheet_formatting_request(sheet_id, sheet.formatting)
            start_column = len(csv_content[0])
            end_column = start_column + 100
            start_row = 0
            end_row = len(csv_content)
            range_to_clear = self.numeric_range_to_letter_range(start_row, end_row, start_column, end_column)
            range_to_clear = "'" + sheet_name + "'!" + range_to_clear
            clear_formatting_request = \
                [self.generate_request_for_clear_range(sheet_id, start_row, end_row, start_column, end_column)]
            self.update_sheet(remote_file_id,
                              sheet_name,
                              csv_content,
                              formatting_request,
                              clear_formatting_request,
                              range_to_clear)

    def update_sheet_ids(self, remote_file_id, sheets_raw, sheet_ids):
        for sheet in sheets_raw:
            if sheet.league_name not in sheet_ids:
                LOGGER.info(f"No sheet_id for {sheet.league_name}! Creating...")
                self.add_sheet(remote_file_id, sheet.league_name)
                sheet_ids = self.download_sheet_ids(remote_file_id)
        for sheet_name in sheet_ids:
            new_sheet_name_list = [sheet.league_name for sheet in sheets_raw]
            if sheet_name not in new_sheet_name_list:
                LOGGER.info(f"Excessive sheet_id detected! Deleting {sheet_name}...")
                self.delete_sheet(remote_file_id, sheet_ids[sheet_name])
                sheet_ids = self.download_sheet_ids(remote_file_id)
        return sheet_ids

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

