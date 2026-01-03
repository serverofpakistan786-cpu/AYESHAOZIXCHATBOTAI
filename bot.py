import os
import logging
import random
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from telegram.constants import ChatAction
import google.generativeai as genai

# ================= LOGGING =================
logging.basicConfig(level=logging.INFO)

# ================= ENV SAFE LOAD =================
def env(name, cast=str, default=None):
    val = os.getenv(name, default)
    if val is None:
        raise RuntimeError(f"Missing ENV: {name}")
    return cast(val)

BOT_TOKEN = env("BOT_TOKEN")
GEMINI_API_KEY = env("GEMINI_API_KEY")
ADMIN_ID = env("ADMIN_ID", int)
LOG_CHANNEL_ID = env("LOG_CHANNEL_ID", int)

SUPPORT_CHANNEL = os.getenv("SUPPORT_CHANNEL", "")
SUPPORT_GROUP = os.getenv("SUPPORT_GROUP", "")

# ================= GEMINI =================
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

REACTIONS = ["❤️", "😍", "🥰", "😊", "✨", "🔥", "💖"]

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        f"Hey {update.effective_user.first_name} 🥰\n\n"
        "Main Gemini AI ChatBot hoon 🤖✨\n"
        "Kuch bhi pooch sakte ho 💬\n\n"
    )
    if SUPPORT_CHANNEL:
        msg += f"📢 Channel: {SUPPORT_CHANNEL}\n"
    if SUPPORT_GROUP:
        msg += f"👥 Group: {SUPPORT_GROUP}\n"

    await update.message.reply_text(msg)

    await context.bot.send_message(
        LOG_CHANNEL_ID,
        f"🚀 /start by {update.effective_user.id}"
    )

# ================= BROADCAST =================
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if not context.args:
        await update.message.reply_text("/broadcast your message")
        return

    text = " ".join(context.args)
    await update.message.reply_text("✅ Broadcast sent (logging enabled)")

    await context.bot.send_message(
        LOG_CHANNEL_ID,
        f"📢 Broadcast:\n{text}"
    )

# ================= CHAT =================
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(update.effective_chat.id, ChatAction.TYPING)

    try:
        res = model.generate_content(update.message.text)
        reply = res.text
    except Exception as e:
        logging.error(e)
        reply = "🥺 Abhi thoda issue aa gaya, baad me try karo."

    await update.message.reply_text(reply)
    await update.message.reply_text(random.choice(REACTIONS))

# ================= MAIN =================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    logging.info("🤖 Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
