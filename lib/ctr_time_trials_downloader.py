import sys
import requests
from json import JSONDecodeError, dumps
from time import time, sleep
from lib.simple_objects.jsoner import Jsoner
from lib.simple_objects.time_conversion import TimeConversion
from .database import Database
from . import LOGGER


class CtrTimeTrialsDownloader(Database):

    def __init__(self, **kwargs):
        self.gamer_search_ban_time = kwargs['gamer_search_ban_time']
        self.page_search_until_bored_time = kwargs['page_search_until_bored_time']
        self.cookie = kwargs['cookie']
        self.page_id_cache = Jsoner(self.file_paths["page_id_cache_json"])
        self.cheat_thresholds = None
        self.ban_timestamp = 0
        self.changes = {}

    @staticmethod
    def get_url_by_gamer(track_id, gamer, platform):
        return f"https://my.callofduty.com/api/papi-client/leaderboards/v2/title/" \
               f"ctr/platform/{platform}/time/alltime/type/1" \
               f"/mode/{track_id}/gamer/{gamer}"

    @staticmethod
    def get_url_by_page(track_id, page, platform):
        return f"https://my.callofduty.com/api/papi-client/leaderboards/v2/title/" \
               f"ctr/platform/{platform}/time/alltime/type/1" \
               f"/mode/{track_id}/page/{page}"

    def get_json_from_url(self, url):
        for _ in range(5):
            try:
                response = requests.get(url, headers={'Cookie': f"ACT_SSO_COOKIE={self.cookie}"}).json()
                break
            except JSONDecodeError as err:
                LOGGER.warning(f"Ups, cos zlego sie wydarzylo:\n"
                               f"{str(err)}")
            except requests.exceptions.ConnectionError as err:
                LOGGER.warning(f"Ups, cos zlego sie wydarzylo:\n"
                               f"{str(err)}")
        else:
            raise ConnectionError("Cos sie z API rozjebalo na amen :(")
        return response

    def get_time_trials_from_url(self, url, player):
        for _ in range(5):
            try:
                response = self.get_json_from_url(url)
                if "message" in response["data"]:
                    if response['data']['message'] == "Not permitted: rate limit exceeded":
                        return {}
                    if response['data']['message'] == "Not permitted: user not found":
                        LOGGER.error("User not permitted? WTF?")
                        raise KeyError()
                    if response['data']['message'] == "No entries for user":
                        return {player: {"time": 0, "rank": 999999, "page": 0}}
                entries = response["data"]["entries"]
                page = response["data"]["page"]
                break
            except KeyError:
                LOGGER.error(f"Bad json structure!!!\n {dumps(response, indent=4)}")
                LOGGER.info("Sleeping 10secs...")
                sleep(10)
        else:
            raise KeyError(f"Bad json structure!!!\n {dumps(response, indent=4)}")
        time_trial_data = dict()
        for entry in entries:
            time_trial_data.setdefault(entry["username"], {})["time"] = entry["values"]["time"]
            time_trial_data[entry["username"]]["rank"] = int(entry["rank"])
            time_trial_data[entry["username"]]["page"] = page
        return time_trial_data

    def load_page_id_where_user_was_found(self, username, track_id):
        data = self.page_id_cache.json
        data.setdefault(username, dict())
        if track_id in data[username]:
            return data[username][track_id]
        else:
            page_list = []
            for other_username, track_ids in data.items():
                if str(track_id) in track_ids.keys():
                    page_list.append(int(data[other_username][track_id]))
            if page_list:
                return int(sum(page_list)/len(page_list))
            else:
                return 1

    def save_page_where_user_was_found(self, username, track_id, page_id):
        if page_id == 0:
            return
        self.page_id_cache.json.setdefault(username, {})[track_id] = page_id
        self.page_id_cache.save()

    def save_user_time(self, username, track_name, user_time, place):
        data = self.time_trials
        data.json.setdefault(username, {}).setdefault('tracks', {}).setdefault(track_name, {}).setdefault("time", "0")
        if user_time not in [data.json.[username]['tracks'][track_name]["time"], "CHEATER", "NO TIME"]:
            self.changes.setdefault(username, {}).setdefault('tracks', {}).setdefault(track_name, {})
            self.changes[username]['tracks'][track_name]["time"] = user_time
        data.json[username]['tracks'][track_name]["time"] = user_time
        data.json[username]['tracks'][track_name]["place"] = place
        data.save()

    def get_username_time(self, username, track_id):
        init_page = self.load_page_id_where_user_was_found(username, track_id)
        page = init_page
        left = (page - 1) * 20 + 1
        right = page * 20
        platform = self.user_dict[username]
        time_trials = dict()
        timer_start = time()
        while True:
            if self.ban_timestamp:
                time_until_search_by_gamer_ban_ends = self.gamer_search_ban_time - (time() - self.ban_timestamp)
                LOGGER.info(f"Time until player search ban ends: {time_until_search_by_gamer_ban_ends}")
            else:
                time_until_search_by_gamer_ban_ends = 0
            time_passed_searching_by_page = time() - timer_start
            sys.stdout.write(f"\rSzukam w przedziale miejsc {left}-{right}             ")
            sys.stdout.flush()
            if track_id in self.page_id_cache.json[username]:
                new_time_trials = self.get_time_trial_with_cache(track_id, username, page, platform,
                                                                 time_passed_searching_by_page,
                                                                 time_until_search_by_gamer_ban_ends)
            else:
                new_time_trials = self.get_time_trial_without_cache(track_id, username, page, platform,
                                                                    time_until_search_by_gamer_ban_ends)
            time_trials = {**time_trials, **new_time_trials}
            if not new_time_trials:
                self.ban_timestamp = time()
                LOGGER.info("\nAPI wants to sleep, we'll have to seach manually...")
            if username in time_trials:
                sys.stdout.write("\r                                               ")
                sys.stdout.flush()
                self.save_page_where_user_was_found(username, track_id, time_trials[username]["page"])
                return time_trials[username]

            old_page = page
            page = self.evaluate_next_page_id(page, init_page)
            if page > old_page:
                right += 20
            else:
                left -= 20

    def get_time_trial_without_cache(self, track_id, username, page, platform, time_until_ban_ends):
        if platform == 'switch':
            url = self.get_url_by_page(track_id, page, platform)
        elif time_until_ban_ends <= 0:
            LOGGER.debug("Checking time by gamer")
            url = self.get_url_by_gamer(track_id, username, platform)
        else:
            LOGGER.info(f"Time until ban ends: {time_until_ban_ends}")
        new_time_trials = self.get_time_trials_from_url(url, username)
        return new_time_trials

    def get_time_trial_with_cache(self, track_id, username, page, platform, time_passed_searching_by_page,
                                  time_until_ban_ends):
        if platform == 'switch' or time_passed_searching_by_page < self.page_search_until_bored_time:
            url = self.get_url_by_page(track_id, page, platform)
        elif time_until_ban_ends <= 0:
            LOGGER.info("OK, I'm bored, checking by gamer!")
            url = self.get_url_by_gamer(track_id, username, platform)
        else:
            LOGGER.info(f"Time until ban ends: {time_until_ban_ends}")
        new_time_trials = self.get_time_trials_from_url(url, username)
        return new_time_trials

    @staticmethod
    def evaluate_next_page_id(page_id, init_page):
        delta = page_id - init_page
        if delta > 0:
            if init_page - delta >= 1:
                return init_page - delta
            else:
                return page_id + 1
        else:
            return init_page - delta + 1

    def get_usernames_times(self, usernames, tracks_info=None):
        if not tracks_info:
            tracks_info = self.tracks_info
        thresholds = self.cheat_thresholds
        users_times = dict()
        for track_name, track_id in tracks_info.items():
            for username in usernames:
                LOGGER.info(f"Szukam rekordu {username} na trasie {track_name}...")
                user_record = self.get_username_time(username, track_id)
                # blad w API - dodaje sekunde do wszystkiego
                user_record["time"] -= 1
                pretty_user_time = TimeConversion(user_record["time"]).as_str
                place = user_record["rank"]

                if user_record["time"] <= 0:
                    LOGGER.info("NO ENTRY")
                    pretty_user_time = "NO TIME"
                    place = 999999
                elif user_record["time"] < thresholds[track_name]:
                    LOGGER.info("CHEATER!")
                    pretty_user_time = "CHEATER"
                    place = 999999
                LOGGER.debug(f"\rCzas: {pretty_user_time} Pozycja: {place}                      \n")
                self.save_user_time(username, track_name, pretty_user_time, place)
                users_times.setdefault(username, {})[track_name] = pretty_user_time
        return users_times
