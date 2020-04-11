from xlsxwriter.workbook import Workbook
from .database import Database
from . import LOGGER


class XlsxOperations(Database):

    @classmethod
    def update_ranking(cls, worksheet_dict, workbook_name):
        LOGGER.info("Preparing new xlsx file for local save")
        workbook = Workbook(workbook_name)
        for worksheet_name, league_csv_data in worksheet_dict.items():
            cls.make_time_trial_worksheet(workbook,
                                          league_csv_data['csv'],
                                          league_csv_data['format'],
                                          worksheet_name=worksheet_name)
        workbook.close()

    @classmethod
    def make_time_trial_worksheet(cls, workbook, league_csv, formatting_matrix, worksheet_name="default"):
        worksheet = workbook.add_worksheet(name=worksheet_name)
        worksheet.set_column(0, 0, width=28)
        worksheet.set_column(1, 100, width=19)
        track_count = len(cls.track_list)
        for r, row in enumerate(league_csv):
            for c, value in enumerate(row):
                format_obj = formatting_matrix[r][c]
                cell_format = workbook.add_format()
                cell_format.set_pattern(1)
                cell_format.set_bg_color(format_obj.background_color)
                cell_format.set_font_color(format_obj.font_color)
                cell_format.set_font_size(format_obj.font_size)
                try:
                    cell_format.set_align('center')
                    cell_format.set_align('vcenter')
                    cell_format.set_bold()
                    cell_format.set_border()
                    cell_format.text_wrap = True
                except AttributeError:
                    pass
                if r >= track_count + 8 and c == 4:
                    cell_format.set_border(0)
                    worksheet.merge_range(r, c, r, c + 2, value, cell_format)
                elif value or value == 0:
                    worksheet.write(r, c, value, cell_format)
        worksheet.freeze_panes(1, 1)
