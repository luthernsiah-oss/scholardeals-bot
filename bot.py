import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

MENU = [["📄 Buy Checker Cards", "🎓 University Forms"],
        ["📚 Study Materials", "📞 Contact Admin"]]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to ScholarDeals 🎓\n\nWhat do you want to do?",
        reply_markup=ReplyKeyboardMarkup(MENU, resize_keyboard=True)
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "📄 Buy Checker Cards":
        await update.message.reply_text(
            "WASSCE Checker available.\nPrice: GH¢18.50\n\nSend payment to:\nMoMo: 0530790707\nName: Frank Nsiah\n\nAfter payment, send screenshot."
        )

    elif text == "🎓 University Forms":
        await update.message.reply_text(
            "University forms available.\n\nJoin WhatsApp:\nhttps://chat.whatsapp.com/"
        )

    elif text == "📚 Study Materials":
        await update.message.reply_text(
            "Send the course and level you need.\nExample: Level 100 Chemistry"
        )

    elif text == "📞 Contact Admin":
        await update.message.reply_text(
            "Contact admin on WhatsApp:\nhttps://wa.me/233530790707"
        )

    else:
        await update.message.reply_text("Please choose an option from the menu.")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
