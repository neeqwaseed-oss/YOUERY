# ai_engineer_agent/config.py
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# مسارات المشروع
PROJECT_PATH = Path(os.getenv("PROJECT_PATH", "/home/user/telegram_whatsapp_link_extractor"))
AGENT_PATH = Path(__file__).parent
MEMORY_PATH = AGENT_PATH / "memory"
MEMORY_PATH.mkdir(exist_ok=True)

# مفاتيح API
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set in environment variables")

DEV_BOT_TOKEN = os.getenv("DEV_BOT_TOKEN")
if not DEV_BOT_TOKEN:
    raise ValueError("DEV_BOT_TOKEN is not set in environment variables")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# مستويات الاستقلالية
AUTO_FIX_LEVEL = os.getenv("AUTO_FIX_LEVEL", "safe")  # safe / moderate / full
# safe: إصلاح الأخطاء البسيطة فقط
# moderate: إصلاح الأخطاء + تعديل ملفات
# full: كل شيء تلقائيًا

# إعدادات المراقبة
HEALTH_CHECK_INTERVAL = int(os.getenv("HEALTH_CHECK_INTERVAL", 60))  # ثواني
MAX_AUTO_FIX_ATTEMPTS = int(os.getenv("MAX_AUTO_FIX_ATTEMPTS", 3))

# الأدوات المسموحة
ALLOWED_TOOLS = ["read", "write", "test", "restart", "install", "git"]

# إعدادات السجل
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_PATH = AGENT_PATH / "logs"
LOG_PATH.mkdir(exist_ok=True)

# إعدادات النموذج
AI_MODEL = os.getenv("AI_MODEL", "gpt-4")
AI_MAX_TOKENS = int(os.getenv("AI_MAX_TOKENS", 4000))
AI_TEMPERATURE = float(os.getenv("AI_TEMPERATURE", 0.1))

# إعدادات Git
GIT_ENABLED = os.getenv("GIT_ENABLED", "true").lower() == "true"
GIT_AUTO_COMMIT = os.getenv("GIT_AUTO_COMMIT", "true").lower() == "true"

# إعدادات الاختبارات
TEST_TIMEOUT = int(os.getenv("TEST_TIMEOUT", 30))