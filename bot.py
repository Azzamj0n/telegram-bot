import random
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Здесь вставь токен
TOKEN = "8228632825:AAFwJ9ZYJtj8DhmbO4wTA3CdiAtYhcDIkoM"

# Словарь для хранения игры каждого пользователя
games = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    number = random.randint(1, 100)
    
    games[user_id] = {
        "number": number,
        "attempts": 0
    }

    await update.message.reply_text(
        "🎮 Я загадал число от 1 до 100.\nПопробуй угадать!"
    )

async def guess(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in games:
        await update.message.reply_text("Напиши /start чтобы начать игру.")
        return

    try:
        user_guess = int(update.message.text)
    except:
        await update.message.reply_text("Введите число!")
        return

    games[user_id]["attempts"] += 1
    secret_number = games[user_id]["number"]

    if user_guess < secret_number:
        await update.message.reply_text("📉 Больше!")
    elif user_guess > secret_number:
        await update.message.reply_text("📈 Меньше!")
    else:
        attempts = games[user_id]["attempts"]
        await update.message.reply_text(
            f"🎉 Ты угадал за {attempts} попыток!\nНапиши /start чтобы сыграть снова."
        )
        del games[user_id]

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, guess))

app.run_polling()
