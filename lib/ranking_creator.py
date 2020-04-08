from copy import deepcopy
from .json_operations import JsonOperations
from .time_conversion import TimeConversion
from .announcements import Announcements


class RankingCreator:
    def __init__(self, time_trials_file, league_names, track_list,
                 minimum_player_count_in_league, league_points_minimum, point_system):
        self.time_trials_file = time_trials_file
        self.league_names = league_names
        self.track_list = track_list
        self.point_system = point_system
        self.league_points_minimum = league_points_minimum
        self.minimum_player_count_in_league = minimum_player_count_in_league
        self.time_trials = None
        self.refresh()

    def refresh(self):
        self.time_trials = JsonOperations.load_json(self.time_trials_file)

    def calc_total_time(self):
        for player, player_info in self.time_trials.items():
            total_time = 0
            for track in player_info['tracks']:
                track_time = TimeConversion.str_to_float(player_info['tracks'][track]['time'])
                total_time += track_time
            player_info['total_time'] = TimeConversion.float_to_str(total_time)
        JsonOperations.save_json(self.time_trials, self.time_trials_file)

    def reset_points_medals_and_leagues(self):
        for player_info in self.time_trials.values():
            player_info['medals'] = {
                'gold': 0,
                'silver': 0,
                'bronze': 0
            }
            player_info['total_points_in_upper_league'] = 0
            player_info['total_points'] = 0
            player_info['league'] = 1

    def give_out_points_and_medals_for_all_leagues(self):
        old_time_trials = deepcopy(self.time_trials)
        self.reset_points_medals_and_leagues()
        league = 1
        next_league_should_be_created = True
        while next_league_should_be_created:
            self.give_out_points_and_medals_for_league(league, False)
            next_league_should_be_created = False
            disqualified_counter = 0
            for player_info in self.time_trials.values():
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
                for player_info in self.time_trials.values():
                    if player_info['league'] == league + 1:
                        player_info['league'] -= 1
            self.give_out_points_and_medals_for_league(league)
            league += 1
        self.do_announcements(old_time_trials)
        JsonOperations.save_json(self.time_trials, self.time_trials_file)

    def do_announcements(self, old_time_trials):
        announcer = Announcements(self.time_trials,
                                  old_time_trials,
                                  self.league_names,
                                  self.track_list)
        announcer.log_league_transfers()
        announcer.log_medals()

    def give_out_points_and_medals_for_league(self, league, give_medals=True):
        data = self.time_trials
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
            players_competing = [player for player in players if track in data[player]['tracks']]
            players_sorted = \
                sorted(players_competing,
                       key=lambda player: TimeConversion.str_to_float(data[player]['tracks'][track]["time"]))
            if len(players_sorted) > len(self.point_system):
                players_sorted = players_sorted[:len(self.point_system)]
            for i, player in enumerate(players_sorted):
                data[player]['tracks'][track]["points"] = self.point_system[i]
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
        JsonOperations.save_json(data, self.time_trials_file)
