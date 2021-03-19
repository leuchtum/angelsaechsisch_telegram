import random
from datetime import datetime
import logging
import json

DB_PFAD = "/angelsaechsisch_telegram_bot/data"
EN_PFAD = "/google-10000-english.txt"
DE_PFAD = "/de.txt"
AUS_PFAD = "/ausnahmen.txt"
ANT_PFAD = "/antworten.txt"
GRZ_PFAD = "/grenzen.json"

logger = logging.getLogger(__name__)


class Vergleicher():
    def __init__(self, pfad):
        self.englisch = self.__bekomme_englisch(pfad)

    def __bekomme_englisch(self, pfad):
        self.rootpfad = pfad
        en_roh = _lese_txt(self.rootpfad + DB_PFAD + EN_PFAD)
        de_roh = _lese_txt(self.rootpfad + DB_PFAD + DE_PFAD)
        aus_roh = _lese_txt(self.rootpfad + DB_PFAD + AUS_PFAD)
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

    def schreibe_ausnahme(self, ausnahme):
        _schreibe_txt(self.rootpfad + DB_PFAD + AUS_PFAD, ausnahme)
        self.__init__(self.rootpfad)


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


def _schreibe_txt(pfad, zeile):
    with open(pfad, "a") as datei:
        zeile += "\n"
        datei.write(zeile)


class Runterkühler():
    STANDARD_ABWARTEN = 5*60
    STANDARD_AMTAG = 10
    
    def __init__(self, pfad) -> None:
        self.rootpfad = pfad
        self.heute = datetime.now().date()
        self.warte = {}
        self.amtag = {}
        self.grenzen = {}
        self.lese_von_datei()

    def zurücksetzen(self, gruppenname):
        self.anlegen_wenn_nicht_da(gruppenname)
        self.warte[gruppenname] = datetime.now().timestamp()
        self.amtag[gruppenname] = 0
        logger.info("Hitze in Gruppenunterhaltung %s zurückgesetzt", gruppenname)

    def kühl_genug(self, gruppenname):
        ist_kühl_genug = False

        self.anlegen_wenn_nicht_da(gruppenname)
        
        # TODO Tageswechsel erkennen!
        
        if self.amtag[gruppenname] < self.grenzen[gruppenname]["amtag"]:
            sekunden = self.warte[gruppenname] - datetime.now().timestamp()
            if sekunden < 0:
                self.warte[gruppenname] = datetime.now().timestamp() + \
                    self.grenzen[gruppenname]["warte"]
                self.amtag[gruppenname] += 1
                ist_kühl_genug = True
            else:
                logger.info(
                    "Gruppenunterhaltung %s noch für %i Sekunden zu heiß!", gruppenname, round(sekunden))
        else:
            logger.info(
                "Gruppenunterhaltung %s darf heute nicht mehr senden!", gruppenname)

        return ist_kühl_genug

    def anlegen_wenn_nicht_da(self, gruppenname):
        if gruppenname not in self.warte:
            self.warte[gruppenname] = datetime.now().timestamp()
            self.amtag[gruppenname] = 0
            self.grenzen[gruppenname] = {
                "warte": self.STANDARD_ABWARTEN,
                "amtag": self.STANDARD_AMTAG
            }
            self.schreibe_in_datei()

    def bekomme_amtag(self, gruppenname):
        self.anlegen_wenn_nicht_da(gruppenname)
        return self.grenzen[gruppenname]["amtag"]

    def bekomme_warte(self, gruppenname):
        self.anlegen_wenn_nicht_da(gruppenname)
        return self.grenzen[gruppenname]["warte"]

    def setze_amtag(self, gruppenname, amtag):
        self.grenzen[gruppenname]["amtag"] = amtag
        self.schreibe_in_datei()

    def setze_warte(self, gruppenname, warte):
        self.grenzen[gruppenname]["warte"] = warte
        self.schreibe_in_datei()
        
    def schreibe_in_datei(self):
        pfad = self.rootpfad + DB_PFAD + GRZ_PFAD
        with open(pfad, "w") as datei:
            json.dump(self.grenzen, datei)
        
    def lese_von_datei(self):
        pfad = self.rootpfad + DB_PFAD + GRZ_PFAD
        with open(pfad, "r") as datei:
            self.grenzen = json.load(datei)
