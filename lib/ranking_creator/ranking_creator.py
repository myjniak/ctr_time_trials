from lib.database_independent.time_conversion import Time
from lib.database_independent.announcements import Announcements
from lib.database import Database


class RankingCreator(Database):

    @classmethod
    def calc_total_time(cls):
        for player, player_info in cls.time_trials.json.items():
            total_time = Time("0:00:00")
            for track in player_info['tracks']:
                track_time = Time(player_info['tracks'][track]['time'])
                total_time += track_time
            player_info['total_time'] = str(total_time)
        cls.time_trials.save()

    @classmethod
    def _move_players_to_the_next_league(cls, players):
        for player in players:
            cls.time_trials.json[player]['league'] += 1
            cls.time_trials.json[player]['total_points_in_upper_league'] = cls.time_trials.json[player]['total_points']
        cls._reset(players, ["medals", "total_points"])

    @classmethod
    def _get_players_in_league(cls, league):
        return [player for player in cls.time_trials.json.keys() if cls.time_trials.json[player]["league"] == league]

    @classmethod
    def _get_players_in_leagues(cls, leagues):
        return [player for player in cls.time_trials.json.keys() if cls.time_trials.json[player]["league"] in leagues]

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
                # data[player]['tracks'][track]['time'] = str(Time(data[player]['tracks'][track]['time']))
            players_times_dict = {player: float(Time(data[player]['tracks'][track]['time']))
                                  for player in players_in_league}
            players_times_filtered = dict(filter(lambda item: item[1] < 300, players_times_dict.items()))
            players_sorted = sorted(list(players_times_filtered.keys()), key=lambda player: players_times_dict[player])
            if len(players_sorted) > len(cls.point_system):
                players_sorted = players_sorted[:len(cls.point_system)]
            tie_count = 1
            points_granted = 0
            for i, player in enumerate(players_sorted):
                if tie_count > 1:
                    tie_count -= 1
                else:
                    tie_count = len(list(filter(lambda p: players_times_dict[p] == players_times_dict[player],
                                                players_sorted)))
                    points_granted = sum(cls.point_system[i:i + tie_count])/tie_count
                data[player]['tracks'][track]['points'] = points_granted
                data[player]['total_points'] += points_granted
                if give_medals:
                    if points_granted > cls.point_system[1]:
                        data[player]['medals']['gold'] += 1
                        data[player]['tracks'][track]['medal'] = 'gold'
                    elif points_granted > cls.point_system[2]:
                        data[player]['medals']['silver'] += 1
                        data[player]['tracks'][track]['medal'] = 'silver'
                    elif points_granted > cls.point_system[3]:
                        data[player]['medals']['bronze'] += 1
                        data[player]['tracks'][track]['medal'] = 'bronze'
        for player in players_in_league:
            data[player]['total_points'] = int(data[player]['total_points'])
        cls.time_trials.save()
