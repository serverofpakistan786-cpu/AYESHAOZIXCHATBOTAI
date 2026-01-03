import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

OWNER_ID = int(os.getenv("OWNER_ID"))

LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID"))
SUPPORT_CHANNEL = os.getenv("SUPPORT_CHANNEL")
SUPPORT_GROUP = os.getenv("SUPPORT_GROUP")
