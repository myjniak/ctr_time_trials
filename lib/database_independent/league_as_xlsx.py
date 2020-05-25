from .league_as_csv import LeagueAsCsv
from .cell_format import CellFormat


GOLD = "FFD700"
SILVER = "C4CACE"
BRONZE = "A46628"
ORANGE = "FFA500"
BLACK = "000000"
RED = "FF0000"
GREEN = "00FF00"
WHITE = "FFFFFF"
LIGHT_BLUE = "70A8D9"
PLACE_COLORS = [GOLD, SILVER, BRONZE, WHITE, WHITE, WHITE, WHITE, 'F3FFF2']


class LeagueAsXlsx(LeagueAsCsv):

    def __init__(self, league_as_json, league, track_list, league_names, time_zone_diff, point_system,
                 league_points_minimum, bots_list):
        super().__init__(league_as_json, league, track_list, league_names, time_zone_diff, point_system,
                         league_points_minimum)
        self.bots_list = bots_list
        self.time_trials = league_as_json
        self.formatting = self.generate_sheet_formatting_matrix(self.content)

    def __call__(self, league_as_json):
        super().__call__(league_as_json)
        self.time_trials = league_as_json
        self.formatting = self.generate_sheet_formatting_matrix(self.content)

    def generate_sheet_formatting_matrix(self, league_csv):
        formatting_matrix = list()
        track_count = len(self.track_list)
        row_len = len(league_csv[track_count + 1])
        formatting_matrix.append(self._evaluate_formatting_for_player_row(league_csv))
        for track_times_formatting in self._evaluate_formatting_for_time_records(league_csv):
            formatting_matrix.append(track_times_formatting)
        formatting_matrix.append([CellFormat(16, BLACK, GOLD)] * row_len)
        formatting_matrix.append([CellFormat(16, BLACK, SILVER)] * row_len)
        formatting_matrix.append([CellFormat(16, BLACK, BRONZE)] * row_len)
        formatting_matrix.append([CellFormat(20, RED, 'F5F5F5')] * row_len)
        formatting_matrix.append([CellFormat(13, RED, 'F5F5F5')] * row_len)
        formatting_matrix.append(self._evaluate_formatting_for_total_time_row(league_csv))
        formatting_matrix.append([])
        for legend_and_announcements_formatting in self._evaluate_formatting_for_legend_and_announcements():
            formatting_matrix.append(legend_and_announcements_formatting)
        return formatting_matrix

    def _evaluate_formatting_for_total_time_row(self, league_csv):
        formatting_row = list()
        total_time_row = len(self.track_list) + 6
        for col, cell in enumerate(league_csv[total_time_row]):
            if col != 0 and int(cell.split(":")[0]) < 70:
                formatting_row.append(CellFormat(13, WHITE, BLACK))
            else:
                formatting_row.append(CellFormat(13, BLACK, 'F5F5F5'))
        return formatting_row

    def _evaluate_formatting_for_player_row(self, league_csv):
        formatting_row = list()
        total_time_row = len(self.track_list) + 6
        for col, cell in enumerate(league_csv[0]):
            if cell in self.bots_list:
                background_color = RED
                font_color = BLACK
            elif col != 0 and int(league_csv[total_time_row][col].split(":")[0]) < 70:
                background_color = BLACK
                font_color = GOLD
            else:
                background_color = ORANGE
                font_color = BLACK
            formatting_row.append(CellFormat(font_size=11, font_color=font_color, background_color=background_color))
        return formatting_row

    def _evaluate_formatting_for_time_records(self, league_csv):
        track_count = len(self.track_list)
        time_formatting_matrix = list()
        players = league_csv[0][1:]
        for r, row in enumerate(league_csv[1:track_count+1]):
            time_formatting_matrix.append([CellFormat(13, BLACK, LIGHT_BLUE)])
            for c in range(1, len(row)):
                # if c % 6 == 1:
                #     league_csv[r][c] = "FIVE"
                # if c % 6 == 2:
                #     league_csv[r][c] = "ma"
                # if c % 6 == 3:
                #     league_csv[r][c] = "sub"
                # if c % 6 == 4:
                #     league_csv[r][c] = "70min"
                # if c % 6 == 5:
                #     league_csv[r][c] = "o ja"
                # if c % 6 == 0:
                #     league_csv[r][c] = "nie moge"
                cell_format = self._evaluate_time_cell_format(players[c-1], row[0])
                time_formatting_matrix[r].append(cell_format)
        return time_formatting_matrix

    @staticmethod
    def _legend_and_announcements_row_formatting(place_bg_color=WHITE, place_font_color=BLACK, font_size=13):
        return [CellFormat(font_size, BLACK, GREEN),
                CellFormat(font_size, place_font_color, place_bg_color),
                *[CellFormat()]*2,
                CellFormat(font_size-2, BLACK, 'BADBAD')]

    def _evaluate_formatting_for_legend_and_announcements(self):
        formatting_matrix = list()
        formatting_matrix.append(self._legend_and_announcements_row_formatting(font_size=16))
        for place_color in PLACE_COLORS:
            formatting_matrix.append(self._legend_and_announcements_row_formatting(place_color))
        formatting_matrix.append(self._legend_and_announcements_row_formatting(place_font_color='DADADA'))
        return formatting_matrix

    def _evaluate_time_cell_format(self, player, track):
        self.time_trials[player]['tracks'][track].setdefault('points', 0)
        pts = self.time_trials[player]['tracks'][track]['points']
        bg_color = WHITE
        if self.point_system[-1] <= pts <= self.point_system[0]:
            font_color = BLACK
            for i, points in enumerate(self.point_system):
                if len(PLACE_COLORS) > i and (self.point_system + [0])[i+1] < pts <= self.point_system[i]:
                    bg_color = PLACE_COLORS[i]
        else:
            font_color = 'DADADA'
        return CellFormat(15, font_color, bg_color)
