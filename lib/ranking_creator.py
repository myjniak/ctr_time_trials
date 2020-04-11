from copy import deepcopy
from lib.simple_objects.time_conversion import TimeConversion
from .announcements import Announcements
from .database import Database


class RankingCreator(Database):
    def __init__(self, minimum_player_count_in_league):
        self.minimum_player_count_in_league = minimum_player_count_in_league

    def calc_total_time(self):
        for player, player_info in self.time_trials.json.items():
            total_time = 0
            for track in player_info['tracks']:
                track_time = TimeConversion(player_info['tracks'][track]['time']).as_float
                total_time += track_time
            player_info['total_time'] = TimeConversion(total_time).as_str
        self.time_trials.save()

    def give_out_points_and_medals_for_all_leagues(self):
        new_time_trials = self.time_trials.json
        old_time_trials = deepcopy(new_time_trials)
        self._reset_points_medals_and_leagues()
        league = 1
        next_league_should_be_created = True
        while next_league_should_be_created:
            self._give_out_points_and_medals_for_league(league, False)
            next_league_should_be_created = False
            disqualified_counter = 0
            for player_info in new_time_trials.values():
                if player_info['total_points'] < self.league_points_minimum:
                    disqualified_counter += 1
                    if disqualified_counter >= self.minimum_player_count_in_league:
                        next_league_should_be_created = True
                    player_info['league'] += 1
                    player_info['medals'] = {
                        'gold': 0,
                        'silver': 0,
                        'bronze': 0
                    }
                    player_info['total_points_in_upper_league'] = player_info['total_points']
                    player_info['total_points'] = 0
            if not next_league_should_be_created:
                for player_info in new_time_trials.values():
                    if player_info['league'] == league + 1:
                        player_info['league'] -= 1
            self._give_out_points_and_medals_for_league(league)
            league += 1
        self._do_announcements(old_time_trials)
        self.time_trials.save()

    def _reset_points_medals_and_leagues(self):
        for player_info in self.time_trials.json.values():
            player_info['medals'] = {
                'gold': 0,
                'silver': 0,
                'bronze': 0
            }
            player_info['total_points_in_upper_league'] = 0
            player_info['total_points'] = 0
            player_info['league'] = 1

    def _do_announcements(self, old_time_trials):
        announcer = Announcements(self.time_trials.json,
                                  old_time_trials,
                                  self.league_names,
                                  self.track_list)
        announcer.log_league_transfers()
        announcer.log_medals()

    def _give_out_points_and_medals_for_league(self, league, give_medals=True):
        data = self.time_trials.json
        players = [player for player in data.keys() if data[player]["league"] == league]
        for player in players:
            data[player]["total_points"] = 0
            data[player]['medals'] = {
                'gold': 0,
                'silver': 0,
                'bronze': 0
            }
        for track in self.track_list:
            for player in players:
                data[player].setdefault('tracks', {}).setdefault(track, {})
                data[player]['tracks'][track]['points'] = 0
                data[player]['tracks'][track].setdefault('time', "NO TIME")
                data[player]['tracks'][track]['medal'] = None
            players_filtered = list(filter(
                lambda player: TimeConversion(data[player]['tracks'][track]['time']).as_float < 300, players))
            players_sorted = \
                sorted(players_filtered,
                       key=lambda player: TimeConversion(data[player]['tracks'][track]['time']).as_float)
            if len(players_sorted) > len(self.point_system):
                players_sorted = players_sorted[:len(self.point_system)]
            for i, player in enumerate(players_sorted):
                data[player]['tracks'][track]['points'] = self.point_system[i]
                data[player]['total_points'] += self.point_system[i]
                if give_medals:
                    if i == 0:
                        data[player]['medals']['gold'] += 1
                        data[player]['tracks'][track]['medal'] = 'gold'
                    elif i == 1:
                        data[player]['medals']['silver'] += 1
                        data[player]['tracks'][track]['medal'] = 'silver'
                    elif i == 2:
                        data[player]['medals']['bronze'] += 1
                        data[player]['tracks'][track]['medal'] = 'bronze'
        self.time_trials.save()
