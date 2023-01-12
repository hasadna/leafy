from django.core.management.base import BaseCommand, CommandError
import datetime
import os
import dotenv
import io

import logging
from telegram import Update
from telegram.ext import (
    filters,
    MessageHandler,
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

from bot.services import get_user, store_location, store_photo


async def extract_user(update):
    f = (update.message or update.edited_message)["from"]
    return await get_user(f.username, f.first_name, f.last_name, f.id)


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="""\
Hi, pleaes send me your locartion!
הי, שלח לי לייב לוקיישן בבקשה!
""",
    )


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await extract_user(update)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=update)


async def got_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message or update.edited_message
    user = await extract_user(update)
    location = message.location
    await store_location(
        user,
        location.latitude,
        location.longitude,
        location.horizontal_accuracy,
        message.date,
    )
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=f"got location! {location}"
    )


async def got_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # TODO ensure location is fresh (last 5min?) should we?
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="Thank you for this tree pic 🌲."
    )
    await context.bot.send_message(chat_id=update.effective_chat.id, text=update)

    user = await extract_user(update)

    message = update.message
    photo_file = await message.effective_attachment[-1].get_file()
    with io.BytesIO() as s:
        await photo_file.download_to_memory(out=s)
        s.seek(0)
        photo_data = s.read()
    await store_photo(user, photo_data, message.date)


# TODO do we want gamification?


class Command(BaseCommand):
    help = "Run the telegram bot. http://t.me/open_workshop_leafy_bot"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        dotenv.load_dotenv()  # Allows reading .env from outside docker
        token = os.environ["TELEGRAM_TOKEN"]
        application = ApplicationBuilder().token(token).build()

        start_handler = CommandHandler("start", start)
        application.add_handler(start_handler)

        application.add_handler(MessageHandler(filters.LOCATION, got_location))
        application.add_handler(MessageHandler(filters.PHOTO, got_photo))
        application.add_handler(MessageHandler(filters.CHAT, echo))

        application.run_polling()
