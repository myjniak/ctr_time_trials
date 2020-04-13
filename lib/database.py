from .database_independent.league_as_xlsx import LeagueAsXlsx
from .database_independent.jsoner import Jsoner


class Database:
    
    file_paths = str()
    platforms = str()
    time_trials = dict()
    tracks_info = dict()
    track_list = dict()
    user_dict = dict()
    cheat_thresholds = dict()
    player_list = list()
    point_system = list()
    league_names = list()
    league_count = int()
    league_points_minimum = int()
    time_zone_diff = int()
    bots_list = list()
    sheets_raw = list()
    
    @classmethod
    def reload(cls):
        cls.time_trials = Jsoner(cls.file_paths["time_trials_json"])
        cls.tracks_info = Jsoner(cls.file_paths["track_ids"]).json
        cls.track_list = list(cls.tracks_info.keys())
        cls.user_dict = Jsoner(cls.file_paths["user_platform_json"]).json
        cls.cheat_thresholds = Jsoner(cls.file_paths["cheat_threshold_json"]).json
        cls.player_list = [player for player in cls.user_dict.keys()
                           if cls.user_dict[player] in cls.platforms]
        cls.league_count = max([player_info["league"] for player_info in cls.time_trials.json.values()])
        cls.create_non_existing_sheet_objects()

    @classmethod
    def refresh_csvs_content(cls):
        cls.create_non_existing_sheet_objects()
        for sheet in cls.sheets_raw:
            sheet(cls.time_trials.json)

    @classmethod
    def create_non_existing_sheet_objects(cls):
        for league in range(1, cls.league_count + 1):
            existing_leagues = [league_sheet.league for league_sheet in cls.sheets_raw]
            if league not in existing_leagues:
                cls.sheets_raw.append(LeagueAsXlsx(cls.time_trials.json,
                                                   league,
                                                   cls.track_list,
                                                   cls.league_names,
                                                   cls.time_zone_diff,
                                                   cls.point_system,
                                                   cls.league_points_minimum,
                                                   cls.bots_list))

    @classmethod
    def initialize_players_json_structure(cls):
        data = cls.time_trials.json
        for player in [*cls.player_list, *cls.bots_list]:
            data.setdefault(player, {})
            data[player].setdefault('tracks', {})
            data[player].setdefault('medals', {})
            data[player].setdefault('league', 0)
            data[player].setdefault('total_points', 0)
            data[player].setdefault('total_points_in_upper_league', 0)
            for track in cls.track_list:
                data[player].setdefault('tracks', {}).setdefault(track, {})
                data[player]['tracks'][track]['points'] = 0
                data[player]['tracks'][track].setdefault('time', "NO TIME")
                data[player]['tracks'][track].setdefault('medal', None)
