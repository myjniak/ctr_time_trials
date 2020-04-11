

class GoogleSheetsRequestPreparator:

    @staticmethod
    def generate_request_for_cell(row, column, sheet_id, cell_format):
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

    @classmethod
    def prepare_sheet_formatting_request(cls, formatting_matrix, sheet_id):
        format_requests = list()
        for row_index, row in enumerate(formatting_matrix):
            for col_index, cell_format in enumerate(row):
                format_requests.append(cls.generate_request_for_cell(row_index, col_index, sheet_id, cell_format))
        return format_requests
