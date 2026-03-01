import random
import sqlite3
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

TOKEN = "8228632825:AAFwJ9ZYJtj8DhmbO4wTA3CdiAtYhcDIkoM"

# ================= DATABASE =================

conn = sqlite3.connect("game.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    balance INTEGER
)
""")
conn.commit()

# ================= MENU =================

def main_menu():
    keyboard = [
        ["🎮 Играть"],
        ["💰 Баланс"],
        ["🏆 Лидеры"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ================= HELPERS =================

def get_user(user_id, username):
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()

    if not user:
        name = username if username else "Пользователь"
        cursor.execute(
            "INSERT INTO users VALUES (?, ?, ?)",
            (user_id, name, 100)
        )
        conn.commit()
        return (user_id, name, 100)

    return user

def update_balance(user_id, new_balance):
    cursor.execute(
        "UPDATE users SET balance = ? WHERE user_id = ?",
        (new_balance, user_id)
    )
    conn.commit()

# ================= GAME =================

games = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username

    user = get_user(user_id, username)

    await update.message.reply_text(
        f"🎯 Добро пожаловать!\n"
        f"💰 Баланс: {user[2]} монет",
        reply_markup=main_menu()
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    text = update.message.text

    user = get_user(user_id, username)
    balance = user[2]

    if text == "💰 Баланс":
        await update.message.reply_text(
            f"💰 Твой баланс: {balance}",
            reply_markup=main_menu()
        )
        return

    if text == "🏆 Лидеры":
        cursor.execute("SELECT username, balance FROM users ORDER BY balance DESC LIMIT 5")
        top = cursor.fetchall()

        if not top:
            await update.message.reply_text("Нет игроков.", reply_markup=main_menu())
            return

        msg = "🏆 Топ игроков:\n"
        for i, (name, bal) in enumerate(top, 1):
            msg += f"{i}. {name} — {bal} 💰\n"

        await update.message.reply_text(msg, reply_markup=main_menu())
        return

    if text == "🎮 Играть":
        await update.message.reply_text(
            "Выбери сложность:\n"
            "1️⃣ Лёгкий (1-50) x1.5\n"
            "2️⃣ Средний (1-100) x2\n"
            "3️⃣ Сложный (1-300) x3"
        )
        return

    if text in ["1", "2", "3"]:
        if user_id in games:
            await update.message.reply_text("Ты уже играешь!")
            return

        context.user_data["difficulty"] = text
        await update.message.reply_text("Введите ставку (макс 10000):")
        return

    if text.isdigit():
        if "difficulty" in context.user_data:
            bet = int(text)

            if bet > 10000:
                await update.message.reply_text("Максимальная ставка 10000")
                return

            if bet > balance:
                await update.message.reply_text("Недостаточно монет")
                return

            difficulty = context.user_data["difficulty"]

            if difficulty == "1":
                number = random.randint(1, 50)
                multiplier = 1.5
            elif difficulty == "2":
                number = random.randint(1, 100)
                multiplier = 2
            else:
                number = random.randint(1, 300)
                multiplier = 3

            update_balance(user_id, balance - bet)

            games[user_id] = {
                "number": number,
                "bet": bet,
                "multiplier": multiplier
            }

            del context.user_data["difficulty"]

            await update.message.reply_text("Я загадал число. Угадывай!")
            return

        if user_id in games:
            guess = int(text)
            game = games[user_id]

            if guess < game["number"]:
                await update.message.reply_text("Больше 📈")
            elif guess > game["number"]:
                await update.message.reply_text("Меньше 📉")
            else:
                win = int(game["bet"] * game["multiplier"])
                cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
                current_balance = cursor.fetchone()[0]
                new_balance = current_balance + win
                update_balance(user_id, new_balance)

                await update.message.reply_text(
                    f"🎉 Победа!\n"
                    f"Выигрыш: {win} 💰\n"
                    f"Баланс: {new_balance}",
                    reply_markup=main_menu()
                )

                del games[user_id]
            return

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

app.run_polling()
