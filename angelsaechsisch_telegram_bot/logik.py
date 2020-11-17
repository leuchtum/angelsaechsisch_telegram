import json
import random

DB_PFAD = "/angelsaechsisch_telegram_bot/data"
EN_PFAD = "/words.txt"
DE_PFAD = "/de.txt"
AUS_PFAD = "/ausnahmen.txt"
ANT_PFAD = "/antworten.txt"

class Vergleicher():
    def __init__(self, pfad):
        self.englisch = self.__bekomme_englisch(pfad)

    def __bekomme_englisch(self, pfad):
        en_roh = _lese_txt(pfad + DB_PFAD + EN_PFAD)
        de_roh = _lese_txt(pfad + DB_PFAD + DE_PFAD)
        aus_roh = _lese_txt(pfad + DB_PFAD + AUS_PFAD)
        en = set(en_roh)
        de = set(de_roh)
        aus = set(aus_roh)
        en = {i.lower() for i in en}
        de = {i.lower() for i in de}
        aus = {i.lower() for i in aus}
        en_clean = en - de
        en_clean = en_clean - aus
        return en_clean

    def beinhaltet_en(self, worte):
        '''
        worte: Liste mit Wörtern
        '''

        worte = [i.lower() for i in worte]
        worte = set(worte)

        anzahl = len(worte)

        if len(worte - self.englisch) == anzahl:
            return False
        else:
            return True

class Antworten():
    def __init__(self, pfad):
        self.antworten = _lese_txt(pfad + DB_PFAD + ANT_PFAD)

    def zufall_antwort(self):
        return random.choice(self.antworten)


def _lese_txt(pfad):
    with open(pfad, "r") as datei:
        roh = datei.read()
    roh = roh.split("\n")
    return roh[:-1]