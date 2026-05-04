import logging
import os
import psycopg2
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# CONFIG
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
MOMO_NUMBER = os.getenv("MOMO_NUMBER")
ACCOUNT_NAME = os.getenv("ACCOUNT_NAME")
DATABASE_URL = os.getenv("DATABASE_URL")

# DB CONNECT
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# CREATE TABLES
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY,
    referrer BIGINT,
    balance NUMERIC DEFAULT 0
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    user_id BIGINT,
    item TEXT,
    amount NUMERIC,
    status TEXT DEFAULT 'pending'
);
""")

conn.commit()

# MENU
menu = ReplyKeyboardMarkup([
    ["📄 Buy Checker", "🎓 University Forms"],
    ["📦 My Orders", "🏆 Affiliate"]
], resize_keyboard=True)

# UNIVERSITY PRICES
UNI_FORMS = {
    "UG": 295, "KNUST": 295, "UCC": 295, "UEW": 295,
    "UDS": 295, "UMaT": 295, "UHAS": 295, "UENR": 295,
    "UPSA": 295, "GIMPA": 295, "AAMUSTED": 295,
    "CKT-UTAS": 295, "SDD-UBIDS": 295, "UESD": 295,
    "GCTU": 295, "UniMAC": 295
}

TECH_FORMS = {
    "ATU": 250, "KsTU": 250, "KTU": 250,
    "CCTU": 250, "TTU": 250, "HTU": 250, "BTU": 250
}

# START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    ref = context.args[0] if context.args else None

    cur.execute("SELECT * FROM users WHERE user_id=%s", (user.id,))
    if not cur.fetchone():
        cur.execute("INSERT INTO users (user_id, referrer) VALUES (%s,%s)", (user.id, ref))
        conn.commit()

    await update.message.reply_text(
        "Welcome to ScholarDeals Bot 👋",
        reply_markup=menu
    )

# BUY CHECKER
async def buy_checker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"Send payment to:\n{MOMO_NUMBER}\n{ACCOUNT_NAME}\n\nThen send screenshot."
    )

# UNIVERSITY FORMS
async def university_forms(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "🎓 University Forms:\n\n"

    for uni, price in UNI_FORMS.items():
        text += f"{uni} — GH¢{price}\n"

    text += "\n🏫 Technical Universities:\n\n"

    for uni, price in TECH_FORMS.items():
        text += f"{uni} — GH¢{price}\n"

    await update.message.reply_text(text)

# ORDERS
async def my_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    cur.execute("SELECT item, amount, status FROM orders WHERE user_id=%s", (user_id,))
    rows = cur.fetchall()

    if not rows:
        await update.message.reply_text("No orders yet.")
        return

    msg = "📦 Your Orders:\n\n"
    for item, amount, status in rows:
        msg += f"{item} — GH¢{amount} ({status})\n"

    await update.message.reply_text(msg)

# AFFILIATE DASHBOARD
async def affiliate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    cur.execute("SELECT balance FROM users WHERE user_id=%s", (user_id,))
    balance = cur.fetchone()[0]

    bot_username = (await context.bot.get_me()).username
    link = f"https://t.me/{bot_username}?start={user_id}"

    msg = f"""
🏆 Affiliate Dashboard

💰 Balance: GH¢ {balance}

🔗 Your Link:
{link}

Share this link and earn!
"""
    await update.message.reply_text(msg)

# HANDLE TEXT
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "📄 Buy Checker":
        await buy_checker(update, context)

    elif text == "🎓 University Forms":
        await university_forms(update, context)

    elif text == "📦 My Orders":
        await my_orders(update, context)

    elif text == "🏆 Affiliate":
        await affiliate(update, context)

# MAIN
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("myorders", my_orders))
app.add_handler(MessageHandler(filters.TEXT, handle))

print("Bot running...")
app.run_polling()
