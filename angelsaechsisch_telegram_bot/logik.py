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
        self.ABWARTEN = 5*60
        self.PRO_TAG = 3
        self.heute = datetime.now().date()
        self.warte = {}
        self.amtag = {}
        
    def kühl_genug(self, gruppenname):
        ist_kühl_genug = False
        
        if self.amtag[gruppenname] < self.PRO_TAG:
            sekunden = self.warte[gruppenname] - datetime.now().timestamp()
            if sekunden < 0:
                self.warte[gruppenname] = datetime.now().timestamp() + self.ABWARTEN
                self.amtag[gruppenname] += 1
                ist_kühl_genug = True
            else:
                logger.info("Gruppenunterhaltung %s noch für %i Sekunden zu heiß!", gruppenname, round(sekunden))
        else:
            logger.info("Gruppenunterhaltung %s darf heute nicht mehr senden!", gruppenname)
            
        return ist_kühl_genug
    
    def anlegen_wenn_nicht_da(self, gruppenname):
        if gruppenname not in self.warte:
            self.warte[gruppenname] = datetime.now().timestamp() + self.ABWARTEN
            self.amtag[gruppenname] = 0
            
    def bekomme_amtag(self, gruppenname):
        self.anlegen_wenn_nicht_da(gruppenname)
        return self.PRO_TAG
        #return self.amtag[gruppenname] / 60
    
    def bekomme_warte(self, gruppenname):
        self.anlegen_wenn_nicht_da(gruppenname)
        return int(self.ABWARTEN / 60)
        #return self.warte[gruppenname] / 60
        
    def setze_amtag(self, gruppenname, amtag):
        raise NotImplementedError("Noch nicht implementiert") #TODO
    
    def setze_warte(self, gruppenname, warte):
        raise NotImplementedError("Noch nicht implementiert") #TODO