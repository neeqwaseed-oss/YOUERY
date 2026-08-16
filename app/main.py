"""
Main entry point for the Telegram Bot.
"""

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from app.config import config
from app.bot.router import router
from app.database.database import init_database
from app.telegram.userbot_manager import UserbotManager
from app.utils.logger import setup_logging


async def main():
    """Main entry point for the application."""

    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)

    bot = None

    try:
        # =========================================================
        # 1. Initialize database
        # =========================================================
        logger.info("Initializing database...")
        await init_database()

        # =========================================================
        # 2. Initialize Telegram Bot
        # =========================================================
        logger.info("Initializing bot...")

        bot = Bot(
            token=config.BOT_TOKEN
        )

        # =========================================================
        # 3. Initialize Dispatcher + FSM Storage
        # =========================================================
        storage = MemoryStorage()

        dp = Dispatcher(
            storage=storage
        )

        # Register main router
        dp.include_router(router)

        # =========================================================
        # 4. Initialize Userbot Manager
        # =========================================================
        logger.info("Setting up userbot manager...")

        userbot_manager = UserbotManager()

        # Userbot is intentionally NOT started here.
        # It will be initialized when required by the scan system.

        # =========================================================
        # 5. Configure Bot Commands
        # =========================================================
        commands = [
            BotCommand(
                command="start",
                description="Start the bot"
            ),
            BotCommand(
                command="help",
                description="Get help"
            )
        ]

        await bot.set_my_commands(commands)

        # =========================================================
        # 6. Start Bot Polling
        # =========================================================
        logger.info("Bot started successfully!")

        await dp.start_polling(
            bot
        )

    except Exception as e:
        logger.error(
            f"Failed to start bot: {e}",
            exc_info=True
        )
        raise

    finally:
        # =========================================================
        # 7. Graceful Shutdown
        # =========================================================
        if bot is not None:
            await bot.session.close()

        logger.info("Bot stopped.")


if __name__ == "__main__":
    asyncio.run(main())