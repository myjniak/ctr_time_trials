import sys
import requests
import json
import csv
from datetime import timedelta


def convert_json_to_csv(file_path="user_times.json"):
    with open(file_path, "r") as f:
        data = json.load(f)
    with open("rekordy.csv", mode='w+', newline='') as f:
        file_writer = csv.writer(f,
                                 delimiter=',',
                                 quotechar='"',
                                 quoting=csv.QUOTE_MINIMAL)
        file_writer.writerow(list(load_track_list().values()))
        for user, track_times in data.items():
            times = track_times.values()
            file_writer.writerow([user] + list(times))


def load_track_list():
    with open("tracks.txt", 'r') as f:
        track_list = f.read().splitlines()
    track_info = dict()
    for track in track_list:
        track_id, name = track.split(maxsplit=1)
        track_info[track_id] = name
    return track_info


def get_url(track_id, page):
    return f"https://my.callofduty.com/api/papi-client/leaderboards/v2/title/" \
           f"ctr/platform/psn/time/alltime/type/1" \
           f"/mode/{track_id}/page/{page}"


def get_json_from_url(url):
    response = requests.get(url, timeout=10)
    return response.json()


def get_time_trials_from_url(url):
    response = get_json_from_url(url)
    entries = response["data"]["entries"]
    time_trial_data = dict()
    for entry in entries:
        time_trial_data[entry["username"]] = entry["values"]["time"]
    return time_trial_data


def load_cache_data():
    with open("page_id_cache.json", "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = {}
    return data


def load_page_id_where_user_was_found(username, track_id):
    data = load_cache_data()
    try:
        return data[username][track_id]
    except KeyError:
        for other_username, track_ids in data.items():
            page_list = []
            if track_id in track_ids.keys():
                page_list.append(int(data[other_username][track_id]))
        if page_list:
            return int(sum(page_list)/len(page_list))
        else:
            return 1


def save_page_where_user_was_found(username, track_id, page_id):
    data = load_cache_data()
    data.setdefault(username, {})[track_id] = page_id
    with open("page_id_cache.json", "w") as f:
        json.dump(data, f, indent=4, sort_keys=True)


def save_user_time(username, track_name, user_time):
    with open("user_times.json", "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = {}
    data.setdefault(username, {})[track_name] = user_time
    with open("user_times.json", "w") as f:
        json.dump(data, f, indent=4, sort_keys=True)


def get_username_time(username, track_id, init_page=7, time_trials={}):
    page = init_page
    left = (page - 1) * 20 + 1
    right = page * 20
    if username in time_trials:
        return time_trials[username]
    while True:
        sys.stdout.write(f"\rSzukam w przedziale miejsc {left}-{right}             ")
        sys.stdout.flush()
        url = get_url(track_id, page)
        time_trials = {**time_trials, **get_time_trials_from_url(url)}
        if username in time_trials:
            sys.stdout.write("\r                                               ")
            sys.stdout.flush()
            save_page_where_user_was_found(username, track_id, page)
            return time_trials[username]
        old_page = page
        page = evaluate_next_page_id(page, init_page)
        if page > old_page:
            right += 20
        else:
            left -= 20


def evaluate_next_page_id(page_id, init_page):
    delta = page_id - init_page
    if delta > 0:
        if init_page - delta >= 1:
            return init_page - delta
        else:
            return page_id + 1
    else:
        return init_page - delta + 1


def convert_time_to_pretty_time(time_in_seconds):
    hh_mm_ss_msmsms = str(timedelta(seconds=time_in_seconds))
    for i, char in enumerate(hh_mm_ss_msmsms):
        if char == "0" or char == ":":
            continue
        else:
            return hh_mm_ss_msmsms[i:]


def get_usernames_times(usernames):
    tracks = load_track_list()
    users_times = dict()
    for track_id, track_name in tracks.items():
        all_user_times = dict()
        for username in usernames:
            last_time_found_page_id = load_page_id_where_user_was_found(username, track_id)
            print(f"Szukam rekordu {username} na trasie {track_name}...")
            user_time = get_username_time(username,
                                          track_id,
                                          init_page=last_time_found_page_id,
                                          time_trials=all_user_times)
            #blad w API - dodaje sekunde do wszystkiego
            user_time -= 1
            pretty_user_time = convert_time_to_pretty_time(user_time)
            print(f"\rCzas: {pretty_user_time}                       \n")
            save_user_time(username, track_name, user_time)
            users_times.setdefault(username, {})[track_name] = pretty_user_time
    return users_times


print("Dej nicki, których time triale chcesz sciagnac. Jak skonczysz wpisywac"
      " nicki, kliknij Enter dwa razy. Wpisz nicki poprawnie, bo bede szukal w nieskonczonosc!")
gamers = []
while True:
    gamer = input("Dej nick: ")
    if not gamer:
        break
    gamers.append(gamer)
#get_usernames_times(["myjniak", "mati1212", "Wajsia"])
get_usernames_times(gamers)
convert_json_to_csv()