import os
import logging
import pandas as pd

from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates

from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app")

TOKEN = os.getenv("BOT_TOKEN", "ТВОЙ_ТОКЕН")
WEBAPP_URL = "https://telegram-mini-adshare-afxx.onrender.com/webapp"
WEBHOOK_URL = "https://telegram-mini-adshare-afxx.onrender.com/webhook"

app = FastAPI()
templates = Jinja2Templates(directory="templates")

telegram_app = ApplicationBuilder().token(TOKEN).build()

# ------------------------------------------------
# /start
# ------------------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            KeyboardButton(
                "Открыть мини-приложение",
                web_app=WebAppInfo(url=WEBAPP_URL)
            )
        ]
    ]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Добро пожаловать!", reply_markup=markup)

telegram_app.add_handler(CommandHandler("start", start))


# ------------------------------------------------
# Получение обновлений от Telegram
# ------------------------------------------------
@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return {"ok": True}


# ------------------------------------------------
# WEBAPP (интерфейс)
# ------------------------------------------------
@app.get("/webapp", response_class=HTMLResponse)
async def webapp(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# ------------------------------------------------
# PROCESS EXCEL FILES  ← ЭТО ВАЖНО!
# ------------------------------------------------
@app.post("/process")
async def process_files(main_file: UploadFile = File(...),
                        payments_file: UploadFile = File(...)):
    try:
        df_main = pd.read_excel(main_file.file)
        df_pay = pd.read_excel(payments_file.file)

        # Пример логики — замени своей!
        df_result = df_main.copy()
        df_result["sum"] = df_main.sum(axis=1)

        result_path = "/tmp/result.xlsx"
        df_result.to_excel(result_path, index=False)

        return FileResponse(result_path, filename="result.xlsx")

    except Exception as e:
        return {"error": str(e)}


# ------------------------------------------------
# УСТАНОВКА WEBHOOK
# ------------------------------------------------
@app.on_event("startup")
async def on_startup():
    await telegram_app.bot.delete_webhook(drop_pending_updates=True)

    await telegram_app.bot.set_webhook(url=WEBHOOK_URL)
    logger.info("Webhook установлен!")
