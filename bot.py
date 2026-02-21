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

# Токены
TOKEN = os.getenv("TOKEN")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

# Авторизация Spotify
auth_manager = SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET
)
sp = spotipy.Spotify(auth_manager=auth_manager)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Напиши название песни 🎵")

# ПОИСК ПЕСЕН (заменяем всю функцию)
async def search_music(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    await update.message.reply_text("Ищу варианты... 🔍")

    results = sp.search(q=query, type="track", limit=5)
    tracks = results["tracks"]["items"]

    if not tracks:
        await update.message.reply_text("Ничего не найдено 😔")
        return

    # Обновляем треки для нового поиска
    context.user_data["tracks"] = tracks

    keyboard = [
        [InlineKeyboardButton(f"{track['name']} — {track['artists'][0]['name']}", callback_data=str(i))]
        for i, track in enumerate(tracks)
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выбери нужную песню:", reply_markup=reply_markup)

# ОБРАБОТКА НАЖАТИЙ (заменяем всю функцию)
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    tracks = context.user_data.get("tracks")
    if not tracks:
        await query.message.reply_text("Сначала сделайте новый поиск 🎵")
        return

    index = int(query.data)
    track = tracks[index]

    name = track["name"]
    artist = track["artists"][0]["name"]
    image = track["album"]["images"][0]["url"]
    url = track["external_urls"]["spotify"]

    keyboard = [[InlineKeyboardButton("Открыть в Spotify 🎧", url=url)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.reply_photo(
        photo=image,
        caption=f"🎵 {name}\n👤 {artist}",
        reply_markup=reply_markup
    )

# Создание приложения и регистрация хэндлеров
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_music))
app.add_handler(CallbackQueryHandler(button_handler))

app.run_polling()        caption=f"🎵 {name}\n👤 {artist}",
        reply_markup=reply_markup
    )

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_music))
app.add_handler(CallbackQueryHandler(button_handler))

app.run_polling()
