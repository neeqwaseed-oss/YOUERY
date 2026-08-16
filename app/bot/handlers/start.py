"""
Start and main menu handlers.
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart

from app.bot.keyboards.main import get_main_menu_keyboard
from app.bot.keyboards.sources import get_sources_keyboard
from app.bot.keyboards.scan import get_scan_menu_keyboard
from app.bot.keyboards.results import get_results_menu_keyboard
from app.bot.keyboards.export import get_export_menu_keyboard
from app.database.repositories.user_repo import UserRepository
from app.telegram.userbot_manager import UserbotManager
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    """Handle /start command."""
    logger.info(f"User {message.from_user.id} started the bot")
    
    # Save user to database
    repo = UserRepository()
    await repo.create_or_update(
        telegram_user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name
    )
    
    welcome_text = (
        "🔗 <b>Link Extractor Bot</b>\n\n"
        "Welcome! I can help you extract Telegram and WhatsApp links "
        "from messages in channels and groups.\n\n"
        "To get started, choose an operation below:"
    )
    
    await message.answer(
        welcome_text,
        reply_markup=get_main_menu_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "menu:back")
async def back_to_main_menu(callback: CallbackQuery):
    """Return to main menu."""
    await callback.answer()
    await callback.message.edit_text(
        "🔗 <b>Link Extractor</b>\n\n"
        "Choose an operation:",
        reply_markup=get_main_menu_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "menu:scan")
async def menu_scan(callback: CallbackQuery):
    """Show scan menu."""
    await callback.answer()
    
    # Check if userbot is initialized
    userbot = UserbotManager()
    try:
        if not userbot.is_initialized:
            await callback.message.edit_text(
                "🔄 <b>Initializing...</b>\n\n"
                "Please wait while I connect to Telegram...",
                parse_mode="HTML"
            )
            await userbot.initialize()
    except Exception as e:
        logger.error(f"Failed to initialize userbot: {e}")
        await callback.message.edit_text(
            "❌ <b>Failed to initialize</b>\n\n"
            f"Error: {str(e)}\n\n"
            "Please check your API credentials and try again.",
            reply_markup=get_main_menu_keyboard(),
            parse_mode="HTML"
        )
        return
    finally:
        await userbot.disconnect()
    
    await callback.message.edit_text(
        "🔍 <b>Extract Links</b>\n\n"
        "Choose a source to scan:",
        reply_markup=get_sources_keyboard(callback.from_user.id),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "menu:sources")
async def menu_sources(callback: CallbackQuery):
    """Show sources menu."""
    await callback.answer()
    
    # Redirect to sources handler
    from app.bot.handlers.sources import menu_sources as sources_handler
    await sources_handler(callback)


@router.callback_query(F.data == "menu:results")
async def menu_results(callback: CallbackQuery):
    """Show results menu."""
    await callback.answer()
    
    # Redirect to results handler
    await callback.message.edit_text(
        "📊 <b>Results</b>\n\n"
        "Please use the scan menu first to extract links.",
        reply_markup=get_main_menu_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "menu:exports")
async def menu_exports(callback: CallbackQuery):
    """Show exports menu."""
    await callback.answer()
    
    # Redirect to export handler
    await callback.message.edit_text(
        "📤 <b>Export</b>\n\n"
        "Please scan first to have results to export.",
        reply_markup=get_main_menu_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "menu:settings")
async def menu_settings(callback: CallbackQuery):
    """Show settings menu."""
    await callback.answer()
    
    # Redirect to settings handler
    from app.bot.handlers.settings import menu_settings as settings_handler
    await settings_handler(callback)