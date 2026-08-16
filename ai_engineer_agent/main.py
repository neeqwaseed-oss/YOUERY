# ai_engineer_agent/main.py
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import DEV_BOT_TOKEN, LOG_LEVEL
from bot.telegram_handler import router
from core.guardian import Guardian
from tools.terminal_tool import TerminalTool
from utils.logger import setup_logging

# إعداد السجل
setup_logging(LOG_LEVEL)
logger = logging.getLogger(__name__)


async def main():
    """النقطة الرئيسية لتشغيل الوكيل"""
    
    logger.info("🤖 AI Engineering Agent starting...")
    
    # 1. تهيئة البوت
    bot = Bot(token=DEV_BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    dp.include_router(router)
    
    # 2. تشغيل Guardian في الخلفية
    guardian = Guardian()
    asyncio.create_task(guardian.start_monitoring())
    logger.info("🛡️ Guardian Agent started")
    
    # 3. تشغيل البوت الرئيسي
    terminal = TerminalTool()
    terminal.start_bot()
    logger.info("🚀 Bot started")
    
    # 4. بدء polling
    logger.info("✅ AI Engineering Agent is ready!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())