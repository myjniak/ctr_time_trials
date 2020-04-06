from .ctr_time_trials import main
from flask import Flask


app = Flask(__name__)


@app.route("/")
def main_():
    return main(do_everyone=False,
                upload=True,
                loop=None,
                logging_to_file=True,
                sheet_ids_file_path="/home/ctrtimet/public_html/sheet_ids.json")


if __name__ == "__main__":
    app.run()
