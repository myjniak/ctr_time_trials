

class GoogleSheetsRequestPreparator:

    @classmethod
    def prepare_sheet_formatting_request(cls, sheet_id, formatting_matrix):
        format_requests = list()
        for row_index, row in enumerate(formatting_matrix):
            for col_index, cell_format in enumerate(row):
                format_requests.append(cls.generate_request_for_cell(sheet_id, row_index, col_index, cell_format))
        row_count = len(formatting_matrix)
        format_requests.append(cls.generate_request_for_column_sizes(sheet_id, 0, 0, 200))
        format_requests.append(cls.generate_request_for_column_sizes(sheet_id, 1, 100, 137))
        format_requests.append(cls.generate_request_for_cell_merge(sheet_id, row_count - 8, row_count, 4, 6))
        return format_requests

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
