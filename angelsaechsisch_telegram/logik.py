import random
from datetime import datetime
import logging
import json
import re
import os
import pathlib

DB_PFAD = "data"
EN_PFAD = "google-10000-english.txt"
DE_PFAD = "de.txt"
AUS_PFAD = "ausnahmen.txt"
ANT_PFAD = "antworten.txt"
GRZ_PFAD = "grenzen.json"

logger = logging.getLogger(__name__)


def _lese_txt(pfad):
    with open(pfad, "r") as datei:
        roh = datei.read()
    roh = roh.split("\n")
    return roh[:-1]


def _schreibe_txt(pfad, zeile):
    with open(pfad, "a") as datei:
        zeile += "\n"
        datei.write(zeile)


class Vergleicher():
    def __init__(self):
        self.pfad = pathlib.Path(__file__).parent
        self.englisch = self.__bekomme_englisch()

    def __bekomme_englisch(self):
        en_roh = _lese_txt(f"{self.pfad}/{DB_PFAD}/{EN_PFAD}")
        de_roh = _lese_txt(f"{self.pfad}/{DB_PFAD}/{DE_PFAD}")
        aus_roh = _lese_txt(f"{self.pfad}/{DB_PFAD}/{AUS_PFAD}")

        en = set(en_roh)
        de = set(de_roh)
        aus = set(aus_roh)

        en = {i.lower() for i in en}
        de = {i.lower() for i in de}
        aus = {i.lower() for i in aus}

        kurze = set()
        for i in en:
            if len(i) < 3:
                kurze.add(i)

        en_clean = en - de
        en_clean = en_clean - aus
        en_clean = en_clean - kurze
        return en_clean

    def beinhaltet_en(self, worte):
        def putzen(wort):
            wort = re.sub('[^A-Za-z0-9]+', '', wort)
            return wort.lower()

        worte = [putzen(i) for i in worte]
        worte = set(worte)

        anzahl = len(worte)

        return len(worte - self.englisch) != anzahl

    def schreibe_ausnahme(self, ausnahme):
        _schreibe_txt(self.rootpfad + DB_PFAD + AUS_PFAD, ausnahme)
        self.__init__(self.rootpfad)


class Antworten():
    def __init__(self):
        self.pfad = pathlib.Path(__file__).parent
        self.antworten = _lese_txt(f"{self.pfad}/{DB_PFAD}/{ANT_PFAD}")
        self.generatoren = {}

    def zufall_antwort(self):
        return random.choice(self.antworten)

    def nächste_antwort(self, gruppennummer):
        def antworten_generator(antworten):
            while True:
                yield from antworten

        if gruppennummer not in self.generatoren:
            self.generatoren[gruppennummer] = antworten_generator(
                self.antworten)

        return next(self.generatoren[gruppennummer])


class Runterkühler():
    STANDARD_ABWARTEN = 5*60
    STANDARD_AMTAG = 10

    def __init__(self) -> None:
        self.pfad = pathlib.Path(__file__).parent
        self.heute = datetime.now().date()
        self.warte = {}
        self.amtag = {}
        self.grenzen = {}
        self.lese_von_datei()

    def zurücksetzen(self, gruppennummer):
        self.anlegen_wenn_nicht_da(gruppennummer)
        self.warte[gruppennummer] = datetime.now().timestamp()
        self.amtag[gruppennummer] = 0
        logger.info(
            "Hitze in Gruppenunterhaltung %s zurückgesetzt", gruppennummer)

    def kühl_genug(self, gruppennummer):
        ist_kühl_genug = False

        self.anlegen_wenn_nicht_da(gruppennummer)
        self.evtl_neuer_tag()

        if self.amtag[gruppennummer] < self.grenzen[gruppennummer]["amtag"]:
            sekunden = self.warte[gruppennummer] - datetime.now().timestamp()
            if sekunden < 0:
                self.warte[gruppennummer] = datetime.now().timestamp() + \
                    self.grenzen[gruppennummer]["warte"]
                self.amtag[gruppennummer] += 1
                ist_kühl_genug = True
            else:
                logger.info(
                    "Gruppenunterhaltung %s noch für %i Sekunden zu heiß!", gruppennummer, round(sekunden))
        else:
            logger.info(
                "Gruppenunterhaltung %s darf heute nicht mehr senden!", gruppennummer)

        return ist_kühl_genug

    def anlegen_wenn_nicht_da(self, gruppennummer):
        if gruppennummer not in self.warte:
            self.warte[gruppennummer] = 0
            self.amtag[gruppennummer] = 0

        if gruppennummer not in self.grenzen:
            self.grenzen[gruppennummer] = {
                "warte": self.STANDARD_ABWARTEN,
                "amtag": self.STANDARD_AMTAG
            }
            self.schreibe_in_datei()

    def bekomme_amtag(self, gruppennummer):
        self.anlegen_wenn_nicht_da(gruppennummer)
        return self.grenzen[gruppennummer]["amtag"]

    def bekomme_warte(self, gruppennummer):
        self.anlegen_wenn_nicht_da(gruppennummer)
        return self.grenzen[gruppennummer]["warte"]

    def setze_amtag(self, gruppennummer, amtag):
        self.anlegen_wenn_nicht_da(gruppennummer)
        self.grenzen[gruppennummer]["amtag"] = amtag
        self.amtag[gruppennummer] = 0
        self.schreibe_in_datei()

    def setze_warte(self, gruppennummer, warte):
        self.anlegen_wenn_nicht_da(gruppennummer)
        self.grenzen[gruppennummer]["warte"] = warte
        self.warte[gruppennummer] = 0
        self.schreibe_in_datei()

    def schreibe_in_datei(self):
        pfad = f"{self.pfad}/{DB_PFAD}/{GRZ_PFAD}"
        with open(pfad, "w") as datei:
            json.dump(self.grenzen, datei)

    def lese_von_datei(self):
        pfad = f"{self.pfad}/{DB_PFAD}/{GRZ_PFAD}"

        if not os.path.exists(pfad):
            self.schreibe_in_datei()

        with open(pfad, "r") as datei:
            self.grenzen = json.load(datei)

    def evtl_neuer_tag(self):
        if self.heute != datetime.now().date():
            for gruppennummer in self.warte:
                self.warte[gruppennummer] = 0
            for gruppennummer in self.amtag:
                self.amtag[gruppennummer] = 0
            self.heute = datetime.now().date()
