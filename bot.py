import os
import random
import logging
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

import google.generativeai as genai

# ===================== LOGGING =====================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# ===================== SAFE ENV LOADER =====================
def get_env(name: str, cast=str):
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"❌ ENV missing: {name}")
    try:
        return cast(value)
    except Exception:
        raise RuntimeError(f"❌ ENV invalid format: {name}")

BOT_TOKEN = get_env("BOT_TOKEN")
GEMINI_API_KEY = get_env("GEMINI_API_KEY")
ADMIN_ID = get_env("ADMIN_ID", int)
LOG_CHANNEL_ID = get_env("LOG_CHANNEL_ID", int)

SUPPORT_CHANNEL = os.getenv("SUPPORT_CHANNEL", "")
SUPPORT_GROUP = os.getenv("SUPPORT_GROUP", "")

# ===================== GEMINI =====================
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# ===================== REACTIONS =====================
REACTIONS = ["❤️", "😍", "🥰", "😊", "✨", "🔥", "💖", "😌"]

# ===================== START =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = (
        f"Hey {user.first_name} 🥰\n\n"
        "Main ek AI chat bot hoon 🤖✨\n"
        "Mujhse kuch bhi pooch sakte ho.\n\n"
    )
    if SUPPORT_CHANNEL:
        text += f"📢 Channel: {SUPPORT_CHANNEL}\n"
    if SUPPORT_GROUP:
        text += f"👥 Group: {SUPPORT_GROUP}\n"

    await update.message.reply_text(text)

    await context.bot.send_message(
        chat_id=LOG_CHANNEL_ID,
        text=f"🚀 /start\nUser: {user.id} | @{user.username}",
    )

# ===================== BROADCAST =====================
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if not context.args:
        await update.message.reply_text("Usage:\n/broadcast Your message")
        return

    msg = " ".join(context.args)

    await context.bot.send_message(
        chat_id=LOG_CHANNEL_ID,
        text=f"📢 Broadcast sent:\n{msg}",
    )

    await update.message.reply_text("✅ Broadcast logged (users DB optional)")

# ===================== CHAT =====================
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action=ChatAction.TYPING,
    )

    user_text = update.message.text

    try:
        response = model.generate_content(user_text)
        reply = response.text
    except Exception as e:
        logging.error(e)
        reply = "🥺 Thoda issue aa gaya, baad me try karo."

    await update.message.reply_text(reply)

    # cute reaction
    try:
        await update.message.reply_text(random.choice(REACTIONS))
    except:
        pass

# ===================== MAIN =====================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    logging.info("🤖 Bot started successfully")
    app.run_polling()

if __name__ == "__main__":
    main()
