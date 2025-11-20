# bot.py
import os
from telegram import Bot, Update, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
WEBAPP_URL = os.environ.get("WEBAPP_URL")  # например https://your-render-service.onrender.com/

if not TOKEN or not WEBAPP_URL:
    print("Установите переменные окружения TELEGRAM_BOT_TOKEN и WEBAPP_URL")
    raise SystemExit

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [
        [KeyboardButton("Открыть MiniApp", web_app=WebAppInfo(url=https://telegram-mini-adshare-afxx.onrender.com/webapp))]
    ]
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Откройте Mini App:", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    print("Бот запущен. Отправьте /start в Telegram.")
    app.run_polling()
