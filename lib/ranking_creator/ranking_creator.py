from lib.database_independent.time_conversion import TimeConversion
from lib.database_independent.announcements import Announcements
from lib.database import Database


class RankingCreator(Database):

    @classmethod
    def calc_total_time(cls):
        for player, player_info in cls.time_trials.json.items():
            total_time = 0
            for track in player_info['tracks']:
                track_time = TimeConversion(player_info['tracks'][track]['time']).as_float
                total_time += track_time
            player_info['total_time'] = TimeConversion(total_time).as_str
        cls.time_trials.save()

    @classmethod
    def _move_players_to_the_next_league(cls, players):
        for player in players:
            cls.time_trials.json[player]['league'] += 1
            cls.time_trials.json[player]['total_points_in_upper_league'] = cls.time_trials.json[player]['total_points']
        cls._reset(players, ["medals",
                             "total_points_in_upper_league",
                             "total_points"])

    @classmethod
    def __disqualify_filter(cls, player):
        return cls.time_trials.json[player]['total_points'] < cls.league_points_minimum

    @classmethod
    def _get_players_to_reset(cls, players):
        players_to_reset = list(filter(cls.__disqualify_filter, players))
        return players_to_reset

    @classmethod
    def _get_players_in_league(cls, league):
        return [player for player in cls.time_trials.json.keys() if cls.time_trials.json[player]["league"] == league]

    @classmethod
    def _reset(cls, players, things_to_reset):
        for player in players:
            player_info = cls.time_trials.json[player]
            if "medals" in things_to_reset:
                player_info['medals'] = {
                    'gold': 0,
                    'silver': 0,
                    'bronze': 0
                }
            if "total_points_in_upper_league" in things_to_reset:
                player_info['total_points_in_upper_league'] = 0
            if "total_points" in things_to_reset:
                player_info['total_points'] = 0
            if "leagues" in things_to_reset:
                player_info['league'] = 1

    @classmethod
    def _do_announcements(cls, old_time_trials):
        announcer = Announcements(cls.time_trials.json,
                                  old_time_trials,
                                  cls.league_names,
                                  cls.track_list)
        announcer.log_league_transfers()
        announcer.log_medals()

    @classmethod
    def _give_out_points_and_medals_for_league(cls, players_in_league, give_medals=True):
        data = cls.time_trials.json
        cls._reset(players_in_league, ["medals", "total_points"])
        for track in cls.track_list:
            for player in players_in_league:
                data[player].setdefault('tracks', {}).setdefault(track, {})
                data[player]['tracks'][track]['points'] = 0
                data[player]['tracks'][track].setdefault('time', "NO TIME")
                data[player]['tracks'][track]['medal'] = None
            players_filtered = list(filter(
                lambda player: TimeConversion(data[player]['tracks'][track]['time']).as_float < 300, players_in_league))
            players_sorted = \
                sorted(players_filtered,
                       key=lambda player: TimeConversion(data[player]['tracks'][track]['time']).as_float)
            if len(players_sorted) > len(cls.point_system):
                players_sorted = players_sorted[:len(cls.point_system)]
            for i, player in enumerate(players_sorted):
                data[player]['tracks'][track]['points'] = cls.point_system[i]
                data[player]['total_points'] += cls.point_system[i]
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
        cls.time_trials.save()
