"""Settings read from environment variables (.env in the backend folder)."""
import os

from dotenv import load_dotenv

load_dotenv()

ORE_BRAIN = os.getenv("ORE_BRAIN", "own").lower()
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-5-5")
ALLOWED_ORIGINS = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "http://localhost:5500").split(",")]
DB_PATH = os.getenv("DB_PATH", "plantwise.db")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "")
WA_VERIFY_TOKEN = os.getenv("WA_VERIFY_TOKEN", "")
WA_ACCESS_TOKEN = os.getenv("WA_ACCESS_TOKEN", "")
WA_PHONE_NUMBER_ID = os.getenv("WA_PHONE_NUMBER_ID", "")
WA_TEMPLATE_NAME = os.getenv("WA_TEMPLATE_NAME", "")
WA_TEMPLATE_LANG = os.getenv("WA_TEMPLATE_LANG", "en")
