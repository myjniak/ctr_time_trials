import csv


class GrandPrixAsCsv:

    def __init__(self, grand_prix_json):
        self.gp_json = grand_prix_json
        self.players = list(grand_prix_json.keys())
        self.content = list()
        self._convert_gp_json_to_csv()

    def _convert_gp_json_to_csv(self):
        players_sorted = sorted(self.players, key=lambda player: self.gp_json[player]["ranking"], reverse=True)
        for i, player in enumerate(players_sorted):
            self.content.append([i+1, player, int(self.gp_json[player]["ranking"])])

    def save(self, file_path):
        with open(file_path + ".csv", mode='w+', newline='') as f:
            list_writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for row in self.content:
                list_writer.writerow(row)

