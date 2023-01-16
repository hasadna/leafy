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

from bot.services import get_user, store_location, store_photo, NoLocationException


async def extract_user(update):
    f = (update.message or update.edited_message)["from"]
    return await get_user(f.username, f.first_name, f.last_name, f.id)


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


async def send_message(update, context, text):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_message(
        update, context, "היי, אני צריך לייב לוקיישן ואז תמונות של עצים, בבקשה!"
    )


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await extract_user(update)
    await send_message(
        update, context, "אני צריך לייב לוקיישן ואז תמונות של עצים, בבקשה"
    )


async def got_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message or update.edited_message
    user = await extract_user(update)
    try:
        location = message.location
        await store_location(
            user,
            location.latitude,
            location.longitude,
            location.horizontal_accuracy,
            message.date,
        )
    except Exception as e:
        await send_message(update, context, "קרתה לי שגיאה")
        await send_message(update, context, str(e))


async def got_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # TODO ensure location is fresh (last 5min?) should we?
    user = await extract_user(update)
    message = update.message
    try:
        photo_file = await message.effective_attachment[-1].get_file()
        with io.BytesIO() as s:
            await photo_file.download_to_memory(out=s)
            s.seek(0)
            photo_data = s.read()
        try:
            await store_photo(user, photo_data, message.date)
            await send_message(update, context, "תודה! 🌲")
        except NoLocationException:
            await send_message(update, context, "אני צריך לייב לוקיישן. שתף איתי בבקשה")
    except Exception as e:
        await send_message(update, context, "קרתה לי שגיאה")
        await send_message(update, context, str(e))


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
        # Last resort
        application.add_handler(MessageHandler(filters.CHAT, echo))

        application.run_polling()
