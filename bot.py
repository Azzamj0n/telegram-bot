import random
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

TOKEN = "8228632825:AAFwJ9ZYJtj8DhmbO4wTA3CdiAtYhcDIkoM"
games = {}
leaderboard = {}
tournament_scores = {}

def main_menu():
    keyboard = [
        ["🎮 Играть"],
        ["🏆 Таблица лидеров"],
        ["🏟 Турнир"],
        ["⭐ Мой рейтинг"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Добро пожаловать в игру 🎯 Угадай число!",
        reply_markup=main_menu()
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    if text == "🎮 Играть":
        keyboard = [
            ["🟢 Легкий (1-50)"],
            ["🟡 Средний (1-100)"],
            ["🔴 Сложный (1-500)"]
        ]
        await update.message.reply_text(
            "Выбери уровень:",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )
        return

    if "Легкий" in text:
        number = random.randint(1, 50)
    elif "Средний" in text:
        number = random.randint(1, 100)
    elif "Сложный" in text:
        number = random.randint(1, 500)
    elif text == "🏆 Таблица лидеров":
        if not leaderboard:
            await update.message.reply_text("Пока нет результатов.", reply_markup=main_menu())
            return
        top = sorted(leaderboard.items(), key=lambda x: x[1])[:5]
        message = "🏆 Топ игроков:\n"
        for i, (uid, score) in enumerate(top, 1):
            message += f"{i}. ID {uid} — {score} попыток\n"
        await update.message.reply_text(message, reply_markup=main_menu())
        return

    elif text == "🏟 Турнир":
        tournament_scores[user_id] = 0
        number = random.randint(1, 100)
        games[user_id] = {"number": number, "attempts": 0, "tournament": True}
        await update.message.reply_text("Турнир начался! Угадай число 1-100")
        return

    elif text == "⭐ Мой рейтинг":
        if user_id in leaderboard:
            await update.message.reply_text(
                f"Твой лучший результат: {leaderboard[user_id]} попыток",
                reply_markup=main_menu()
            )
        else:
            await update.message.reply_text(
                "Ты ещё не играл!",
                reply_markup=main_menu()
            )
        return

    else:
        if user_id not in games:
            return

        try:
            guess = int(text)
        except:
            await update.message.reply_text("Введите число!")
            return

        games[user_id]["attempts"] += 1
        secret = games[user_id]["number"]

        if guess < secret:
            await update.message.reply_text("Больше 📈")
        elif guess > secret:
            await update.message.reply_text("Меньше 📉")
        else:
            attempts = games[user_id]["attempts"]

            if games[user_id].get("tournament"):
                tournament_scores[user_id] += 1
                await update.message.reply_text(
                    f"🏟 Очко засчитано! Всего: {tournament_scores[user_id]}"
                )
            else:
                if user_id not in leaderboard or attempts < leaderboard[user_id]:
                    leaderboard[user_id] = attempts

                await update.message.reply_text(
                    f"🎉 Угадал за {attempts} попыток!",
                    reply_markup=main_menu()
                )

            del games[user_id]

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

app.run_polling()
