import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler,
    filters, ContextTypes
)

TOKEN = os.getenv("TOKEN")
JAMENDO_API = os.getenv("JAMENDO_API")

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Напиши название песни 🎵")

# Поиск треков через Jamendo API
def search_music(query):
    url = "https://api.jamendo.com/v3.0/tracks/"
    params = {
        "client_id": JAMENDO_API,
        "format": "json",
        "limit": 5,
        "namesearch": query,
        "audioformat": "mp32"
    }
    response = requests.get(url, params=params)
    data = response.json()
    results = []
    for track in data.get("results", []):
        results.append({
            "name": track["name"],
            "audio": track["audio"]
        })
    return results

# Обработка сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    await update.message.reply_text("Ищу песни... 🔍")

    tracks = search_music(query)
    if not tracks:
        await update.message.reply_text("Песни не найдены 😔")
        return

    # Создаём кнопки для каждого трека
    keyboard = []
    for i, track in enumerate(tracks):
        keyboard.append([InlineKeyboardButton(track["name"], callback_data=str(i))])
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Сохраняем треки в context для callback
    context.user_data["tracks"] = tracks
    await update.message.reply_text("Выберите трек:", reply_markup=reply_markup)

# Обработка нажатий на кнопки
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    idx = int(query.data)
    track = context.user_data["tracks"][idx]

    await query.message.reply_text(f"Скачиваем: {track['name']} 🎵")
    await query.message.reply_audio(track["audio"])

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.add_handler(CallbackQueryHandler(button))

app.run_polling()
