import os
import logging
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

import google.generativeai as genai

# -------------------- LOGGING --------------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# -------------------- ENV --------------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

OWNER_ID = int(os.getenv("OWNER_ID", "0"))
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID", "0"))

# ⚠️ HARD-CODED LINKS (NO INLINE BUTTON ERROR)
SUPPORT_CHANNEL_LINK = "https://t.me/+KKYgpQNCwbgwODdl"
GROUP_LINK = "https://t.me/+M9pETo_ZmGFhODk9"

# -------------------- GEMINI --------------------
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro")

# -------------------- PERSONALITY --------------------
SYSTEM_PROMPT = (
    "You are AYESHAXOZIX, a friendly, cute, respectful female AI chatbot.\n"
    "You talk in Hinglish, sound caring, sweet and natural.\n"
    "Use emojis sometimes. Do not act robotic.\n"
)

# -------------------- START --------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    buttons = [
        [
            InlineKeyboardButton("💬 Support", url=SUPPORT_CHANNEL_LINK),
            InlineKeyboardButton("👥 Group", url=GROUP_LINK),
        ]
    ]

    await update.message.reply_text(
        f"Heyy {user.first_name} 💖\n"
        "Main AYESHAXOZIX hoon 😄\n"
        "Tum mujhse kuch bhi baat kar sakte ho...",
        reply_markup=InlineKeyboardMarkup(buttons),
    )

    if LOG_CHANNEL_ID != 0:
        await context.bot.send_message(
            LOG_CHANNEL_ID,
            f"🆕 New User Started Bot\n👤 {user.first_name} | {user.id}",
        )

# -------------------- CHAT --------------------
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text

    prompt = f"""
{SYSTEM_PROMPT}

User: {text}
AI:
"""

    try:
        response = model.generate_content(prompt)
        reply = response.text.strip()
    except Exception:
        reply = "Aww 😕 thoda sa issue aa gaya, phir se try karo na."

    await update.message.reply_text(reply)

# -------------------- MAIN --------------------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    print("✅ Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
