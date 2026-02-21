import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

TOKEN = os.getenv("TOKEN")
JAMENDO_API = os.getenv("JAMENDO_API")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Напиши название песни 🎵")

def search_music(query):
    url = "https://api.jamendo.com/v3.0/tracks/"
    params = {
        "client_id": JAMENDO_API,
        "format": "json",
        "limit": 1,
        "namesearch": query,
        "audioformat": "mp32"
    }
    response = requests.get(url, params=params)
    data = response.json()
    if data.get("results"):
        track = data["results"][0]
        return {
            "name": track["name"],
            "artist": track["artist_name"],
            "audio": track["audio"]
        }
    return None

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    await update.message.reply_text("Ищу песню... 🔍")

    track = search_music(query)

    if track:
        # Отправляем текст с названием и автором
        await update.message.reply_text(f"🎵 {track['name']} — {track['artist']}")
        await update.message.reply_audio(track["audio"])
    else:
        await update.message.reply_text("Песня не найдена 😔")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.run_polling()
