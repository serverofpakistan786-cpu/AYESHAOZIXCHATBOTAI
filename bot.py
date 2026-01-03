import logging
import random
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    CommandHandler,
    filters,
)
import google.generativeai as genai

from config import (
    BOT_TOKEN,
    GEMINI_API_KEY,
    OWNER_ID,
    LOG_CHANNEL_ID,
    SUPPORT_CHANNEL,
    SUPPORT_GROUP,
)
from reactions import random_reaction

logging.basicConfig(level=logging.INFO)

# Gemini setup
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

FALLBACK_REPLIES = [
    "Thoda sa busy hoon jaan 🙈",
    "Abhi thoda issue aa raha hai 😅",
    "Main hoon yahin ❤️ phir try karo",
]

USERS = set()

async def send_log(context, text):
    try:
        await context.bot.send_message(LOG_CHANNEL_ID, text)
    except:
        pass

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    USERS.add(user.id)

    msg = (
        f"Hi {user.first_name} 💖\n"
        f"Main Gemini AI ChatBot hoon 🤖\n\n"
        f"📢 Channel: {SUPPORT_CHANNEL}\n"
        f"👥 Group: {SUPPORT_GROUP}"
    )

    await update.message.reply_text(msg)

    await send_log(
        context,
        f"🟢 BOT STARTED\n"
        f"👤 User: {user.first_name}\n"
        f"🆔 ID: {user.id}",
    )

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    USERS.add(user.id)

    try:
        response = model.generate_content(update.message.text)
        reply = response.text.strip() if response.text else random.choice(FALLBACK_REPLIES)
    except Exception as e:
        logging.error(e)
        reply = random.choice(FALLBACK_REPLIES)

    sent = await update.message.reply_text(reply)

    if random.randint(1, 100) <= 40:
        try:
            await context.bot.send_message(
                chat_id=sent.chat_id,
                text=random_reaction(),
                reply_to_message_id=sent.message_id,
            )
        except:
            pass

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return

    if not context.args:
        await update.message.reply_text("❌ Message likho\n/broadcast Hello users")
        return

    text = " ".join(context.args)
    success = 0

    for uid in USERS:
        try:
            await context.bot.send_message(uid, text)
            success += 1
        except:
            pass

    await update.message.reply_text(f"✅ Broadcast sent to {success} users")
    await send_log(context, f"📢 BROADCAST DONE\nUsers: {success}")

async def bot_started(app):
    try:
        await app.bot.send_message(
            LOG_CHANNEL_ID,
            "🚀 Bot is LIVE on Koyeb\nAll systems running ✅",
        )
    except:
        pass

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).post_init(bot_started).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    app.run_polling()

if __name__ == "__main__":
    main()
