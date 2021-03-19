from .logik import Vergleicher, Antworten, Runterkühler
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import os
import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


class Bot():
    def __init__(self, key):
        self.vgl = Vergleicher(os.getcwd())
        self.ant = Antworten(os.getcwd())
        self.kühl = Runterkühler(os.getcwd())

        self.updater = Updater(key, use_context=True)
        self.dp = self.updater.dispatcher

        self.dp.add_handler(CommandHandler("start", self.__hilfe))
        self.dp.add_handler(CommandHandler("hilfe", self.__hilfe))
        self.dp.add_handler(CommandHandler("nullen", self.__zurücksetzen))
        self.dp.add_handler(CommandHandler("ausnahme", self.__ausnahme))
        self.dp.add_handler(CommandHandler("warte", self.__warte))
        self.dp.add_handler(CommandHandler("amtag", self.__amtag))
        self.dp.add_handler(MessageHandler(Filters.text, self.__lesen))
        self.dp.add_error_handler(self.__fehler)

    def __hilfe(self, update, context):
        if self.__ist_gruppenunterhaltung(update):
            gruppenname = update.message.chat.title.replace(" ", "_")
            nachricht = (
                "Hallo Sportsfreunde!\n"
                "Ihr könnt mir gerne sagen, wie oft ich euch erinnern soll, "
                "dass hier nur Deutsch gesprochen wird. "
                "Dazu könnt ihr folgende Befehle schicken:\n"
                "\n"
                "Befehl: /warte 20\n"
                "Damit warte ich beispielsweise zwischen jeder höflichen "
                "Erinnerung 20 Minuten.\n"
                "\n"
                "Befehl: /amtag 10\n"
                "Damit schicke ich euch maximal 10 höfliche Erinnerungen pro Tag.\n"
                "\n"
                "Aktuell erinnere ich euch maximal "
                f"{self.kühl.bekomme_amtag(gruppenname)} "
                "pro Tag mit einem Mindestabstand von "
                f"{int(self.kühl.bekomme_warte(gruppenname)/60)} "
                "Minuten daran, dass hier nur reinstes und feinstes Deutsch "
                "gesprochen wird.\n"
                "\n"
                "Außerdem könnt ihr die aktuelle Rückkühlzeit mit sowie die Anzahl der "
                "bereits gesendeten täglichen Nachrichten mit dem Befehl /nullen "
                "zurücksetzen.\n"
                "\n"
                "Falls ich mal ein Wort völlig falsch verstehe, könnt ihr das "
                "Wort über /ausnahme WORT von einer weiteren höflichen Erinnerung "
                "ausschließen."
            )
            self.__senden_log(update, "HILFE_NACHRICHT")
            update.message.reply_text(nachricht)

    def __warte(self, update, context):
        if self.__ist_gruppenunterhaltung(update) and self.__hat_ein_argument(update):
            gruppenname = update.message.chat.title.replace(" ", "_")
            zeit = context.args[0]
            try:
                zeit = int(zeit)
                self.kühl.setze_warte(gruppenname, zeit*60)
                nachricht = (
                "Aber gerne doch! "
                "Die Rückkühlzeit zwischen den höflichen Erinnerungen beträgt "
                f"nun {zeit} Minuten."
                )
            except:
                nachricht = "Ich habe dich leider nicht verstanden."
            
            self.__senden_log(update, "AMTAG_NACHRICHT")
            update.message.reply_text(nachricht)

    def __amtag(self, update, context):
        if self.__ist_gruppenunterhaltung(update) and self.__hat_ein_argument(update):
            gruppenname = update.message.chat.title.replace(" ", "_")
            maximal = context.args[0]
            try:
                maximal = int(maximal)
                self.kühl.setze_amtag(gruppenname, maximal)
                nachricht = (
                    "Wie du willst, Kamerad! "
                    f"Ich erinnere euch nun maximal {maximal} mal pro Tag daran, "
                    "dass in dieser Gruppenunterhaltung striktes "
                    "Angelsächsisch-Verbot besteht."
                )
            except:
                nachricht = "Ich habe dich leider nicht verstanden."
            
            self.__senden_log(update, "AMTAG_NACHRICHT")
            update.message.reply_text(nachricht)

    def __zurücksetzen(self, update, context):
        if self.__ist_gruppenunterhaltung(update):
            gruppenname = update.message.chat.title.replace(" ", "_")
            self.kühl.zurücksetzen(gruppenname)
            nachricht = (
                "Erledigt!"
                )
            self.__senden_log(update, "ZURÜCKSETZEN_NACHRICHT")
            update.message.reply_text(nachricht)
            
    def __ausnahme(self, update, context):
        if self.__ist_gruppenunterhaltung(update) and self.__hat_ein_argument(update):
            ausnahme = context.args[0]
            self.vgl.schreibe_ausnahme(ausnahme)
            nachricht = (
                f"Alles klar, ab sofort reagiere ich auf '{ausnahme}' nicht mehr"
            )
            self.__senden_log(update, "AUSNAHME_NACHRICHT")
            update.message.reply_text(nachricht)
            
            
    def __lesen(self, update, context):
        if self.__ist_gruppenunterhaltung(update):
            nachricht = update.message.text
            gruppenname = update.message.chat.title.replace(" ", "_")
            nutzer = update.message.from_user.full_name.replace(" ", "_")
            worte = self.__aufbereiten(nachricht)

            logger.info('Erhalten: %s@%s: %s', nutzer, gruppenname, nachricht)

            if self.vgl.beinhaltet_en(worte) and self.kühl.kühl_genug(gruppenname):
                antwort = self.ant.zufall_antwort()
                self.__senden_log(update, antwort)
                update.message.reply_text(
                    "<b>"+antwort+"</b>", parse_mode="HTML")

    def __ist_gruppenunterhaltung(self, update):
        if update.message.chat.type == "group":
            return True
        update.message.reply_text(
            "Roboter läuft nur in Gruppenunterhaltungen.")
        return False
    
    def __hat_ein_argument(self, update):
        return True #TODO

    def __aufbereiten(self, string):
        return string.split(" ")

    def __senden_log(self, update, nachricht):
        gruppenname = update.message.chat.title.replace(" ", "_")
        nutzer = update.message.from_user.full_name.replace(" ", "_")
        logger.info('Senden: %s@%s: %s', nutzer, gruppenname, nachricht)
        
    def __fehler(self, update, context):
        logger.warning(
            'Nachricht "%s" hat einen Fehler erzeugt: "%s"', update, context.error)

    def arbeite(self):
        self.updater.start_polling()
        self.updater.idle()