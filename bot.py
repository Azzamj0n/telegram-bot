import random
from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

TOKEN = "8228632825:AAFwJ9ZYJtj8DhmbO4wTA3CdiAtYhcDIkoM"

users = {}
games = {}

def main_menu():
    keyboard = [
        [InlineKeyboardButton("🎮 Играть", callback_data="play")],
        [InlineKeyboardButton("💰 Баланс", callback_data="balance")],
        [InlineKeyboardButton("🏆 Лидеры", callback_data="leaders")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in users:
        users[user_id] = 100  # стартовые монеты

    await update.message.reply_text(
        "🎯 Добро пожаловать в игру!\n"
        f"💰 Твой баланс: {users[user_id]} монет",
        reply_markup=main_menu()
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "play":
        keyboard = [
            [InlineKeyboardButton("10 💰", callback_data="bet_10")],
            [InlineKeyboardButton("20 💰", callback_data="bet_20")],
            [InlineKeyboardButton("50 💰", callback_data="bet_50")]
        ]
        await query.message.reply_text(
            "Выбери ставку:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data.startswith("bet_"):
        bet = int(query.data.split("_")[1])

        if users[user_id] < bet:
            await query.message.reply_text("❌ Недостаточно монет!")
            return

        users[user_id] -= bet
        number = random.randint(1, 100)

        games[user_id] = {
            "number": number,
            "bet": bet
        }

        await query.message.reply_text(
            f"🎲 Я загадал число от 1 до 100.\n"
            f"Ставка: {bet} 💰\n"
            "Попробуй угадать!"
        )

    elif query.data == "balance":
        await query.message.reply_text(
            f"💰 Твой баланс: {users[user_id]} монет",
            reply_markup=main_menu()
        )

    elif query.data == "leaders":
        if not users:
            await query.message.reply_text("Пока нет игроков.")
            return

        top = sorted(users.items(), key=lambda x: x[1], reverse=True)[:5]
        text = "🏆 Топ игроков по балансу:\n"
        for i, (uid, coins) in enumerate(top, 1):
            text += f"{i}. ID {uid} — {coins} 💰\n"

        await query.message.reply_text(text)

async def guess(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in games:
        return

    try:
        guess = int(update.message.text)
    except:
        await update.message.reply_text("Введите число!")
        return

    secret = games[user_id]["number"]
    bet = games[user_id]["bet"]

    if guess < secret:
        await update.message.reply_text("Больше 📈")
    elif guess > secret:
        await update.message.reply_text("Меньше 📉")
    else:
        win = bet * 2
        users[user_id] += win
        await update.message.reply_text(
            f"🎉 Ты выиграл!\n"
            f"+{win} 💰\n"
            f"Новый баланс: {users[user_id]}",
            reply_markup=main_menu()
        )
        del games[user_id]

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, guess))

app.run_polling()
