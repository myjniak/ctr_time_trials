from . import LOGS_PATH


def log(msg, filename="logs.txt"):
    print(msg)
    if filename != "logs.txt":
        with open(LOGS_PATH + filename, "a+") as f:
            f.write(f"\n{str(msg)}")
