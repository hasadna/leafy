import asyncio
import datetime
import dotenv
import io
import logging
import os


from django.core.management.base import BaseCommand, CommandError
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


# "היי, אני צריך לייב לוקיישן ואז תמונות של עצים, בבקשה!"
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = '''
מה שקשה למדוד קשה לנהל. כדי לקדם קבלת החלטות מבוססות נתונים,
שלב ראשון במיפוי היער העירוני הדיגיטלי הוא לדעת כמה עצים יש לנו? איפה הם נמצאים? ואיך הם נראים?'''
    await send_message(
        update, context, message
    )
    await asyncio.sleep(1)

    message = '''יוצאים לדרך, קודם כל יש להפעיל את הגדרת המיקום הזו, share my live location למשך זמן המיפוי הצפוי'''
    await send_message(update, context, message)
    await asyncio.sleep(1)

    message = '''
עבור כל עץ שיתועד צריך לעשות 3 דברים בלבד:
1. צילום נוף העץ.
2. צילום מקרוב של העלים
3. ציילום בסיס העץ והגזע קרוב ככל שניתן'''
    await send_message(update, context, message)
    await asyncio.sleep(1)

    message = '''
לכל תמונה שתצולם יצורף מיקום בצורה אוטומטית.
חשוב למפות עם כיוון ההליכה וכל עץ לצלם קודם מרחוק (נוף) ועד לקרוב (בסיס העץ). 3 תמונות יספיקו בהחלט :)

כדי שנדע שסיימת, בסוף המיפוי יש להקליד end/

זהו פיילוט, ובכל מקרה לא נשמור פרטים אישיים'''
    await send_message(update, context, message)
    await asyncio.sleep(1)

    message = '''אם הכל ברור ומוסכם, אפשר להתחיל לצלם, בהצלחה :)'''
    await send_message(update, context, message)


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
        print(location.latitude, location.longitude, location.horizontal_accuracy, datetime.datetime.now())
        print()
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
            # await send_message(update, context, "תודה! 🌲")
        except NoLocationException:
            await send_message(update, context, "אני צריך לייב לוקיישן. שתף איתי בבקשה")
    except Exception as e:
        await send_message(update, context, "קרתה לי שגיאה")
        await send_message(update, context, str(e))


async def end(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = '''
    תודה! עשית עבודה מצויינת. עזרת לקידום דיגיטציית עצי הרחוב בישראל.
    אשמח להיפגש בהמשך ולהמשיך לעבוד ביחד'''
    await send_message(update, context, message)


class Command(BaseCommand):
    help = "Run the telegram bot. http://t.me/open_workshop_leafy_bot"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        dotenv.load_dotenv()  # Allows reading .env from outside docker
        token = os.environ["TELEGRAM_TOKEN"]
        application = ApplicationBuilder().token(token).build()

        start_handler = CommandHandler("start", start)
        end_handler = CommandHandler('end', end)
        application.add_handler(start_handler)
        application.add_handler(end_handler)

        application.add_handler(MessageHandler(filters.LOCATION, got_location))
        application.add_handler(MessageHandler(filters.PHOTO, got_photo))
        # Last resort
        application.add_handler(MessageHandler(filters.CHAT, echo))

        application.run_polling()
