# ScholarDeals Ghana Bot - Railway Stable Full Version

import os
import logging
import psycopg2
from psycopg2 import pool

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# ───────────────── LOGGING ─────────────────

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# ───────────────── ENV ─────────────────

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
ADMIN_ID = int(os.getenv("TELEGRAM_ADMIN_ID", "8255451505"))

if not BOT_TOKEN:
    raise Exception("Missing TELEGRAM_BOT_TOKEN")
if not DATABASE_URL:
    raise Exception("Missing DATABASE_URL")

# ───────────────── DB ─────────────────

db_pool = None

def init_db():
    global db_pool
    db_pool = psycopg2.pool.ThreadedConnectionPool(1, 10, DATABASE_URL)

    conn = db_pool.getconn()
    try:
        cur = conn.cursor()

        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id BIGINT PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            referrer_id BIGINT,
            affiliate_balance NUMERIC(10,2) DEFAULT 0,
            joined_at TIMESTAMP DEFAULT NOW()
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            order_type TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT NOW()
        )
        """)

        conn.commit()
        logger.info("Database ready")

    finally:
        cur.close()
        db_pool.putconn(conn)

# ───────────────── DB HELPERS ─────────────────

def get_user(uid):
    conn = db_pool.getconn()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE id=%s", (uid,))
        return cur.fetchone()
    finally:
        cur.close()
        db_pool.putconn(conn)

def register_user(uid, username, name):
    conn = db_pool.getconn()
    try:
        cur = conn.cursor()
        cur.execute("""
        INSERT INTO users (id, username, full_name)
        VALUES (%s, %s, %s)
        ON CONFLICT (id) DO NOTHING
        """, (uid, username, name))
        conn.commit()
    finally:
        cur.close()
        db_pool.putconn(conn)

def create_order(uid, order_type):
    conn = db_pool.getconn()
    try:
        cur = conn.cursor()
        cur.execute("""
        INSERT INTO orders (user_id, order_type)
        VALUES (%s, %s) RETURNING id
        """, (uid, order_type))
        oid = cur.fetchone()[0]
        conn.commit()
        return oid
    finally:
        cur.close()
        db_pool.putconn(conn)

# ───────────────── UI ─────────────────

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📄 Checker Cards", callback_data="checker")],
        [InlineKeyboardButton("🎓 University Forms", callback_data="forms")],
        [InlineKeyboardButton("🤝 Affiliate", callback_data="affiliate")]
    ])

# ───────────────── START ─────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    register_user(user.id, user.username or "", user.full_name or "")

    await update.message.reply_text(
        "Welcome to ScholarDeals Ghana Bot 🚀",
        reply_markup=main_menu()
    )

# ───────────────── MENU ─────────────────

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if q.data == "checker":
        oid = create_order(q.from_user.id, "checker")
        await q.edit_message_text(f"Checker section (Order #{oid}) coming soon.")

    elif q.data == "forms":
        oid = create_order(q.from_user.id, "forms")
        await q.edit_message_text(f"Forms section (Order #{oid}) coming soon.")

    elif q.data == "affiliate":
        await q.edit_message_text("Affiliate system coming soon.")

# ───────────────── MESSAGE ─────────────────

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Use the buttons to continue.")

# ───────────────── ERROR ─────────────────

async def error(update, context):
    logger.error("Error:", exc_info=context.error)

# ───────────────── MAIN ─────────────────

def main():
    init_db()

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(menu))
    app.add_handler(MessageHandler(filters.ALL, handle_message))

    app.add_error_handler(error)

    logger.info("Bot starting...")
    app.run_polling()

if __name__ == "__main__":
    main()
