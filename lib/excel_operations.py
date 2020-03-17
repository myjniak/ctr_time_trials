import csv
import glob
import json
from pandas import read_excel
from xlsxwriter.workbook import Workbook
from .json_operations import JsonOperations


GOLD = "FFD700"
SILVER = "C4CACE"
BRONZE = "A46628"
COLOR_PRIZES = [GOLD, SILVER, BRONZE, 'FFFFFF', 'FFFFFF', 'FFFFFF', 'FFFFFF', 'F3FFF2']


class ExcelOperations:

    def __init__(self, point_system, league_names, **file_paths):
        self.point_system = point_system
        self.league_names = league_names
        self.csv_name = file_paths["csv_output"]
        self.time_trials = None
        self.track_list = None
        self.league_count = None
        self.load_time_trial_info(**file_paths)

    def load_time_trial_info(self, **file_paths):
        self.time_trials = JsonOperations.load_json(file_paths["time_trials_json"])
        self.track_list = list(JsonOperations.load_track_id_json(file_paths["track_ids"]).values())
        self.league_count = max([player_info["league"] for player_info in self.time_trials.values()])

    def convert_csvs_to_xlsx(self, name="time_trial_ranking.xlsx", worksheet_names=[1, 2, 3, 4, 5, 6]):
        workbook = Workbook(name)
        for league in range(1, self.league_count + 1):
            worksheet_name = worksheet_names[league-1]
            for csvfile in glob.glob(self.csv_name + str(league) + ".csv"):
                self.make_time_trial_worksheet(workbook, csvfile, worksheet_name=worksheet_name)
        workbook.close()

    @staticmethod
    def convert_xlsx_to_json(xlsx_path, json_path):
        excel_data_df = read_excel(xlsx_path, header=0, index_col=0, keep_default_na=True)
        json_str = excel_data_df.apply(lambda x: [x.dropna()], axis=0).to_json()
        parsed_json = json.loads(json_str)
        for player in parsed_json:
            parsed_json[player] = {'tracks': {track: {"time": time} for track, time in parsed_json[player][0].items()}}
        JsonOperations.save_json(parsed_json, json_path)
        return parsed_json

    def make_time_trial_worksheet(self, workbook, csv_file, worksheet_name="default"):
        worksheet = workbook.add_worksheet(name=worksheet_name)
        worksheet.set_column(0, 0, width=28)
        worksheet.set_column(1, 100, width=19)
        players = list()
        track_count = len(self.track_list)
        with open(csv_file, 'rt', encoding='utf8') as f:
            reader = csv.reader(f)
            for r, row in enumerate(reader):
                if r == 0:
                    players = row[1:]
                for c, value in enumerate(row):
                    if value:
                        if 0 < r <= len(self.track_list) and c > 0:
                            cell_format = self.evaluate_cell_format(r, players[c-1], workbook)
                        else:
                            cell_format = workbook.add_format()
                            cell_format.set_pattern(1)
                            cell_format.set_bg_color('white')
                        if r == 0:
                            if players[c-1] in ["N. Tropy", "Oxide", "Velo"]:
                                cell_format.set_bg_color('red')
                            else:
                                cell_format.set_bg_color('orange')
                            cell_format.set_font_size(13)
                        if c == 0:
                            cell_format.set_bg_color('green')
                            cell_format.set_font_size(15)
                        if r == track_count + 1:
                            cell_format.set_bg_color(GOLD)
                            cell_format.set_font_size(18)
                        elif r == track_count + 2:
                            cell_format.set_bg_color(SILVER)
                            cell_format.set_font_size(18)
                        elif r == track_count + 3:
                            cell_format.set_bg_color(BRONZE)
                            cell_format.set_font_size(18)
                        elif r == track_count + 4:
                            cell_format.set_bg_color('F5F5F5')
                            cell_format.set_font_color('red')
                            cell_format.set_font_size(22)
                        elif r == track_count + 5:
                            cell_format.set_font_color('red')
                            cell_format.set_bg_color('F5F5F5')
                            cell_format.text_wrap = True
                            cell_format.set_font_size(13)
                        elif r == track_count + 6:
                            cell_format.set_font_size(18)
                        elif r == track_count + 8:
                            cell_format.set_font_size(18)
                        elif track_count + 9 <= r < track_count + 9 + len(self.point_system) and c == 1:
                            if len(COLOR_PRIZES) > r - (track_count + 9):
                                cell_format.set_bg_color(COLOR_PRIZES[r - (track_count + 9)])
                            else:
                                cell_format.set_bg_color('white')
                        elif r == track_count + 17 and c == 1:
                            cell_format.set_font_color('DADADA')
                        if r >= track_count + 8 and c == 1:
                            cell_format.set_font_size(15)
                        try:
                            cell_format.set_align('center')
                            cell_format.set_align('vcenter')
                            cell_format.set_bold()
                            cell_format.set_border()
                        except AttributeError:
                             pass
                        if r >= track_count + 8 and c == 5:
                            cell_format.set_border(0)
                            cell_format.set_bg_color('BADBAD')
                            worksheet.merge_range(r, c - 1, r, c + 1, value, cell_format)
                        else:
                            worksheet.write(r, c, value, cell_format)
        worksheet.freeze_panes(1, 1)

    def convert_user_times_json_to_csvs(self, minimum_points=1, cur_datetime=''):
        for league in range(1, self.league_count + 1):
            self.convert_user_times_json_to_league_csv(league, minimum_points, cur_datetime)

    def write_all_players_times(self, dict_writer, players):
        for track in self.track_list:
            track_times = {player: self.time_trials[player]['tracks'][track]["time"] for player in players
                           if track in self.time_trials[player]['tracks']}
            track_times[' '] = track
            dict_writer.writerow(track_times)

    def write_all_players_medals(self, dict_writer, players):
        for medal_rank in ['gold', 'silver', 'bronze']:
            medals = {player: player_info['medals'][medal_rank] for player, player_info in self.time_trials.items()
                      if player in players}
            medals[' '] = medal_rank.capitalize() + " Medals"
            dict_writer.writerow(medals)

    def write_all_players_total_points(self, dict_writer, list_writer, league, players, minimum_points=1):
        if league == 1:
            upper_league_name = None
        else:
            upper_league_name = self.league_names[league - 2]
        total_points = {player: player_info['total_points'] for player, player_info in self.time_trials.items()
                        if player in players}
        total_points[' '] = 'Total Points'
        dict_writer.writerow(total_points)
        points_in_upper_league = {player: player_info['total_points_in_upper_league']
                                  for player, player_info in self.time_trials.items()
                                  if player in players}
        if any(points_in_upper_league.values()):
            points_in_upper_league[' '] = f'Total Points In {upper_league_name} ({minimum_points}p to advance)'
            dict_writer.writerow(points_in_upper_league)
        else:
            list_writer.writerow([""])

    def convert_user_times_json_to_league_csv(self, league, minimum_points=1, cur_datetime=''):
        data = self.time_trials
        with open(self.csv_name + str(league) + ".csv", mode='w+', newline='') as f:
            list_writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            players = [player for player in data.keys() if data[player]["league"] == league]
            players = sorted(players,
                             key=lambda player: self.time_trials[player]['total_points'],
                             reverse=True)
            list_writer.writerow([cur_datetime] + players)
            dict_writer = csv.DictWriter(f,
                                         fieldnames=[' '] + players,
                                         delimiter=',',
                                         quotechar='"',
                                         quoting=csv.QUOTE_MINIMAL)
            self.write_all_players_times(dict_writer, players)
            self.write_all_players_medals(dict_writer, players)
            self.write_all_players_total_points(dict_writer, list_writer, league, players,
                                                minimum_points=minimum_points)
            total_time = {player: player_info['total_time'] for player, player_info in data.items()
                          if player in players}
            total_time[' '] = 'Total Time'
            dict_writer.writerow(total_time)
            list_writer.writerow([""])
            list_writer.writerow(["POINT SYSTEM", '', '', '', '', 'ANNOUNCEMENTS'])
            try:
                with open(f"logs/{league}.txt", 'r') as league_logs:
                    announcements = league_logs.read().splitlines()
                    announcements.reverse()
            except FileNotFoundError:
                announcements = []
            for i, points in enumerate(self.point_system):
                if i == 0:
                    place = '1st'
                elif i == 1:
                    place = '2nd'
                elif i == 2:
                    place = '3rd'
                else:
                    place = f"{i+1}th"
                if i < len(announcements):
                    announcement = announcements[i]
                else:
                    announcement = ''
                list_writer.writerow([place, '1:00.00', f"{points}p", '', '', announcement])
            if i+1 < len(announcements):
                announcement = announcements[i+1]
            else:
                announcement = ''
            list_writer.writerow([f">{i+1}th", '1:00.00', '0p', '', '', announcement])

    def evaluate_cell_format(self, row, player, workbook):
        track = self.track_list[row-1]
        if track in self.time_trials[player]['tracks']:
            self.time_trials[player]['tracks'][track].setdefault('points', 0)
            pts = self.time_trials[player]['tracks'][track]['points']
            cell_format = workbook.add_format()
            cell_format.set_pattern(1)
            cell_format.set_font_size(15)
            cell_format.set_bg_color('FFFFFF')
            if pts in self.point_system:
                cell_format.set_font_color('black')
                for i, points in enumerate(self.point_system):
                    if len(COLOR_PRIZES) > i and pts == self.point_system[i]:
                        cell_format.set_bg_color(COLOR_PRIZES[i])
            else:
                cell_format.set_font_color('DADADA')
            return cell_format
