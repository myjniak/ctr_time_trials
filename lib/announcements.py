import logging


class Announcements:

    def __init__(self, new_tts, old_tts, league_names, track_list):
        self.new_tts = new_tts
        self.old_tts = old_tts
        self.league_names = league_names
        self.track_list = track_list
        self.leagues_with_transfers = self.get_leagues_with_transfers(new_tts, old_tts)

    def log_medals(self):
        grades = {
            'gold': 3,
            'silver': 2,
            'bronze': 1,
            None: 0
        }
        players = [player for player in self.new_tts.keys()
                   if self.new_tts[player]["league"] not in self.leagues_with_transfers]
        for player in players:
            for track in self.track_list:
                try:
                    m_old = self.old_tts[player]['tracks'][track]['medal']
                    m_new = self.new_tts[player]['tracks'][track]['medal']
                except KeyError:
                    continue
                if grades[m_new] > grades[m_old]:
                    logging.info(f"{player} gets {m_new.upper()} medal on {track}!",
                        filename=f"{self.new_tts[player]['league']}.txt")

    def log_league_transfers(self):
        for player, player_info in self.new_tts.items():
            self.old_tts[player].setdefault('league', 0)
            l_old = self.old_tts[player]['league']
            l_new = player_info['league']
            if l_new > l_old:
                logging.info(f"{player} entered the {self.league_names[l_new - 1]}", filename=f"{l_new}.txt")
            elif l_new < l_old:
                logging.info(f"{player} HAS ASCENDED TO {self.league_names[l_new - 1]}!", filename=f"{l_new}.txt")

    @staticmethod
    def get_leagues_with_transfers(new_tts, old_tts):
        leagues_with_transfers = []
        for player, player_info in new_tts.items():
            old_tts[player].setdefault('league', 0)
            l_old = old_tts[player]['league']
            l_new = player_info['league']
            if l_new != l_old:
                leagues_with_transfers.append(l_new)
                leagues_with_transfers.append(l_old)
        leagues_with_transfers = list(set(leagues_with_transfers))
        return leagues_with_transfers
