"""
Configuration module for the application.
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Bot configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set in environment variables")

API_ID = os.getenv("API_ID")
if not API_ID:
    raise ValueError("API_ID is not set in environment variables")

API_HASH = os.getenv("API_HASH")
if not API_HASH:
    raise ValueError("API_HASH is not set in environment variables")

SESSION_NAME = os.getenv("SESSION_NAME", "userbot_session")

# Database configuration
DATABASE_PATH = os.getenv("DATABASE_PATH", str(BASE_DIR / "data" / "app.db"))
DATABASE_DIR = Path(DATABASE_PATH).parent
DATABASE_DIR.mkdir(parents=True, exist_ok=True)

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Scan configuration
MAX_RETRIES = 3
RETRY_BACKOFF = [5, 10, 20]  # seconds
DEFAULT_SCAN_LIMIT = 1000
MAX_MESSAGES_PER_SCAN = 10000

# Rate limiting
RATE_LIMIT_PER_SECOND = 2
RATE_LIMIT_PER_MINUTE = 30

# Export configuration
EXPORT_DIR = BASE_DIR / "exports"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

# Session directory
SESSION_DIR = BASE_DIR / "sessions"
SESSION_DIR.mkdir(parents=True, exist_ok=True)

# Data directory
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# WhatsApp configuration
INCLUDE_WHATSAPP_GROUPS = True
INCLUDE_WHATSAPP_CONTACTS = False

# Telegram configuration
EXCLUDE_PERSONAL_ACCOUNTS = True
EXCLUDE_BOTS = True
EXCLUDE_DUPLICATES = True

# Results pagination
ITEMS_PER_PAGE = 20

# Temporary directory for exports
TEMP_DIR = BASE_DIR / "temp"
TEMP_DIR.mkdir(parents=True, exist_ok=True)


class Config:
    """Configuration class holding all settings."""
    
    BOT_TOKEN = BOT_TOKEN
    API_ID = API_ID
    API_HASH = API_HASH
    SESSION_NAME = SESSION_NAME
    DATABASE_PATH = DATABASE_PATH
    LOG_LEVEL = LOG_LEVEL
    MAX_RETRIES = MAX_RETRIES
    RETRY_BACKOFF = RETRY_BACKOFF
    DEFAULT_SCAN_LIMIT = DEFAULT_SCAN_LIMIT
    MAX_MESSAGES_PER_SCAN = MAX_MESSAGES_PER_SCAN
    RATE_LIMIT_PER_SECOND = RATE_LIMIT_PER_SECOND
    RATE_LIMIT_PER_MINUTE = RATE_LIMIT_PER_MINUTE
    EXPORT_DIR = EXPORT_DIR
    SESSION_DIR = SESSION_DIR
    DATA_DIR = DATA_DIR
    INCLUDE_WHATSAPP_GROUPS = INCLUDE_WHATSAPP_GROUPS
    INCLUDE_WHATSAPP_CONTACTS = INCLUDE_WHATSAPP_CONTACTS
    EXCLUDE_PERSONAL_ACCOUNTS = EXCLUDE_PERSONAL_ACCOUNTS
    EXCLUDE_BOTS = EXCLUDE_BOTS
    EXCLUDE_DUPLICATES = EXCLUDE_DUPLICATES
    ITEMS_PER_PAGE = ITEMS_PER_PAGE
    TEMP_DIR = TEMP_DIR


config = Config()