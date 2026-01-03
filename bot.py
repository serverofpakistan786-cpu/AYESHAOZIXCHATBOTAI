import os
import random
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
)
from google import genai

# ================= CONFIG =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID"))
SUPPORT_CHANNEL = os.getenv("SUPPORT_CHANNEL")  # @username
SUPPORT_GROUP = os.getenv("SUPPORT_GROUP")      # @username
# =========================================

# Gemini Client
client = genai.Client(api_key=GEMINI_API_KEY)

logging.basicConfig(level=logging.INFO)

REACTIONS = ["🥰", "❤️", "😍", "😘", "😊", "💖", "✨"]

# ---------- START ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"Hey {user.first_name} 💖\n"
        f"Main tumhari AI dost hoon 🥰\n\n"
        f"👉 Support: {SUPPORT_CHANNEL}\n"
        f"👉 Group: {SUPPORT_GROUP}"
    )

    await context.bot.send_message(
        LOG_CHANNEL_ID,
        f"🟢 Bot started by:\n👤 {user.first_name}\n🆔 {user.id}"
    )

# ---------- BROADCAST ----------
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if not context.args:
        await update.message.reply_text("❌ Message do broadcast ke liye")
        return

    msg = " ".join(context.args)

    await context.bot.send_message(LOG_CHANNEL_ID, f"📢 Broadcast:\n{msg}")
    await update.message.reply_text("✅ Broadcast sent")

# ---------- GEMINI CHAT ----------
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=text
        )

        reply = response.text
        reaction = random.choice(REACTIONS)

        await update.message.reply_text(f"{reply}\n\n{reaction}")

    except Exception as e:
        await update.message.reply_text("😔 Thoda issue aa gaya, baad me try karo")
        await context.bot.send_message(LOG_CHANNEL_ID, f"❌ Error:\n{e}")

# ---------- MAIN ----------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
