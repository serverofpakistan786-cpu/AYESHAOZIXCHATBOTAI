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

# ---------------- LOGGING ----------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ---------------- ENV VARIABLES ----------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID", "0"))
SUPPORT_CHANNEL_LINK = os.getenv("SUPPORT_CHANNEL_LINK", "")
GROUP_LINK = os.getenv("GROUP_LINK", "")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ---------------- GEMINI SETUP ----------------
genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel(
    model_name="models/gemini-1.5-flash"
)

# ---------------- PERSONALITY ----------------
SYSTEM_PROMPT = """
You are AYESHA XOZIX, a friendly, cute, respectful female AI chatbot.
You speak in Hinglish.
You sound sweet, caring and natural.
Sometimes use emojis.
Do not sound robotic.
"""

# ---------------- START COMMAND ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    buttons = []
    if SUPPORT_CHANNEL_LINK:
        buttons.append([InlineKeyboardButton("💬 Support", url=SUPPORT_CHANNEL_LINK)])
    if GROUP_LINK:
        buttons.append([InlineKeyboardButton("👥 Group", url=GROUP_LINK)])

    await update.message.reply_text(
        f"Heyy {user.first_name} 💖\n"
        "Main AYESHA XOZIX hoon 😊\n"
        "Tum mujhse kuch bhi baat kar sakte ho...",
        reply_markup=InlineKeyboardMarkup(buttons) if buttons else None
    )

    # Log channel (safe)
    if LOG_CHANNEL_ID != 0:
        try:
            await context.bot.send_message(
                chat_id=LOG_CHANNEL_ID,
                text=f"🆕 New User Started Bot\n👤 {user.first_name} | {user.id}"
            )
        except Exception as e:
            logging.error(f"Log channel error: {e}")

# ---------------- CHAT HANDLER ----------------
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    prompt = f"""
{SYSTEM_PROMPT}

User: {text}
AI:
"""

    try:
        response = model.generate_content(prompt)
        reply = response.candidates[0].content.parts[0].text.strip()
    except Exception as e:
        logging.error(f"Gemini Error: {e}")
        reply = "Aww 😕 thoda sa issue aa gaya, phir se try karo na."

    await update.message.reply_text(reply)

# ---------------- STATS (OWNER) ----------------
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    await update.message.reply_text("✅ Bot is running fine on Koyeb")

# ---------------- MAIN ----------------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    app.run_polling()

if __name__ == "__main__":
    main()
