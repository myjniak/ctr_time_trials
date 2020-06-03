import argparse
import logging
import traceback
import os
from time import sleep, time
from lib.google.google_requests import GoogleRequests
from lib.leagues_as_xlsx import LeaguesAsXlsx
from lib.database import Database
from lib.database_independent.jsoner import Jsoner
from lib.ranking_creator.dynamic_ranking_creator import DynamicRankingCreator
from lib.ranking_creator.frozen_ranking_creator import FrozenRankingCreator
from lib.database_independent.announcements import Announcements
from lib.grand_prix import GrandPrix
from lib.database_independent.grand_prix_as_xlsx import GrandPrixAsXlsx
from lib.database_independent.grand_prix_as_csv import GrandPrixAsCsv
from confidential.variables import *


FREEZE_LEAGUES = False
USER_TIMES_SNAPSHOT_FILE_PATH = "dynamic_jsons/GP1_start.json"
LOGS_PATH = 'logs/'
BOTS_LIST = ["N. Tropy", "Oxide", "Velo", "Beenox"]
POINT_SYSTEM = [10, 8, 6, 5, 4, 3, 2, 1]
LEAGUE_POINTS_MINIMUM = 20
LEAGUE_PLAYERS_MINIMUM = 5
SHEET_IDS_FILE_PATH = "config/sheet_ids.json"
LOG_RESET_INTERVAL = 10000
TIMES_FROM_WEBPAGE_JSON_FILE_PATH = "dynamic_jsons/manual_times_from_webpage.json"
LEAGUE_NAMES = ["Nitro Tier", "Platinum Tier", "Gold Tier", "Sapphire Tier", "Wumpa Tier", "Armadillo Tier",
                "Tier 7", "Tier 8", "Tier 9"]
FILE_PATHS = {
    "cheat_threshold_json": "config/cheat_thresholds.json",
    "track_ids": "config/tracks.json",
    "user_platform_json": "config/user_list.json",
    "time_trials_json": "dynamic_jsons/user_times.json",
    "page_id_cache_json": "dynamic_jsons/page_id_cache.json",
    "csv_path": "output/time_trial_ranking",
    "xlsx_path": "output/time_trial_ranking.xlsx"
}
GOOGLE_DRIVE_CREDENTIALS_PATH = "confidential/credentials.json"
GOOGLE_DRIVE_TOKEN_PATH = "confidential/token.pickle"
INPUT_EXCEL_FILE_PATH = "output/times_from_webpage.xlsx"
INPUT_TEMPLATE_EXCEL_FILE_PATH = "config/CTR TT INPUT template.xlsx"
PLATFORMS = ['psn', 'xbl', 'switch']
GAMER_SEARCH_BAN_TIME = 800
PAGE_SEARCH_UNTIL_BORED_TIME = 5
SLEEP_BETWEEN_ITERATIONS = 5
TIME_ZONE_DIFF = 7
logging.basicConfig(filename=f"{LOGS_PATH}logs.txt",
                    level=logging.WARNING,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


def prepare_database():
    Announcements.logs_path = LOGS_PATH
    Database.platforms = PLATFORMS
    Database.file_paths = FILE_PATHS
    Database.bots_list = BOTS_LIST
    Database.point_system = POINT_SYSTEM
    Database.league_names = LEAGUE_NAMES
    Database.league_points_minimum = LEAGUE_POINTS_MINIMUM
    Database.time_zone_diff = TIME_ZONE_DIFF
    Database.freeze_leagues = FREEZE_LEAGUES
    Database.league_players_minimum = LEAGUE_PLAYERS_MINIMUM


def przytnij_logi_i_ogloszenia(logs_msg_count=50000, announcements_msg_count=10):
    LOGGER.debug("Przycinam logi")
    file_list = os.listdir(LOGS_PATH)
    for f in file_list:
        if f.endswith('txt') and not f.startswith("logs"):
            msg_count = announcements_msg_count
        else:
            msg_count = logs_msg_count
        with open(LOGS_PATH + f, 'r') as log:
            data = log.read().splitlines(True)
        with open(LOGS_PATH + f, 'w') as log:
            log.writelines(data[-msg_count:])


def reset_input_sheet(serwis):
    LOGGER.debug("Resetuje arkusz do inputu...")
    serwis.upload_file("config/Time Trial Input.xlsx", RANKING_INPUT_FILE_ID)
    serwis.protect_first_column(RANKING_INPUT_FILE_ID, MASTER_EMAIL)


def main(static=None, frozen=None, gp_start=None, gp=None):
    prepare_database()
    if gp_start:
        GrandPrix.gp_start()
        return

    if frozen:
        rankingowaczka = FrozenRankingCreator()
    else:
        rankingowaczka = DynamicRankingCreator()
    if static:
        main_loop_static(rankingowaczka, gp)
    else:
        for i in range(3):
            try:
                serwis = GoogleRequests(GOOGLE_DRIVE_CREDENTIALS_PATH,
                                        GOOGLE_DRIVE_TOKEN_PATH,
                                        GOOGLE_SHEETS_API_KEY)
                main_loop(serwis, rankingowaczka, gp)
            except:
                formatted_lines = traceback.format_exc().splitlines()
                for line in formatted_lines:
                    LOGGER.error(line)
                prepare_database()
        else:
            LOGGER.error("FATAL ERROR - CRASHED 3 TIMES")


def main_loop_static(rankingowaczka, gp):
    przytnij_logi_i_ogloszenia()
    Database.reload()
    Database.initialize_players_json_structure()
    Database.time_trials.apply_json_to_self("config/challenge_ghosts.json")

    # Zarankinguj w user_times.json
    rankingowaczka.give_out_points_and_medals_for_all_leagues()
    rankingowaczka.calc_total_time()

    # Zapisz update do jsona i excela
    Database.refresh_csvs_content()
    Database.time_trials.save()
    LeaguesAsXlsx.save()

    if gp:
        GrandPrixAsXlsx(GrandPrix().ranking).save("output/grand_prix.xlsx")

    LOGGER.info("ROBOTA SKONCZONA")


def main_loop(serwis, rankingowaczka, gp):
    sheet_ids = Jsoner(SHEET_IDS_FILE_PATH)
    last_log_reset_time = time()
    grand_prix = GrandPrix()
    while True:
        if serwis.get_cell_value(RANKING_INPUT_FILE_ID, "A1"):
            Database.reload()
            Database.initialize_players_json_structure()

            # Sciagnij inputowy eksel, zapisz go w postaci JSON i zaaplikuj do user_times.json
            input_as_csv = serwis.get_range_value(RANKING_INPUT_FILE_ID, "A1:Z50")
            Jsoner(input_as_csv).save(TIMES_FROM_WEBPAGE_JSON_FILE_PATH)
            Database.time_trials.apply_json_to_self(TIMES_FROM_WEBPAGE_JSON_FILE_PATH, verbose=True)

            # Wyczysc input na serwerze
            reset_input_sheet(serwis)

            # Zaaplikuj ponownie boty
            Database.time_trials.apply_json_to_self("config/challenge_ghosts.json")

            # Zarankinguj user_times.json
            rankingowaczka.give_out_points_and_medals_for_all_leagues()
            rankingowaczka.calc_total_time()

            # Zapisz update do jsona i do raw data pod excele
            Database.time_trials.save()
            Database.refresh_csvs_content()

            # Dodaj nowe sheet id jak pojawily sie nowe
            new_sheet_ids = serwis.update_sheet_ids(RANKING_FILE_ID, Database.sheets_raw, sheet_ids.json)
            if new_sheet_ids != sheet_ids.json:
                sheet_ids.json_as_variable = new_sheet_ids
                sheet_ids.save()

            # Wrzuc na google drive
            serwis.update_leagues(RANKING_FILE_ID, Database.sheets_raw, sheet_ids.json)

            if gp:
                grand_prix_ranking = grand_prix.ranking
                serwis.update_grand_prix(GRAND_PRIX_FILE_ID, GrandPrixAsCsv(grand_prix_ranking).content)
                Jsoner(grand_prix_ranking).save("dynamic_jsons/grand_prix_stats.json")

            LOGGER.info("ROBOTA SKONCZONA")
        else:
            LOGGER.debug("heartbeat")
        if time() - last_log_reset_time > LOG_RESET_INTERVAL:
            przytnij_logi_i_ogloszenia()
            last_log_reset_time = time()
        else:
            sleep(SLEEP_BETWEEN_ITERATIONS)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--static", help="Wygeneruj tylko excela testowo", action="store_true")
    parser.add_argument("--frozen", help="Nie rob transferow miedzy ligami", action="store_true")
    parser.add_argument("--gp-start", help="Wystartuj Grand Prix - ustaw trasy w jsonie wpierw!", action="store_true")
    parser.add_argument("--gp", help="Obliczaj dodatkowo rankingi Grand Prix", action="store_true")
    args = parser.parse_args()
    main(args.static, args.frozen, args.gp_start, args.gp)


# def establish_player_list_to_do(gamer_list, do_everyone=None):
#     gamers = []
#     if do_everyone:
#         gamers = gamer_list
#     elif do_everyone is None:
#         print("Dej nicki, których time triale chcesz sciagnac. Jak skonczysz wpisywac"
#               " nicki, kliknij Enter dwa razy. Wpisz nicki poprawnie, bo bede szukal w nieskonczonosc!\n"
#               "Wpisz 'all' zeby zaaktualizowac wszystkich graczy w bazie config/user_list.json.")
#         while True:
#             gamer = input("Dej nick: ")
#             if not gamer:
#                 break
#             elif gamer == "all":
#                 gamers = gamer_list
#                 break
#             elif gamer in gamer_list:
#                 gamers.append(gamer)
#             else:
#                 print(f"Nie ma takiego gracza w bazie! Tu masz do wyboru:\n{gamer_list}")
#     return gamers
