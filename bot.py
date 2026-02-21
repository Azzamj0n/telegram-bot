import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

TOKEN = os.getenv("TOKEN")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

auth_manager = SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET
)
sp = spotipy.Spotify(auth_manager=auth_manager)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Напиши название песни 🎵")

async def search_music(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    await update.message.reply_text("Ищу варианты... 🔍")

    results = sp.search(q=query, type="track", limit=5)

    tracks = results["tracks"]["items"]

    if not tracks:
        await update.message.reply_text("Ничего не найдено 😔")
        return

    context.user_data["tracks"] = tracks

    keyboard = []
    for i, track in enumerate(tracks):
        name = track["name"]
        artist = track["artists"][0]["name"]
        keyboard.append(
            [InlineKeyboardButton(f"{name} — {artist}", callback_data=str(i))]
        )

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Выбери нужную песню:",
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    index = int(query.data)
    track = context.user_data["tracks"][index]

    name = track["name"]
    artist = track["artists"][0]["name"]
    image = track["album"]["images"][0]["url"]
    url = track["external_urls"]["spotify"]

    keyboard = [
        [InlineKeyboardButton("Открыть в Spotify 🎧", url=url)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.reply_photo(
        photo=image,
        caption=f"🎵 {name}\n👤 {artist}",
        reply_markup=reply_markup
    )

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_music))
app.add_handler(CallbackQueryHandler(button_handler))

app.run_polling()
