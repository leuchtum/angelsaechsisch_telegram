from .logik import Vergleicher, Antworten
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, JobQueue
import os
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

class Bot():
    def __init__(self, key):
        self.vgl = Vergleicher(os.getcwd())
        self.ant = Antworten(os.getcwd())

        self.updater = Updater(key, use_context=True)
        self.dp = self.updater.dispatcher

        self.dp.add_handler(MessageHandler(Filters.text, self.__lesen))
        self.dp.add_error_handler(self.__error)


    def __lesen(self, update, context):
        nachricht = update.message.text
        worte = self.__aufbereiten(nachricht)

        if self.vgl.beinhaltet_en(worte):
            antwort = self.ant.zufall_antwort()
            update.message.reply_text("<b>"+antwort+"</b>", parse_mode = "HTML")

    def __aufbereiten(self, string):
        worte = string.split(" ")
        return worte

    def __error(self, update, context):
        logger.warning('Update "%s" caused error "%s"', update, context.error)

    def arbeite(self):
        self.updater.start_polling()
        self.updater.idle()