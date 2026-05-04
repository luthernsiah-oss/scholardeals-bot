import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_ID = int(os.getenv("TELEGRAM_ADMIN_ID", "0"))

MENU = [["📄 Buy Checker Cards", "🎓 University Forms"],
        ["📚 Study Materials", "📞 Contact Admin"]]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to ScholarDeals 🎓\n\nChoose an option:",
        reply_markup=ReplyKeyboardMarkup(MENU, resize_keyboard=True)
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "📄 Buy Checker Cards":
        await update.message.reply_text(
            "WASSCE Checker\nPrice: GH¢18.50\n\nSend payment to:\nMoMo: 0530790707\nName: Frank Nsiah\n\nAfter payment, send screenshot."
        )

    elif text == "🎓 University Forms":
        await update.message.reply_text(
            "Get university forms via WhatsApp:\nhttps://wa.me/233530790707"
        )

    elif text == "📚 Study Materials":
        await update.message.reply_text(
            "Send what you need (course + level). Admin will reply you."
        )

    elif text == "📞 Contact Admin":
        await update.message.reply_text(
            "Chat admin:\nhttps://wa.me/233530790707"
        )

    else:
        await update.message.reply_text("Please choose from the menu.")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user

    caption = f"New payment screenshot\nName: {user.full_name}\nUsername: @{user.username}\nUser ID: {user.id}"

    await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=update.message.photo[-1].file_id,
        caption=caption
    )

    await update.message.reply_text("Payment received. Waiting for approval.")

async def reply_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    try:
        user_id = int(context.args[0])
        message = " ".join(context.args[1:])

        await context.bot.send_message(chat_id=user_id, text=message)
        await update.message.reply_text("Message sent.")
    except:
        await update.message.reply_text("Usage: /reply user_id message")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reply", reply_command))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
