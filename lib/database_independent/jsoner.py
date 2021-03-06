import json
import os
from .time_conversion import Time
from . import LOGGER


class Jsoner:

    def __init__(self, json_input):
        self.json_filepath = None
        self.json_as_variable = None
        if isinstance(json_input, str) and os.path.isfile(json_input):
            self.json_filepath = json_input
            self.json_as_variable = self._load_json(json_input)
        elif isinstance(json_input, list):
            self.json_as_variable = self._convert_csv_to_json(json_input)
        elif isinstance(json_input, dict):
            self.json_as_variable = json_input

    @property
    def json(self):
        return self.json_as_variable

    @property
    def path(self):
        return self.json_filepath

    def save(self, filepath=None):
        if filepath is None:
            if self.json_filepath:
                filepath = self.json_filepath
            else:
                raise ValueError("JSON filepath not provided!")
        with open(filepath, "w") as f:
            json.dump(self.json_as_variable, f, indent=4, sort_keys=True)

    def apply_json_to_self(self, json_path, verbose=False):
        LOGGER.info(f"Applying {json_path}...")
        source = Jsoner._load_json(json_path)
        target = self.json_as_variable
        for player, player_info in source.items():
            if 'tracks' in player_info:
                for track in player_info['tracks']:
                    for registered_player in target:
                        if player.lower().strip() == registered_player.lower():
                            exact_player_name = registered_player
                            break
                    else:
                        LOGGER.warning(f"Bullshit PLAYER input: '{player}'\n"
                                       f"Available player list: {list(target.keys())}")
                        LOGGER.debug(source)
                        break
                    input_time = Time(source[player]['tracks'][track]['time'])
                    current_time = Time(target[exact_player_name]['tracks'][track]['time'])
                    if float(input_time) < 299:
                        if verbose:
                            LOGGER.info(f"{exact_player_name}: {track}: new time:{str(input_time)}")
                            if float(input_time) > float(current_time):
                                LOGGER.warn(f"Worse time input detected: {str(current_time)} -> {str(input_time)}")
                        target[exact_player_name].setdefault('tracks', {}).setdefault(track, {})
                        target[exact_player_name]['tracks'][track]['time'] = str(input_time)
                    else:
                        LOGGER.warning(f"Bullshit TIME input: {source[player]['tracks'][track]['time']}")
                        LOGGER.debug(source)

    @classmethod
    def _convert_csv_to_json(cls, csv_content):
        LOGGER.info(f"Converting CSV to JSON")
        output_json = dict()
        for col, player in enumerate(csv_content[0]):
            if col == 0:
                continue
            if player:
                for row in csv_content[1:]:
                    if row and row[0]:
                        track = row[0]
                    else:
                        LOGGER.error("Someone added a row / column to the Input excel!!!")
                    if col < len(row) and row[col]:
                        output_json.setdefault(player, dict()).setdefault('tracks', dict()).setdefault(track, dict())
                        output_json[player]['tracks'][track]['time'] = row[col]
        return output_json

    @staticmethod
    def _load_json(json_path):
        with open(json_path, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {}
        return data
