import os


LOGS_PATH = 'logs/'


def trim_txt_files(msg_count=10):
    file_list = os.listdir(LOGS_PATH)
    for f in file_list:
        if f.endswith('txt') and not f.startswith("logs"):
            with open(LOGS_PATH + f, 'r') as log:
                data = log.read().splitlines(True)
            with open(LOGS_PATH + f, 'w') as log:
                log.writelines(data[-msg_count:])


trim_txt_files()
