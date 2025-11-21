import os
import logging
from fastapi import FastAPI, Request
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Логи
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Токен
TOKEN = os.getenv("BOT_TOKEN", "8583826837:AAGJI6Qf5QvI_GXva_xzWs9Eo1i96jKLJC0")

# URL мини-приложения (ОСНОВНОЙ)
WEBAPP_URL = "https://telegram-mini-adshare-afxx.onrender.com/webapp"

# URL вебхука
WEBHOOK_URL = "https://telegram-mini-adshare-afxx.onrender.com/webhook"

# FastAPI приложение
app = FastAPI()

# Telegram Application
telegram_app = ApplicationBuilder().token(TOKEN).build()


# ---------- Команда /start ----------
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

    await update.message.reply_text(
        "Добро пожаловать в мини-приложение!",
        reply_markup=reply_markup
    )


telegram_app.add_handler(CommandHandler("start", start))


# ---------- Приём вебхуков ----------
@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return {"ok": True}


# ---------- Установка вебхука на Render ----------
@app.on_event("startup")
async def on_startup():
    logger.info("Удаляем старый WebHook…")
    await telegram_app.bot.delete_webhook(drop_pending_updates=True)

    logger.info(f"Устанавливаем новый WebHook: {WEBHOOK_URL}")
    await telegram_app.bot.set_webhook(url=WEBHOOK_URL)

    logger.info("WebHook установлен успешно!")
