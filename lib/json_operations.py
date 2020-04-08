import json
import logging
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
    def apply_json_to_json(cls, json_source, json_target, verbose=False):
        logging.info(f"Applying {json_source}...")
        source = cls.load_json(json_source)
        target = cls.load_json(json_target)
        for player, player_info in source.items():
            if 'tracks' in player_info:
                for track in player_info['tracks']:
                    input_time_as_float = \
                        TimeConversion.str_to_float(source[player]['tracks'][track]["time"], value_on_error=300)
                    for registered_player in target:
                        if player.lower() == registered_player.lower():
                            exact_player_name = registered_player
                            break
                    else:
                        break
                    if input_time_as_float != 300:
                        pretty_input_time = TimeConversion.float_to_str(input_time_as_float)
                        target[exact_player_name].setdefault('tracks', {}).setdefault(track, {})["time"] =\
                            pretty_input_time
                        if verbose:
                            logging.info(f"{exact_player_name}: {track}: {pretty_input_time}")
        cls.save_json(target, json_target)
