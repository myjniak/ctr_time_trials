from copy import deepcopy
from .ranking_creator import RankingCreator


class FrozenRankingCreator(RankingCreator):

    @classmethod
    def give_out_points_and_medals_for_all_leagues(cls):
        old_time_trials = deepcopy(cls.time_trials.json)
        cls._reset(cls.time_trials.json.keys(), ["medals",
                                                 "total_points_in_upper_league",
                                                 "total_points"])
        cls._put_new_players_to_last_league()
        for league in range(1, cls.league_count+1):
            players = cls._get_players_in_league(league)
            cls._give_out_points_and_medals_for_league(players, False)

        cls._do_announcements(old_time_trials)
        cls.time_trials.save()

    @classmethod
    def _put_new_players_to_last_league(cls):
        for player in cls.time_trials.json:
            if cls.time_trials.json[player]["league"] == 0:
                cls.time_trials.json[player]["league"] = cls.league_count
