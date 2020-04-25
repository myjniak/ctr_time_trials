from xlsxwriter.workbook import Workbook
from .grand_prix_as_csv import GrandPrixAsCsv
from . import LOGGER

GOLD = "FFD700"
SILVER = "C4CACE"
BRONZE = "A46628"
WHITE = "FFFFFF"
LIGHT_BLUE = "DDEFFF"
RED = "FF0000"
BLACK = "000000"


class GrandPrixAsXlsx(GrandPrixAsCsv):

    def save(self, file_path):
        LOGGER.info("Preparing Grand Prix xlsx file for local save")
        workbook = Workbook(file_path)
        worksheet_name = "Grand Prix"
        csv_data = self.content
        self.make_time_trial_worksheet(workbook,
                                       csv_data,
                                       worksheet_name=worksheet_name)
        workbook.close()

    @classmethod
    def make_time_trial_worksheet(cls, workbook, csv_data, worksheet_name="default"):
        worksheet = workbook.add_worksheet(name=worksheet_name)
        worksheet.set_column(0, 0, width=10)
        worksheet.set_column(1, 1, width=50)
        worksheet.set_column(2, 2, width=20)
        for r, row in enumerate(csv_data):
            for c, value in enumerate(row):
                cell_format = workbook.add_format()
                cell_format.set_pattern(1)
                cell_format.set_font_color(BLACK)
                cell_format.set_font_size(24)
                cell_format.set_bg_color(cls.row_bg_color(r))
                cell_format.set_align('center')
                cell_format.set_align('vcenter')
                cell_format.set_font(cls.col_set_font(c))
                worksheet.write(r, c, value, cell_format)

    @staticmethod
    def col_set_font(col):
        if col == 1:
            return "Arial"
        else:
            return "Impact"

    @staticmethod
    def row_bg_color(row):
        if row == 0:
            c = GOLD
        elif row == 1:
            c = SILVER
        elif row == 2:
            c = BRONZE
        elif row % 2 == 0:
            c = WHITE
        else:
            c = LIGHT_BLUE
        return c
