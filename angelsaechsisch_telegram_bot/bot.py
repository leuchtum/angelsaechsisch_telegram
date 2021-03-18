from .logik import Vergleicher, Antworten, Runterkühler
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, JobQueue
import os
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

class Bot():
    def __init__(self, key):
        self.vgl = Vergleicher(os.getcwd())
        self.ant = Antworten(os.getcwd())
        self.kühl = Runterkühler()

        self.updater = Updater(key, use_context=True)
        self.dp = self.updater.dispatcher

        self.dp.add_handler(MessageHandler(Filters.text, self.__lesen))
        self.dp.add_error_handler(self.__fehler)


    def __lesen(self, update, context):
        if update.message.chat.type == "group":
            nachricht = update.message.text
            gruppenname = update.message.chat.title.replace(" ","_")
            nutzer = update.message.from_user.full_name.replace(" ","_")
            worte = self.__aufbereiten(nachricht)
            
            logger.info('Erhalten: %s@%s: %s', nutzer, gruppenname, nachricht)
            
            if self.vgl.beinhaltet_en(worte) and self.kühl.kühl_genug(gruppenname):
                antwort = self.ant.zufall_antwort()
                logger.info('Senden: %s: %s', nutzer, antwort)
                update.message.reply_text("<b>"+antwort+"</b>", parse_mode = "HTML")

    def __aufbereiten(self, string):
        return string.split(" ")

    def __fehler(self, update, context):
        logger.warning('Nachricht "%s" hat einen Fehler erzeugt: "%s"', update, context.error)

    def arbeite(self):
        self.updater.start_polling()
        self.updater.idle()