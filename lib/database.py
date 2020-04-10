from .json_operations import JsonOperations


class Database:
    
    file_paths = str()
    platforms = str()
    time_trials = dict()
    tracks_by_ids = dict()
    track_list = dict()
    user_dict = dict()
    cheat_thresholds = dict()
    player_list = list()
    
    @classmethod
    def load(cls):
        cls.time_trials = JsonOperations.load_json(cls.file_paths["time_trials_json"])
        cls.tracks_by_ids = JsonOperations.load_track_id_json(cls.file_paths["track_ids"])
        cls.track_list = list(cls.tracks_by_ids.values())
        cls.user_dict = JsonOperations.load_json(cls.file_paths["user_platform_json"])
        cls.cheat_thresholds = JsonOperations.load_json(cls.file_paths["cheat_threshold_json"])
        cls.player_list = [player for player in cls.user_dict.keys()
                           if cls.user_dict[player] in cls.platforms]

    @classmethod
    def initialize_players_json_structure(cls):
        for player in [*cls.player_list, "N. Tropy", "Oxide", "Velo", "Beenox"]:
            cls.time_trials.setdefault(player, {})
            cls.time_trials[player].setdefault('tracks', {})
            cls.time_trials[player].setdefault('medals', {})
            cls.time_trials[player].setdefault('league', 0)
            cls.time_trials[player].setdefault('total_points', 0)
            cls.time_trials[player].setdefault('total_points_in_upper_league', 0)
            for track in cls.track_list:
                cls.time_trials[player].setdefault('tracks', {}).setdefault(track, {})
                cls.time_trials[player]['tracks'][track]['points'] = 0
                cls.time_trials[player]['tracks'][track].setdefault('time', "NO TIME")
                cls.time_trials[player]['tracks'][track].setdefault('medal', None)
        JsonOperations.save_json(cls.time_trials, cls.file_paths["time_trials_json"])
