import csv
from copy import deepcopy
from datetime import datetime, timedelta
from lib import LOGGER


class LeagueAsCsv:

    def __init__(self, league_as_json, league, track_list, league_names, time_zone_diff, point_system,
                 league_points_minimum):
        self.league_points_minimum = league_points_minimum
        self.league = league
        self.track_list = track_list
        self.league_names = league_names
        self.time_zone_diff = time_zone_diff
        self.point_system = point_system
        self.league_name = self.league_names[league - 1]
        self.content = list()
        self._convert_user_times_json_to_league_csv(league_as_json)
        self.old_content = deepcopy(self.content)

    def __str__(self):
        return str(self.content)

    def __call__(self, league_as_json):
        # Basically it's a refresh
        self.old_content = deepcopy(self.content)
        self._convert_user_times_json_to_league_csv(league_as_json)

    def save(self, file_path):
        with open(file_path + str(self.league) + ".csv", mode='w+', newline='') as f:
            list_writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for row in self.content:
                list_writer.writerow(row)

    def _convert_user_times_json_to_league_csv(self, data):
        self.content = list()
        cur_datetime = (datetime.now() + timedelta(hours=self.time_zone_diff)).strftime("%d.%m.%Y %H:%M")

        players = [player for player in data.keys() if data[player]["league"] == self.league]
        players = sorted(players,
                         key=lambda player: data[player]['total_points'],
                         reverse=True)
        self.content.append([cur_datetime] + players)
        self._write_all_players_times(data, players)
        self._write_all_players_medals(data, players)
        self._write_all_players_total_points(data, players)
        self._write_all_players_total_points_in_upper_league(data, players)
        self._write_all_players_total_time(data, players)
        self.content.append(list())
        self.content.append(["POINT SYSTEM", '', '', '', 'ANNOUNCEMENTS'])
        self._write_legend_and_announcements()

    def _write_all_players_times(self, data, players):
        for track in self.track_list:
            track_times = [data[player]['tracks'][track]['time'] for player in players]
            self.content.append([track] + track_times)

    def _write_all_players_medals(self, data, players):
        for medal_rank in ['gold', 'silver', 'bronze']:
            row_name = medal_rank.capitalize() + " Medals"
            medals = [data[player]['medals'][medal_rank] for player in players]
            self.content.append([row_name] + medals)

    def _write_all_players_total_points(self, data, players):
        row_name = "Total Points"
        total_points = [data[player]['total_points'] for player in players]
        self.content.append([row_name] + total_points)

    def _write_all_players_total_points_in_upper_league(self, data, players):
        if self.league == 1:
            self.content.append(list())
        else:
            upper_league_name = self.league_names[self.league - 2]
            row_name = f"Total Points In {upper_league_name} ({self.league_points_minimum}p to advance)"
            points_in_upper_league = \
                [data[player]['total_points_in_upper_league'] for player in players]
            self.content.append([row_name] + points_in_upper_league)

    def _write_all_players_total_time(self, data, players):
        row_name = "Total Time"
        total_points = [data[player]['total_time'] for player in players]
        self.content.append([row_name] + total_points)

    def _write_legend_and_announcements(self):
        try:
            with open(f"logs/{self.league}.txt", 'r') as league_logs:
                announcements = league_logs.read().splitlines()
                announcements.reverse()
        except FileNotFoundError:
            LOGGER.error("Could not read announcements file")
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
            self.content.append([place, '1:00.00', f"{points}p", '', announcement])
        if i + 1 < len(announcements):
            announcement = announcements[i + 1]
        else:
            announcement = ''
        self.content.append([f">{i+1}th", '1:00.00', '0p', '', announcement])
