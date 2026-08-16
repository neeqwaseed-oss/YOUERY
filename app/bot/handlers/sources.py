"""
Sources handlers - manage source selection and listing.
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from app.bot.keyboards.sources import get_sources_keyboard, get_source_back_keyboard
from app.bot.keyboards.main import get_main_menu_keyboard
from app.bot.keyboards.scan import get_scan_menu_keyboard
from app.bot.states.scan_states import ScanStates
from app.database.repositories.source_repo import SourceRepository
from app.telegram.source_reader import SourceReader
from app.telegram.userbot_manager import UserbotManager
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = Router()


@router.callback_query(F.data == "menu:sources")
async def menu_sources(callback: CallbackQuery):
    """Show sources menu."""
    await callback.answer()
    
    user_id = callback.from_user.id
    source_repo = SourceRepository()
    
    # Get sources from database
    sources = await source_repo.get_by_user(user_id)
    
    if not sources:
        await callback.message.edit_text(
            "📂 <b>Sources</b>\n\n"
            "No sources found. Please scan a channel or group first.\n\n"
            "To add a source, use the bot to extract links from a channel or group.",
            reply_markup=get_main_menu_keyboard(),
            parse_mode="HTML"
        )
        return
    
    text = "📂 <b>Your Sources</b>\n\n"
    for i, source in enumerate(sources, 1):
        source_type = {
            'group': '👥',
            'supergroup': '👥',
            'channel': '📢'
        }.get(source.source_type, '📁')
        
        text += f"{i}. {source_type} <b>{source.title}</b>\n"
        if source.username:
            text += f"   @{source.username}\n"
        text += f"   ID: <code>{source.telegram_chat_id}</code>\n\n"
    
    await callback.message.edit_text(
        text,
        reply_markup=get_source_back_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "source:refresh")
async def refresh_sources(callback: CallbackQuery):
    """Refresh sources list."""
    await callback.answer("🔄 Refreshing sources...")
    
    user_id = callback.from_user.id
    userbot = UserbotManager()
    
    try:
        # Initialize userbot if needed
        if not userbot.is_initialized:
            await userbot.initialize()
        
        # Get sources from Telegram
        source_reader = SourceReader(userbot)
        telegram_sources = await source_reader.get_accessible_sources()
        
        # Save to database
        source_repo = SourceRepository()
        saved_count = 0
        
        for source in telegram_sources:
            try:
                await source_repo.create(
                    telegram_user_id=user_id,
                    telegram_chat_id=source['id'],
                    title=source['title'],
                    username=source.get('username'),
                    source_type=source['type']
                )
                saved_count += 1
            except Exception as e:
                logger.warning(f"Failed to save source {source['id']}: {e}")
        
        # Get updated sources
        sources = await source_repo.get_by_user(user_id)
        
        text = f"✅ <b>Sources Refreshed</b>\n"
        text += f"Added/Updated: {saved_count} sources\n\n"
        text += "📂 <b>Your Sources</b>\n\n"
        
        for i, source in enumerate(sources, 1):
            source_type = {
                'group': '👥',
                'supergroup': '👥',
                'channel': '📢'
            }.get(source.source_type, '📁')
            
            text += f"{i}. {source_type} <b>{source.title}</b>\n"
            if source.username:
                text += f"   @{source.username}\n"
            text += f"   ID: <code>{source.telegram_chat_id}</code>\n\n"
        
        await callback.message.edit_text(
            text,
            reply_markup=get_source_back_keyboard(),
            parse_mode="HTML"
        )
        
    except Exception as e:
        logger.error(f"Failed to refresh sources: {e}")
        await callback.message.edit_text(
            "❌ <b>Failed to refresh sources</b>\n\n"
            f"Error: {str(e)}",
            reply_markup=get_source_back_keyboard(),
            parse_mode="HTML"
        )
    finally:
        await userbot.disconnect()


@router.callback_query(F.data.startswith("source:select:"))
async def select_source(callback: CallbackQuery, state: FSMContext):
    """Select a source for scanning."""
    source_id = int(callback.data.split(":")[2])
    
    await callback.answer(f"Selected source ID: {source_id}")
    
    # Save source ID in state
    await state.update_data(selected_source_id=source_id)
    
    # Get source info
    source_repo = SourceRepository()
    source = await source_repo.get_by_id(source_id)
    
    if not source:
        await callback.message.edit_text(
            "❌ <b>Source not found</b>\n\n"
            "The selected source no longer exists.",
            reply_markup=get_main_menu_keyboard(),
            parse_mode="HTML"
        )
        return
    
    # Show scan mode selection
    await callback.message.edit_text(
        f"🔍 <b>Selected Source</b>\n\n"
        f"📌 <b>{source.title}</b>\n"
        f"{'@' + source.username if source.username else ''}\n\n"
        f"Choose scan mode:",
        reply_markup=get_scan_menu_keyboard(),
        parse_mode="HTML"
    )
    
    await state.set_state(ScanStates.select_mode)


@router.callback_query(F.data == "source:back")
async def source_back(callback: CallbackQuery):
    """Go back from sources menu."""
    await callback.answer()
    await callback.message.edit_text(
        "🔗 <b>Link Extractor</b>\n\n"
        "Choose an operation:",
        reply_markup=get_main_menu_keyboard(),
        parse_mode="HTML"
    )