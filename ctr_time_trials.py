import argparse
from datetime import datetime
from time import sleep
from lib.ctr_time_trials import CtrTimeTrials
from lib.excel_operations import ExcelOperations
from lib.json_operations import JsonOperations
from lib.google_drive_interactions import GoogleDriveInteractions
from lib.ranking_creator import RankingCreator
from confidential.variables import *
import sys


POINT_SYSTEM = [10, 8, 6, 5, 4, 3, 2, 1]
LEAGUE_POINTS_MINIMUM = 20
MINIMUM_PLAYER_COUNT_IN_LEAGUE = 5
SHEET_IDS_FILE_PATH = "sheet_ids.json"
TIMES_FROM_WEBPAGE_JSON_FILE_PATH = "dynamic_jsons/manual_times_from_webpage.json"
LEAGUE_NAMES = ["Nitro Tier", "Platinum Tier", "Gold Tier", "Sapphire Tier", "Wumpa Tier", "Armadillo Tier"]
FILE_PATHS = {
    "cheat_threshold_json": "config/cheat_thresholds.json",
    "track_ids": "config/tracks.txt",
    "user_platform_json": "config/user_config.json",
    "time_trials_json": "user_times.json",
    "page_id_cache_json": "page_id_cache.json",
    "csv_output": "output/time_trial_ranking",
    "xlsx_output": "output/time_trial_ranking"
}
GOOGLE_DRIVE_CREDENTIALS_PATH = "confidential/credentials.json"
GOOGLE_DRIVE_TOKEN_PATH = "confidential/token.pickle"
OUTPUT_EXCEL_FILE_PATH = "output/time_trial_ranking.xlsx"
INPUT_EXCEL_FILE_PATH = "output/times_from_webpage.xlsx"
INPUT_TEMPLATE_EXCEL_FILE_PATH = "config/CTR TT INPUT template.xlsx"
PLATFORMS = ['psn', 'xbl', 'switch']
GAMER_SEARCH_BAN_TIME = 800
PAGE_SEARCH_UNTIL_BORED_TIME = 5
SLEEP_BETWEEN_ITERATIONS = 300


def establish_player_list_to_do(gamer_list, do_everyone=None):
    gamers = []
    if do_everyone:
        gamers = gamer_list
    elif do_everyone is None:
        print("Dej nicki, których time triale chcesz sciagnac. Jak skonczysz wpisywac"
              " nicki, kliknij Enter dwa razy. Wpisz nicki poprawnie, bo bede szukal w nieskonczonosc!\n"
              "Wpisz 'all' zeby zaaktualizowac wszystkich graczy w bazie config/user_config.json.")
        while True:
            gamer = input("Dej nick: ")
            if not gamer:
                break
            elif gamer == "all":
                gamers = gamer_list
                break
            elif gamer in gamer_list:
                gamers.append(gamer)
            else:
                print(f"Nie ma takiego gracza w bazie! Tu masz do wyboru:\n{gamer_list}")
    return gamers


def operacje_na_google_drive(serwis, just_do_it=False, sheet_ids_file_path=SHEET_IDS_FILE_PATH):
    auto_upload = ''
    if not just_do_it:
        auto_upload = input("Chcesz auto-upload?")
    if auto_upload in ['y', 'yes', 'tak', 'ok'] or just_do_it:

        print("Wysylanie pliku...")
        serwis.upload_file(OUTPUT_EXCEL_FILE_PATH, RANKING_FILE_ID)
        print("Sciagam sheet IDs...")
        sheet_ids = serwis.download_sheet_ids(RANKING_FILE_ID)
        JsonOperations.save_json(sheet_ids, sheet_ids_file_path)
        print("Resetuje arkusz do inputu...")
        serwis.upload_file(INPUT_TEMPLATE_EXCEL_FILE_PATH, RANKING_INPUT_FILE_ID)
        print("Resetuje uprawnienia arkuszu do inputu...")
        serwis.protect_first_column(RANKING_INPUT_FILE_ID, MASTER_EMAIL)


def main(do_everyone=None, upload=None, loop=None, logging_to_file=False, sheet_ids_file_path=SHEET_IDS_FILE_PATH):
    if logging_to_file:
        sys.stdout = open("logs/logs.txt", "w")
    while True:
        serwis = GoogleDriveInteractions(GOOGLE_DRIVE_CREDENTIALS_PATH,
                                         GOOGLE_DRIVE_TOKEN_PATH,
                                         GOOGLE_SHEETS_API_KEY)
        serwis.download_file(INPUT_EXCEL_FILE_PATH, RANKING_INPUT_FILE_ID)
        zapisywaczka_do_excela = ExcelOperations(POINT_SYSTEM, LEAGUE_NAMES, **FILE_PATHS)
        nowe_czasy = \
            zapisywaczka_do_excela.convert_xlsx_to_json(INPUT_EXCEL_FILE_PATH, TIMES_FROM_WEBPAGE_JSON_FILE_PATH)
        if nowe_czasy:
            current_datetime = datetime.now().strftime("%I:%M%p %B %d, %Y")
            sciagaczka_time_triali = CtrTimeTrials(cookie=ACTIVISION_COOKIE,
                                                   gamer_search_ban_time=GAMER_SEARCH_BAN_TIME,
                                                   page_search_until_bored_time=PAGE_SEARCH_UNTIL_BORED_TIME,
                                                   platforms=PLATFORMS,
                                                   **FILE_PATHS)
            gamers = establish_player_list_to_do(sciagaczka_time_triali.player_list, do_everyone=do_everyone)
            sciagaczka_time_triali.get_usernames_times(gamers)
            JsonOperations().apply_json_to_json("config/manual_user_times.json", FILE_PATHS["time_trials_json"])
            JsonOperations.save_json(sciagaczka_time_triali.changes, "new_records.json")

            zapisywaczka_do_excela.load_time_trial_info(**FILE_PATHS)
            zapisywaczka_do_excela.convert_xlsx_to_json(INPUT_EXCEL_FILE_PATH, TIMES_FROM_WEBPAGE_JSON_FILE_PATH)
            JsonOperations().apply_json_to_json(TIMES_FROM_WEBPAGE_JSON_FILE_PATH, FILE_PATHS["time_trials_json"])

            rankingowaczka = RankingCreator(FILE_PATHS["time_trials_json"],
                                            league_names=LEAGUE_NAMES,
                                            track_list=sciagaczka_time_triali.track_list,
                                            minimum_player_count_in_league=MINIMUM_PLAYER_COUNT_IN_LEAGUE,
                                            league_points_minimum=LEAGUE_POINTS_MINIMUM,
                                            point_system=POINT_SYSTEM)
            rankingowaczka.give_out_points_and_medals_for_all_leagues()
            rankingowaczka.calc_total_time()

            zapisywaczka_do_excela.load_time_trial_info(**FILE_PATHS)
            zapisywaczka_do_excela.convert_user_times_json_to_csvs(LEAGUE_POINTS_MINIMUM, current_datetime)
            zapisywaczka_do_excela.convert_csvs_to_xlsx(OUTPUT_EXCEL_FILE_PATH, LEAGUE_NAMES)
            operacje_na_google_drive(serwis, just_do_it=upload, sheet_ids_file_path=sheet_ids_file_path)
        else:
            print("nie ma nowych czasow")

        if not loop:
            return open('logs/logs.txt', 'r').readlines()
        print("Pospie troche...")
        sleep(SLEEP_BETWEEN_ITERATIONS)


def every_gamer_should_be_checked(everyone, noone):
    if everyone:
        return True
    elif noone:
        return False
    return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--sheetidpath", help="Sciazka do zapisania jsona z ID sheetow", action="store_true")
    parser.add_argument("--none", help="Nie sciagaj niczego, obrob tylko excela", action="store_true")
    parser.add_argument("--all", help="Sciagnij czasy wszystkich graczy z user_config.json", action="store_true")
    parser.add_argument("-u", help="Wyslij excela na koniec", action="store_true")
    parser.add_argument("--loop", help="Napierdalaj w kolko do usranej smierci", action="store_true")
    parser.add_argument("-l", help="Loguj tylko do pliku, żeby Traceback wszedł", action="store_true")
    args = parser.parse_args()
    main(every_gamer_should_be_checked(args.all, args.none), args.u, args.loop, args.l, args.sheetidpath)
