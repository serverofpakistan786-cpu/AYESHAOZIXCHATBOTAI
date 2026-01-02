import os
import logging
from dotenv import load_dotenv

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

import google.generativeai as genai
from motor.motor_asyncio import AsyncIOMotorClient

# ---------------- LOAD ENV ----------------
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OWNER_ID = int(os.getenv("OWNER_ID"))
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID"))
SUPPORT_CHANNEL_LINK = os.getenv("SUPPORT_CHANNEL_LINK")
GROUP_LINK = os.getenv("GROUP_LINK")
MONGO_URI = os.getenv("MONGO_URI")

# ---------------- LOGGING ----------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# ---------------- GEMINI ----------------
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# ---------------- MONGO ----------------
mongo_client = AsyncIOMotorClient(MONGO_URI)
db = mongo_client["ayeshaxozix"]
users_col = db["users"]

# ---------------- FEMALE PERSONALITY PROMPT ----------------
SYSTEM_PROMPT = (
    "You are AYESHAXOZIX, a friendly, cute, respectful female AI chatbot. "
    "You talk in Hinglish, sound caring, sweet and natural. "
    "Use emojis sometimes. Do not act robotic. "
    "Remember user context if available."
)

# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    await users_col.update_one(
        {"user_id": user.id},
        {"$set": {"username": user.username, "name": user.first_name}},
        upsert=True,
    )

    buttons = [
        [
            InlineKeyboardButton("💬 Support", url=SUPPORT_CHANNEL_LINK),
            InlineKeyboardButton("👥 Group", url=GROUP_LINK),
        ]
    ]

    await update.message.reply_text(
        f"Heyy {user.first_name} 💖\n"
        "Main AYESHAXOZIX hoon 😄\n"
        "Tum mujhse kuch bhi baat kar sakte ho…",
        reply_markup=InlineKeyboardMarkup(buttons),
    )

    await context.bot.send_message(
        LOG_CHANNEL_ID,
        f"🟢 New User Started Bot\n👤 {user.first_name} | `{user.id}`",
        parse_mode="Markdown",
    )

# ---------------- AI CHAT ----------------
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text

    user_data = await users_col.find_one({"user_id": user.id})
    memory = user_data.get("memory", "") if user_data else ""

    prompt = f"""
{SYSTEM_PROMPT}

Previous memory:
{memory}

User: {text}
AI:
"""

    try:
        response = model.generate_content(prompt)
        reply = response.text.strip()
    except Exception as e:
        reply = "Awww 😕 thoda sa issue aa gaya, phir se try karo na."

    await update.message.reply_text(reply)

    await users_col.update_one(
        {"user_id": user.id},
        {"$set": {"memory": text[-500:]}},
        upsert=True,
    )

# ---------------- OWNER COMMAND ----------------
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return

    count = await users_col.count_documents({})
    await update.message.reply_text(f"👥 Total Users: {count}")

# ---------------- MAIN ----------------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    app.run_polling()

if __name__ == "__main__":
    main()
