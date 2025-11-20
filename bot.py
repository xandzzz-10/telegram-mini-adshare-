from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "8583826837:AAGJI6Qf5QvI_GXva_xzWs9Eo1i96jKLJC0"

WEBAPP_URL = "https://telegram-mini-adshare-afxx.onrender.com/webapp"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("📊 Открыть приложение", web_app=WebAppInfo(url=WEBAPP_URL))]
    ]

    await update.message.reply_text(
        "Добро пожаловать! 👋\nНажмите кнопку ниже, чтобы открыть мини-приложение:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()

if __name__ == "__main__":
    main()
