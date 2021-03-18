import random
from datetime import datetime
import logging

DB_PFAD = "/angelsaechsisch_telegram_bot/data"
EN_PFAD = "/google-10000-english.txt"
DE_PFAD = "/de.txt"
AUS_PFAD = "/ausnahmen.txt"
ANT_PFAD = "/antworten.txt"

logger = logging.getLogger(__name__)
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
        worte = [i.lower() for i in worte]
        worte = set(worte)

        anzahl = len(worte)

        return len(worte - self.englisch) != anzahl

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


class Runterkühler():
    def __init__(self) -> None:
        self.ABWARTEN = 20
        self.ab_da_darf_ich_wieder = datetime.now().timestamp()
        
    def kühl_genug(self, gruppenname):
        sekunden = self.ab_da_darf_ich_wieder - datetime.now().timestamp()
        if self.ab_da_darf_ich_wieder < datetime.now().timestamp():
            self.zurücksetzen()
            return True
        else:
            logger.info("Gruppenunterhaltung %s noch für %i Sekunden zu heiß!", gruppenname, round(sekunden))
            return False
        
    def zurücksetzen(self):
        self.ab_da_darf_ich_wieder = datetime.now().timestamp() + self.ABWARTEN