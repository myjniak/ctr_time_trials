from .database_independent.jsoner import Jsoner
from .database import Database
from .database_independent.time_conversion import TimeConversion
from . import LOGGER


class GrandPrix(Database):

    def __init__(self):
        self.settings = Jsoner("config/grand_prix.json").json
        self.gp_start_snapshot = Jsoner("dynamic_jsons/user_times_snapshot.json").json
        self.ranking_json = dict()

    @classmethod
    def gp_start(cls):
        LOGGER.info("STARTING GRAND PRIX")
        LOGGER.info("EVALUATING QUALIFIED PLAYERS")
        gp_json = Jsoner("config/grand_prix.json")
        Database.reload()
        qualified_players = cls.get_player_list_qualified_for_gp()
        gp_json.json["players"] = qualified_players
        gp_json.save()
        gp_snapshot = Jsoner("dynamic_jsons/user_times.json")
        gp_snapshot.save("dynamic_jsons/user_times_snapshot.json")

    @classmethod
    def get_player_list_qualified_for_gp(cls):
        qualified_players = list()
        time_trials = cls.time_trials.json
        invalids = ["NO TIME", "CHEATER"]
        for player in time_trials:
            if player in Database.bots_list:
                continue
            if all([track_stats["time"] not in invalids for track_stats in time_trials[player]["tracks"].values()]):
                qualified_players.append(player)
        return qualified_players

    @property
    def ranking(self):
        self.calc_gp_json()
        return self.ranking_json

    def calc_final_ranking(self, player):
        points = self.ranking_json[player]["total_points"]
        points_improved = self.ranking_json[player]["total_points_improved"]
        time_improved = self.ranking_json[player]["total_time_improved"]
        self.ranking_json[player]["ranking"] = max(points + 5*points_improved, 1) * time_improved

    def get_time(self, player, track, from_snapshot=False):
        if from_snapshot:
            return TimeConversion(self.gp_start_snapshot[player]['tracks'][track]['time']).as_float
        else:
            return TimeConversion(self.time_trials.json[player]['tracks'][track]['time']).as_float

    def calc_gp_json(self):
        players = self.settings["players"]
        point_system = self.calc_point_system(len(players))
        for track in self.settings['tracks']:
            players_sorted = sorted(players, key=lambda player: self.get_time(player, track))
            for place, player in enumerate(players_sorted):
                self.ranking_json.setdefault(player, dict()).setdefault("tracks", dict()).setdefault(track, dict())
                new_time = self.get_time(player, track)
                old_time = self.get_time(player, track, True)
                self.ranking_json[player]["tracks"][track]["time_improvement"] = old_time - new_time
                self.ranking_json[player]["tracks"][track]["new_place"] = place + 1
                self.ranking_json[player]["tracks"][track]["points"] = point_system[place]
                self.ranking_json[player].setdefault("total_points", 0)
                self.ranking_json[player]["total_points"] += point_system[place]
                self.ranking_json[player].setdefault("total_time_improved", 0)
                self.ranking_json[player]["total_time_improved"] += old_time - new_time
            players_sorted = sorted(players, key=lambda player: self.get_time(player, track, True))
            for place, player in enumerate(players_sorted):
                track_stats = self.ranking_json[player]["tracks"][track]
                track_stats["old_place"] = place + 1
                track_stats["place_improvement"] = track_stats["old_place"] - track_stats["new_place"]
                track_stats["old_points"] = point_system[place]
                self.ranking_json[player].setdefault("old_total_points", 0)
                self.ranking_json[player]["old_total_points"] += point_system[place]
                self.ranking_json[player].setdefault("total_places_improved", 0)
                self.ranking_json[player]["total_places_improved"] += track_stats["place_improvement"]
            for player in players:
                new_points = self.ranking_json[player]["total_points"]
                old_points = self.ranking_json[player]["old_total_points"]
                self.ranking_json[player]["total_points_improved"] = new_points - old_points
                self.calc_final_ranking(player)

    @staticmethod
    def calc_point_system(player_count):
        point_system = list()
        for i in range(player_count):
            if i <= 2:
                point_system.append(i)
            else:
                point_system.append(point_system[i - 1] + i - 1)
        point_system.reverse()
        return point_system

