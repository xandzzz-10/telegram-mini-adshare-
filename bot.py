import os
import logging
from fastapi import FastAPI, Request
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo
from telegram.ext import Application, ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN", "8583826837:AAGJI6Qf5QvI_GXva_xzWs9Eo1i96jKLJC0")

WEBHOOK_HOST = "https://telegram-mini-adshare-afxx.onrender.com"
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = WEBHOOK_HOST + WEBHOOK_PATH

WEBAPP_URL = WEBHOOK_HOST + "/webapp"

app = FastAPI()

# ---------------------------------------
# Telegram application
# ---------------------------------------
telegram_app: Application = ApplicationBuilder().token(TOKEN).build()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            KeyboardButton(
                text="Открыть мини-приложение",
                web_app=WebAppInfo(url=WEBAPP_URL)
            )
        ]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text("Добро пожаловать!", reply_markup=reply_markup)


telegram_app.add_handler(CommandHandler("start", start))


# ---------------------------------------
# FastAPI endpoint (приём webhook)
# ---------------------------------------
@app.post(WEBHOOK_PATH)
async def process_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return {"ok": True}


# ---------------------------------------
# Установка webhook при старте Render-а
# ---------------------------------------
@app.on_event("startup")
async def on_startup():
    logger.info("Удаляю старый webhook…")
    await telegram_app.bot.delete_webhook(drop_pending_updates=True)

    logger.info(f"Ставлю новый webhook: {WEBHOOK_URL}")
    await telegram_app.bot.set_webhook(url=WEBHOOK_URL)

    logger.info("Webhook УСТАНОВЛЕН!")
