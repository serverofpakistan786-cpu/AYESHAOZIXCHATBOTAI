import os
import google.generativeai as genai
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ---------------- ENV ----------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

OWNER_ID = int(os.getenv("OWNER_ID"))
SUPPORT_CHANNEL_LINK = os.getenv("SUPPORT_CHANNEL_LINK")
GROUP_LINK = os.getenv("GROUP_LINK")
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID"))

# ---------------- GEMINI ----------------
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro")

# ---------------- PERSONALITY ----------------
SYSTEM_PROMPT = (
    "You are AYESHAXOZIX, a friendly, cute, respectful female AI chatbot.\n"
    "You talk in Hinglish, sound caring, sweet and natural.\n"
    "Use emojis sometimes. Do not act robotic.\n"
)

# ---------------- START ----------------
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

    await context.bot.send_message(
        LOG_CHANNEL_ID,
        f"🟢 New User Started Bot\n👤 {user.first_name} | `{user.id}`",
        parse_mode="Markdown",
    )

# ---------------- CHAT ----------------
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        reply = "Awww 😕 thoda sa issue aa gaya, phir se try karo na."

    await update.message.reply_text(reply)

# ---------------- OWNER STATS (NO MONGO) ----------------
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    await update.message.reply_text("👑 Bot is running perfectly 💖")

# ---------------- MAIN ----------------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    app.run_polling()

if __name__ == "__main__":
    main()
