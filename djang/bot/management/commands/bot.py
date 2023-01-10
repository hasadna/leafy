from django.core.management.base import BaseCommand, CommandError
import datetime
import os
import dotenv

import logging
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id,
       text="""\
Hi, pleaes send me your locartion!
הי, שלח לי לייב לוקיישן בבקשה!
"""
   )


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=update)

async def got_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message or update.edited_message
    location = msg.location
    lat = location.latitude
    lon = location.longitude
    acc = location.horizontal_accuracy
    # TODO check if in polygon
    # if in polygon and we were not in a polygon:
        # Ask users for tree pics
    # elif we used to be in a polygon:
        # Save that we're not in polygon
    # TODO save in DB
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"got location! {lat} / {lon} ~ {acc}")

async def got_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # TODO pull latest location from db
    # TODO ensure location is fresh (last 5min?) should we?
    # TODO should I try get it from EXIF?
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Thank you for this tree pic 🌲.")

# TODO do we want gamification?



class Command(BaseCommand):
    help = "Run the telegram bot. http://t.me/open_workshop_leafy_bot"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        dotenv.load_dotenv() # Allows reading .env from outside docker
        token = os.environ['TELEGRAM_TOKEN']
        application = ApplicationBuilder().token(token).build()
        
        start_handler = CommandHandler('start', start)
        application.add_handler(start_handler)

        application.add_handler(MessageHandler(filters.LOCATION, got_location))
        application.add_handler(MessageHandler(filters.PHOTO, got_photo))
        application.add_handler(MessageHandler(filters.CHAT, echo))
        
        application.run_polling()
