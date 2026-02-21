import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("TOKEN")

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["Привет", "Извини"], ["Помощь"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Привет! Я бот, могу извиняться 😊", reply_markup=reply_markup)

# Любое сообщение
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()

    if "извини" in text or "прости" in text:
        await update.message.reply_text("Ничего страшного! Всё в порядке 😉")
    elif "привет" in text:
        await update.message.reply_text("Привет! Рад тебя видеть 😎")
    elif "помощь" in text:
        await update.message.reply_text("Напиши 'Извини', и я отвечу вежливо 😇")
    else:
        await update.message.reply_text("Я не понял, но всё равно тебе прощаю 😅")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

app.run_polling()
