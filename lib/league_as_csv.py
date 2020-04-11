import csv
from datetime import datetime, timedelta
from .database import Database
from . import LOGGER


class LeagueAsCsv(Database):

    def __init__(self, league):
        self.league = league
        self.content = list()
        self._convert_user_times_json_to_league_csv()

    def __str__(self):
        return str(self.content)

    def save(self):
        with open(self.file_paths["csv_path"] + str(self.league) + ".csv", mode='w+', newline='') as f:
            list_writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for row in self.content:
                list_writer.writerow(row)

    def _convert_user_times_json_to_league_csv(self):
        data = self.time_trials.json
        cur_datetime = (datetime.now() + timedelta(hours=self.time_zone_diff)).strftime("%d.%m.%Y %H:%M")

        players = [player for player in data.keys() if data[player]["league"] == self.league]
        players = sorted(players,
                         key=lambda player: data[player]['total_points'],
                         reverse=True)
        self.content.append([cur_datetime] + players)
        self._write_all_players_times(players)
        self._write_all_players_medals(players)
        self._write_all_players_total_points(players)
        self._write_all_players_total_points_in_upper_league(players)
        self._write_all_players_total_time(players)
        self.content.append(list())
        self.content.append(["POINT SYSTEM", '', '', '', 'ANNOUNCEMENTS'])
        self._write_legend_and_announcements()

    def _write_all_players_times(self, players):
        for track in self.track_list:
            track_times = [self.time_trials.json[player]['tracks'][track]['time'] for player in players]
            self.content.append([track] + track_times)

    def _write_all_players_medals(self, players):
        for medal_rank in ['gold', 'silver', 'bronze']:
            row_name = medal_rank.capitalize() + " Medals"
            medals = [self.time_trials.json[player]['medals'][medal_rank] for player in players]
            self.content.append([row_name] + medals)

    def _write_all_players_total_points(self, players):
        row_name = "Total Points"
        total_points = [self.time_trials.json[player]['total_points'] for player in players]
        self.content.append([row_name] + total_points)

    def _write_all_players_total_points_in_upper_league(self, players):
        if self.league == 1:
            self.content.append(list())
        else:
            upper_league_name = self.league_names[self.league - 2]
            row_name = f"Total Points In {upper_league_name} ({self.league_points_minimum}p to advance)"
            points_in_upper_league = \
                [self.time_trials.json[player]['total_points_in_upper_league'] for player in players]
            self.content.append([row_name] + points_in_upper_league)

    def _write_all_players_total_time(self, players):
        row_name = "Total Time"
        total_points = [self.time_trials.json[player]['total_time'] for player in players]
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
