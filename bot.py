import os
import random
import logging

from telegram import Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

import google.generativeai as genai

# ================== CONFIG ================== #

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID", "0"))

SUPPORT_CHANNEL = os.getenv("SUPPORT_CHANNEL", "@your_channel")
SUPPORT_GROUP = os.getenv("SUPPORT_GROUP", "@your_group")

# ================== LOGGING ================== #

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# ================== GEMINI ================== #

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("models/gemini-1.5-flash")

REACTIONS = ["❤️", "😍", "😊", "🥰", "💖", "😘"]

# ================== HANDLERS ================== #

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    text = (
        f"Hey {user.first_name} 💕\n\n"
        "Main ek AI chatbot hoon ✨\n"
        "Mujhse kuch bhi baat karo 😌\n\n"
        f"📢 Channel: {SUPPORT_CHANNEL}\n"
        f"👥 Group: {SUPPORT_GROUP}"
    )

    await update.message.reply_text(text)

    if LOG_CHANNEL_ID != 0:
        await context.bot.send_message(
            chat_id=LOG_CHANNEL_ID,
            text=f"🟢 New user\n👤 {user.id} | {user.first_name}"
        )

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    try:
        response = model.generate_content(user_text)

        if not response.text:
            raise Exception("Empty Gemini response")

        reply = response.text

    except Exception as e:
        logging.error(f"Gemini error: {e}")
        reply = "Aww 😔 thoda issue aa gaya, fir se try karo 💕"

    await update.message.reply_text(reply)

    if random.random() < 0.4:
        await update.message.reply_text(random.choice(REACTIONS))

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if not context.args:
        await update.message.reply_text("❌ Usage:\n/broadcast Hello everyone")
        return

    msg = " ".join(context.args)

    if LOG_CHANNEL_ID != 0:
        await context.bot.send_message(
            chat_id=LOG_CHANNEL_ID,
            text=f"📢 Broadcast:\n{msg}"
        )

    await update.message.reply_text("✅ Broadcast sent")

# ================== MAIN ================== #

def main():
    app: Application = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    print("🤖 Bot started successfully")
    app.run_polling()

if __name__ == "__main__":
    main()
