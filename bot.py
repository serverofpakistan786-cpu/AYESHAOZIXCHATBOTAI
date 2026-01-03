import os
import random
import asyncio
import logging

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

import google.generativeai as genai

# ---------------- CONFIG ---------------- #

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

ADMIN_ID = int(os.getenv("ADMIN_ID"))
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID"))

SUPPORT_CHANNEL = os.getenv("SUPPORT_CHANNEL")
SUPPORT_GROUP = os.getenv("SUPPORT_GROUP")

# ---------------- LOGGING ---------------- #

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ---------------- GEMINI ---------------- #

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro")

REACTIONS = ["❤️", "😍", "😊", "🥰", "💖", "😘"]

# ---------------- HANDLERS ---------------- #

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

    await context.bot.send_message(
        chat_id=LOG_CHANNEL_ID,
        text=f"🟢 New user started bot\n👤 {user.id} | {user.first_name}"
    )

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    try:
        response = model.generate_content(user_text)
        reply = response.text

    except Exception:
        reply = "Aww 😔 thoda issue aa gaya, fir se try karo 💕"

    await update.message.reply_text(reply)

    if random.random() < 0.4:
        await update.message.reply_text(random.choice(REACTIONS))

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if not context.args:
        await update.message.reply_text("❌ Message do\n/broadcast hello")
        return

    msg = " ".join(context.args)

    await context.bot.send_message(LOG_CHANNEL_ID, f"📢 Broadcast:\n{msg}")
    await update.message.reply_text("✅ Broadcast sent (log channel)")

# ---------------- MAIN ---------------- #

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    print("🤖 Bot started...")
    app.run_polling()

if __name__ == "__main__":
    main()
