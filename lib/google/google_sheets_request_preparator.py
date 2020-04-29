from xlsxwriter import utility


class GoogleSheetsRequestPreparator:

    @staticmethod
    def numeric_range_to_letter_range(start_row, end_row, start_column, end_column):
        start_col = utility.xl_col_to_name(start_column)
        end_col = utility.xl_col_to_name(end_column)
        return start_col + str(start_row + 1) + ":" + end_col + str(end_row + 1)

    @staticmethod
    def letter_range_to_numeric_range(letter_range):
        start_cell, end_cell = letter_range.split(":")
        start_row, start_column = utility.xl_cell_to_rowcol(start_cell)
        end_row, end_column = utility.xl_cell_to_rowcol(end_cell)
        return start_row, end_row, start_column, end_column

    @classmethod
    def prepare_sheet_formatting_request(cls, sheet_id, formatting_matrix):
        format_requests = list()
        for row_index, row in enumerate(formatting_matrix):
            for col_index, cell_format in enumerate(row):
                format_requests.append(cls.generate_request_for_cell(sheet_id, row_index, col_index, cell_format))
        row_count = len(formatting_matrix)
        format_requests.append(cls.generate_request_for_column_sizes(sheet_id, 0, 0, 200))
        format_requests.append(cls.generate_request_for_column_sizes(sheet_id, 1, 100, 145))
        format_requests.append(cls.generate_request_for_row_sizes(sheet_id, 0, 40, 20))
        format_requests.append(cls.generate_request_for_row_sizes(sheet_id, 41, 60, 40))
        format_requests.append(cls.generate_request_for_cell_merge(sheet_id, row_count - 10, row_count - 1, 4, 6))
        format_requests.append(cls.generate_request_for_all_cells(sheet_id))
        return format_requests

    @staticmethod
    def generate_request_for_clear_range(sheet_id, start_row, end_row, start_column, end_column):
        template = {
            "repeatCell": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": start_row,
                    "endRowIndex": end_row + 1,
                    "startColumnIndex": start_column,
                    "endColumnIndex": end_column + 1
                },
                "cell": {
                },
                "fields": "userEnteredFormat(backgroundColor, textFormat(bold, fontSize, foregroundColor))"
            }
        }
        return template

    @staticmethod
    def generate_request_for_all_cells(sheet_id):
        template = {
            "repeatCell": {
                "range": {
                    "sheetId": sheet_id,
                    "startColumnIndex": 0,
                    "endColumnIndex": 100
                },
                "cell": {
                    "userEnteredFormat": {
                        "horizontalAlignment": "CENTER",
                        "verticalAlignment": "MIDDLE",
                        "wrapStrategy": "WRAP"
                    }
                },
                "fields": "userEnteredFormat(horizontalAlignment, verticalAlignment, wrapStrategy)"
            },
        }
        return template

    @staticmethod
    def generate_request_for_cell_merge(sheet_id, start_row, end_row, start_column, end_column):
        template = {
            "mergeCells": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": start_row,
                    "endRowIndex": end_row + 1,
                    "startColumnIndex": start_column,
                    "endColumnIndex": end_column + 1
                },
                "mergeType": "MERGE_ROWS"
            }
        }
        return template

    @staticmethod
    def generate_request_for_column_sizes(sheet_id, start_column, end_column, size):
        template = {
            "updateDimensionProperties": {
                "range": {
                    "sheetId": sheet_id,
                    "dimension": "COLUMNS",
                    "startIndex": start_column,
                    "endIndex": end_column + 1
                },
                "properties": {
                    "pixelSize": size
                },
                "fields": "pixelSize"
            }
        }
        return template

    @staticmethod
    def generate_request_for_row_sizes(sheet_id, start_row, end_row, size):
        template = {
            "updateDimensionProperties": {
                "range": {
                    "sheetId": sheet_id,
                    "dimension": "ROWS",
                    "startIndex": start_row,
                    "endIndex": end_row + 1
                },
                "properties": {
                    "pixelSize": size
                },
                "fields": "pixelSize"
            }
        }
        return template

    @staticmethod
    def generate_request_for_cell(sheet_id, row, column, cell_format):
        bg_colors = tuple(int(cell_format.background_color[i:i + 2], 16)/256 for i in (0, 2, 4))
        font_colors = tuple(int(cell_format.font_color[i:i + 2], 16) / 256 for i in (0, 2, 4))
        template = {
            "repeatCell": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": row,
                    "endRowIndex": row + 1,
                    "startColumnIndex": column,
                    "endColumnIndex": column + 1
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {
                            "red": bg_colors[0],
                            "green": bg_colors[1],
                            "blue": bg_colors[2]
                        },
                        "textFormat": {
                            "foregroundColor": {
                                "red": font_colors[0],
                                "green": font_colors[1],
                                "blue": font_colors[2]
                            },
                            "fontSize": cell_format.font_size,
                            "bold": True
                        }
                    }
                },
                "fields": "userEnteredFormat(backgroundColor, textFormat(bold, fontSize, foregroundColor))"
            }
        }
        return template

    @staticmethod
    def generate_request_for_range(sheet_id, start_row, end_row, start_column, end_column, cell_format):
        bg_colors = tuple(int(cell_format.background_color[i:i + 2], 16)/256 for i in (0, 2, 4))
        font_colors = tuple(int(cell_format.font_color[i:i + 2], 16) / 256 for i in (0, 2, 4))
        template = {
            "repeatCell": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": start_row,
                    "endRowIndex": end_row + 1,
                    "startColumnIndex": start_column,
                    "endColumnIndex": end_column + 1
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {
                            "red": bg_colors[0],
                            "green": bg_colors[1],
                            "blue": bg_colors[2]
                        },
                        "textFormat": {
                            "foregroundColor": {
                                "red": font_colors[0],
                                "green": font_colors[1],
                                "blue": font_colors[2]
                            },
                            "fontSize": cell_format.font_size,
                            "bold": True
                        }
                    }
                },
                "fields": "userEnteredFormat(backgroundColor, textFormat(bold, fontSize, foregroundColor))"
            }
        }
        return template
