import os
import logging
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN", "8583826837:AAGJI6Qf5QvI_GXva_xzWs9Eo1i96jKLJC0")
WEBAPP_URL = "https://telegram-mini-adshare-afxx.onrender.com/webapp"

app = FastAPI()
templates = Jinja2Templates(directory="templates")

telegram_app = Application.builder().token(TOKEN).build()


# ---------------- /start ----------------
async def start(update, context):
    keyboard = [
        [KeyboardButton("Открыть мини-приложение",
                        web_app=WebAppInfo(url=WEBAPP_URL))]
    ]

    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Добро пожаловать!", reply_markup=markup)


telegram_app.add_handler(CommandHandler("start", start))


# ---------------- Webhook ----------------
@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return {"ok": True}


# ---------------- Webapp page ----------------
@app.get("/webapp", response_class=HTMLResponse)
async def webapp(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# ---------------- Startup ----------------
@app.on_event("startup")
async def on_startup():
    webhook_url = "https://telegram-mini-adshare-afxx.onrender.com/webhook"

    await telegram_app.bot.delete_webhook(drop_pending_updates=True)
    await telegram_app.bot.set_webhook(url=webhook_url)

    logger.info("Webhook установлен!")
