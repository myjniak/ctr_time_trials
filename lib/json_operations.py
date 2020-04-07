import json
from .time_conversion import TimeConversion


class JsonOperations:

    @staticmethod
    def load_json(json_path):
        with open(json_path, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {}
        return data

    @staticmethod
    def save_json(json_variable, file_path):
        with open(file_path, "w") as f:
            json.dump(json_variable, f, indent=4, sort_keys=True)

    @staticmethod
    def load_track_id_json(file_path):
        with open(file_path, 'r') as f:
            track_list = f.read().splitlines()
        track_info = dict()
        for track in track_list:
            track_id, name = track.split(maxsplit=1)
            track_info[track_id] = name
        return track_info

    @classmethod
    def apply_json_to_json(cls, json_source, json_target):
        source = cls.load_json(json_source)
        target = cls.load_json(json_target)
        for player, player_info in source.items():
            if 'tracks' in player_info:
                for track in player_info['tracks']:
                    input_time_is_valid = \
                        TimeConversion.str_to_float(source[player]['tracks'][track]["time"], value_on_error=300) != 300
                    if player in target and input_time_is_valid:
                        target[player].setdefault('tracks', {}).setdefault(track, {})["time"] =\
                            source[player]['tracks'][track]["time"]
        cls.save_json(target, json_target)
