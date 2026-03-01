import random
import sqlite3
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# ====== ДАННЫЕ ======
TOKEN = "8228632825:AAFwJ9ZYJtj8DhmbO4wTA3CdiAtYhcDIkoM"
ADMIN_ID = 7037545654
CARD_NUMBER = "4444888814271817"

# ====== БАЗА ДАННЫХ ======
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

# ====== ХЕЛПЕРЫ ======
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

# ====== МЕНЮ ======
def main_menu():
    keyboard = [
        ["🎮 Играть", "💰 Баланс"],
        ["🏆 Лидеры", "💳 Пополнить баланс"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def difficulty_menu():
    keyboard = [
        ["🟢 Лёгкий 1.5x", "🟡 Средний 2x", "🔴 Сложный 3x"],
        ["⬅️ Назад"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ====== ИГРА ======
games = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    user = get_user(user_id, username)
    await update.message.reply_text(
        f"🎯 Добро пожаловать!\n💰 Баланс: {user[2]} монет",
        reply_markup=main_menu()
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    text = update.message.text
    user = get_user(user_id, username)
    balance = user[2]

    # ===== МЕНЮ =====
    if text == "💰 Баланс":
        await update.message.reply_text(f"💰 Твой баланс: {balance}", reply_markup=main_menu())
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

    if text == "💳 Пополнить баланс":
        await update.message.reply_text(
            f"💳 Чтобы пополнить баланс, переведи деньги на карту:\n"
            f"{CARD_NUMBER}\n"
            "1₽ = 1 монета\n"
            "После перевода отправь скрин с текстом «Подтвердить»",
            reply_markup=main_menu()
        )
        return

    if text == "🎮 Играть":
        await update.message.reply_text(
            "Выбери уровень сложности:",
            reply_markup=difficulty_menu()
        )
        return

    if text == "⬅️ Назад":
        await update.message.reply_text("Возврат в главное меню", reply_markup=main_menu())
        return

    # ===== Выбор сложности =====
    if text in ["🟢 Лёгкий 1.5x", "🟡 Средний 2x", "🔴 Сложный 3x"]:
        if user_id in games:
            await update.message.reply_text("Ты уже играешь!")
            return
        if text == "🟢 Лёгкий 1.5x":
            games[user_id] = {"number": random.randint(1, 50), "multiplier": 1.5}
        elif text == "🟡 Средний 2x":
            games[user_id] = {"number": random.randint(1, 100), "multiplier": 2}
        else:
            games[user_id] = {"number": random.randint(1, 300), "multiplier": 3}
        await update.message.reply_text("Введите ставку (макс 10000 монет):")
        return

    # ===== Ставка и угадайка =====
    if text.isdigit():
        if user_id in games and "bet" not in games[user_id]:
            bet = int(text)
            if bet > 10000:
                await update.message.reply_text("Максимальная ставка 10000")
                return
            if bet > balance:
                await update.message.reply_text("Недостаточно монет")
                return
            games[user_id]["bet"] = bet
            update_balance(user_id, balance - bet)
            await update.message.reply_text("Я загадал число. Угадывай!")
            return
        elif user_id in games and "bet" in games[user_id]:
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
                update_balance(user_id, current_balance + win)
                await update.message.reply_text(
                    f"🎉 Победа!\nВыигрыш: {win} 💰\nБаланс: {current_balance + win}",
                    reply_markup=main_menu()
                )
                del games[user_id]
            return

    # ===== Подтверждение пополнения (на кириллице) =====
    if text.lower() == "подтвердить":
        await update.message.reply_text("Спасибо! Админ проверит ваш платёж и добавит монеты.")
        return

# ===== КОМАНДЫ АДМИНА =====
async def addcoins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ Ты не админ!")
        return
    if len(context.args) != 2:
        await update.message.reply_text("Используй: /addcoins <user_id> <amount>")
        return
    target_id = int(context.args[0])
    amount = int(context.args[1])
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (target_id,))
    user = cursor.fetchone()
    if not user:
        await update.message.reply_text("Игрок не найден")
        return
    new_balance = user[0] + amount
    update_balance(target_id, new_balance)
    await update.message.reply_text(f"✅ Добавлено {amount} монет пользователю {target_id}")

# ===== Команда /мойid =====
async def мойid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Твой ID: {update.effective_user.id}")

# ===== RUN =====
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("addcoins", addcoins))
app.add_handler(CommandHandler("мойid", мойid))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.run_polling()
