from copy import deepcopy
from lib import LOGGER
from .ranking_creator import RankingCreator


class DynamicRankingCreator(RankingCreator):

    @classmethod
    def give_out_points_and_medals_for_all_leagues(cls):
        old_time_trials = deepcopy(cls.time_trials.json)
        cls._reset(cls.time_trials.json.keys(), ["medals",
                                                 "total_points_in_upper_league",
                                                 "total_points",
                                                 "leagues"])
        league = 0
        while True:
            league += 1
            players = cls._get_players_in_league(league)
            cls._give_out_points_and_medals_for_league(players, False)

            players_to_disqualify = cls._get_players_to_disqualify(players)
            next_league_should_be_created = cls.league_players_minimum <= len(players_to_disqualify) < len(players)
            if next_league_should_be_created:
                cls._move_players_to_the_next_league(players_to_disqualify)
                players = cls._get_players_in_league(league)
            cls._give_out_points_and_medals_for_league(players)
            if not next_league_should_be_created:
                break

        if cls.league_count != league:
            LOGGER.info(f"LEAGUE COUNT CHANGED TO {league}!")
            cls.league_count = league
        cls._do_announcements(old_time_trials)
        cls.time_trials.save()

    @classmethod
    def _move_players_to_the_next_league(cls, players):
        for player in players:
            cls.time_trials.json[player]['league'] += 1
            cls.time_trials.json[player]['total_points_in_upper_league'] = cls.time_trials.json[player]['total_points']
        cls._reset(players, ["medals", "total_points"])

    @classmethod
    def __disqualify_filter(cls, player):
        return cls.time_trials.json[player]['total_points'] < cls.league_points_minimum

    @classmethod
    def _get_players_to_disqualify(cls, players):
        players_to_reset = list(filter(cls.__disqualify_filter, players))
        return players_to_reset
