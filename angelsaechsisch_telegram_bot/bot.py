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
            gruppennummer, nutzernummer = self.extrahiere(update)
            nachricht = (
                "<b>Hallo Sportsfreunde!</b>\n"
                "\n"
                "Meine Aufgabe ist es zu überwachen, dass hier "
                "nur reinstes und feinstes Deutsch genutzt wird. "
                "Im Moment erinnere ich euch daran "
                f"<b>maximal {self.kühl.bekomme_amtag(gruppennummer)} pro Tag</b> "
                "mit einem <b>Mindestabstand von "
                f"{int(self.kühl.bekomme_warte(gruppennummer)/60)} Minuten</b>.\n"
                "\n"
                "Wenn euch diese Einstellungen nicht genehm sind, könnt ihr "
                "sie natürlich anpassen. Dazu gibt es folgende Befehle:\n"
                "\n"
                "<b>Kommando:</b> /warte 20\n"
                "Damit warte ich beispielsweise zwischen jeder höflichen "
                "Erinnerung 20 Minuten.\n"
                "\n"
                "<b>Kommando:</b> /amtag 10\n"
                "Damit schicke ich euch maximal 10 höfliche Erinnerungen pro Tag.\n"
                "\n"
                "<b>Kommando:</b> /nullen\n"
                "Mit diesem Befehl werden die Rückzühlzeit und die Anzahl der "
                "am Tag versandten Nachrichten zurückgesetzt.\n"
                "\n"
                "<b>Kommando:</b> /ausnahme WORT\n"
                "Es kann vorkommen, dass ich ein deutsches Wort fehlinterpretiere. "
                "Wenn ich in Zukunft auf dieses Wort nicht mehr reagieren soll, "
                "nutzt einfach dieses Kommando."
            )
            self.__senden_log(update, context, "HILFE_NACHRICHT")
            update.message.reply_text(nachricht, parse_mode="HTML")

    def __warte(self, update, context):
        if self.__ist_gruppenunterhaltung(update) and self.__hat_ein_argument(context, update):
            gruppennummer, nutzernummer = self.extrahiere(update)
            zeit = context.args[0]
            try:
                zeit = int(zeit)
                self.kühl.setze_warte(gruppennummer, zeit*60)
                nachricht = (
                    "Aber gerne doch! "
                    "Die Rückkühlzeit zwischen den höflichen Erinnerungen beträgt "
                    f"nun <b>{zeit} Minuten</b>."
                )
            except:
                nachricht = "Ich habe dich leider nicht verstanden."

            self.__senden_log(update, context, "WARTE_NACHRICHT")
            update.message.reply_text(nachricht, parse_mode="HTML")

    def __amtag(self, update, context):
        if self.__ist_gruppenunterhaltung(update) and self.__hat_ein_argument(context, update):
            gruppennummer, nutzernummer = self.extrahiere(update)
            maximal = context.args[0]
            try:
                maximal = int(maximal)
                self.kühl.setze_amtag(gruppennummer, maximal)
                nachricht = (
                    "Wie du willst, Kamerad! "
                    "Ich erinnere euch nun maximal "
                    f"<b>{maximal} mal pro Tag</b> daran, "
                    "dass in dieser Gruppenunterhaltung striktes "
                    "Angelsächsisch-Verbot besteht."
                )
            except:
                nachricht = "Ich habe dich leider nicht verstanden."

            self.__senden_log(update, context, "AMTAG_NACHRICHT")
            update.message.reply_text(nachricht, parse_mode="HTML")

    def __zurücksetzen(self, update, context):
        if self.__ist_gruppenunterhaltung(update):
            gruppennummer, nutzernummer = self.extrahiere(update)
            self.kühl.zurücksetzen(gruppennummer)
            nachricht = (
                "Erledigt!"
            )
            self.__senden_log(update, context, "ZURÜCKSETZEN_NACHRICHT")
            update.message.reply_text(nachricht)

    def __ausnahme(self, update, context):
        if self.__ist_gruppenunterhaltung(update) and self.__hat_ein_argument(context, update):
            ausnahme = context.args[0]
            self.vgl.schreibe_ausnahme(ausnahme)
            nachricht = (
                f"Alles klar, ab sofort reagiere ich auf '{ausnahme}' nicht mehr."
            )
            self.__senden_log(update, context, "AUSNAHME_NACHRICHT")
            update.message.reply_text(nachricht)

    def __lesen(self, update, context):
        if self.__ist_gruppenunterhaltung(update):
            nachricht = update.message.text
            gruppennummer, nutzernummer = self.extrahiere(update)
            worte = self.__aufbereiten(nachricht)

            logger.info('Erhalten: %s@%s: %s', nutzernummer,
                        gruppennummer, nachricht)

            if self.vgl.beinhaltet_en(worte) and self.kühl.kühl_genug(gruppennummer):
                antwort = self.ant.nächste_antwort(gruppennummer)
                self.__senden_log(update, context, antwort)
                update.message.reply_text(
                    "<b>"+antwort+"</b>", parse_mode="HTML")

    def __ist_gruppenunterhaltung(self, update):
        if update.message.chat.type == "group":
            return True
        update.message.reply_text(
            "Roboter läuft nur in Gruppenunterhaltungen.")
        return False

    def __hat_ein_argument(self, context, update):
        if len(context.args) == 1:
            return True
        update.message.reply_text(
            "Du musst diesen Befehl richtig nutzen. Siehe: /hilfe")
        return False

    def __aufbereiten(self, string):
        return string.split(" ")

    def __senden_log(self, update, context, nachricht):
        gruppennummer, nutzernummer = self.extrahiere(update)
        logger.info('Senden: %s@%s: %s', nutzernummer,
                    gruppennummer, nachricht)

    def __fehler(self, update, context):
        logger.warning(
            'Nachricht "%s" hat einen Fehler erzeugt: "%s"', update, context.error)

    def extrahiere(self, update):
        gruppennummer = str(update.message.chat.id)
        nutzernummer = str(update.message.from_user.id)
        return gruppennummer, nutzernummer

    def arbeite(self):
        self.updater.start_polling()
        self.updater.idle()
