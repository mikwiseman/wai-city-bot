import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
RUNWAY_API_KEY = os.getenv("RUNWAY_API_KEY")
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://mikwiseman.github.io/wai-city-bot")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not found in environment variables")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment variables")
if not RUNWAY_API_KEY:
    raise ValueError("RUNWAY_API_KEY not found in environment variables")