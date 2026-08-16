"""
Scan handlers - manage scan operations and progress.
"""

import asyncio
from typing import Dict, Any

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.states.scan_states import ScanStates
from app.bot.keyboards.scan import (
    get_scan_menu_keyboard, get_scan_confirmation_keyboard,
    get_scan_stop_keyboard
)
from app.bot.keyboards.main import get_main_menu_keyboard
from app.database.repositories.scan_repo import ScanRepository
from app.database.repositories.source_repo import SourceRepository
from app.workers.scan_worker import ScanWorker
from app.telegram.userbot_manager import UserbotManager
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = Router()


@router.callback_query(F.data == "menu:scan")
async def menu_scan(callback: CallbackQuery):
    """Show scan menu."""
    await callback.answer()
    
    user_id = callback.from_user.id
    source_repo = SourceRepository()
    
    # Get sources from database
    sources = await source_repo.get_by_user(user_id)
    
    if not sources:
        await callback.message.edit_text(
            "🔍 <b>Extract Links</b>\n\n"
            "No sources found. Please refresh sources first.\n\n"
            "Use /start to return to main menu.",
            reply_markup=get_main_menu_keyboard(),
            parse_mode="HTML"
        )
        return
    
    # Build source selection keyboard
    builder = InlineKeyboardBuilder()
    for source in sources:
        source_type = {
            'group': '👥',
            'supergroup': '👥',
            'channel': '📢'
        }.get(source.source_type, '📁')
        
        title = source.title or f"Source {source.telegram_chat_id}"
        if len(title) > 30:
            title = title[:27] + "..."
        
        builder.add(
            InlineKeyboardButton(
                text=f"{source_type} {title}",
                callback_data=f"source:select:{source.id}"
            )
        )
    
    builder.add(InlineKeyboardButton(text="🔄 Refresh", callback_data="source:refresh"))
    builder.add(InlineKeyboardButton(text="⬅️ Back", callback_data="menu:back"))
    builder.adjust(1)
    
    await callback.message.edit_text(
        "🔍 <b>Select Source</b>\n\n"
        "Choose a source to scan:",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )


@router.callback_query(ScanStates.select_mode, F.data.startswith("scan:mode:"))
async def select_scan_mode(callback: CallbackQuery, state: FSMContext):
    """Select scan mode."""
    mode = callback.data.split(":")[2]
    
    await callback.answer(f"Selected mode: {mode}")
    await state.update_data(scan_mode=mode)
    
    if mode == "recent":
        # Show limit selection
        builder = InlineKeyboardBuilder()
        limits = [100, 500, 1000, 5000, 10000]
        for limit in limits:
            builder.add(
                InlineKeyboardButton(
                    text=f"📨 {limit} messages",
                    callback_data=f"scan:limit:{limit}"
                )
            )
        builder.add(InlineKeyboardButton(text="⬅️ Back", callback_data="menu:back"))
        builder.adjust(1)
        
        await callback.message.edit_text(
            "📊 <b>Select Limit</b>\n\n"
            "How many recent messages to scan?",
            reply_markup=builder.as_markup(),
            parse_mode="HTML"
        )
        await state.set_state(ScanStates.enter_limit)
        
    elif mode == "full":
        # Full scan - no additional parameters
        await state.set_state(ScanStates.confirm_scan)
        await show_confirmation(callback.message, state)
        
    elif mode == "range":
        # Ask for start message ID
        await callback.message.edit_text(
            "📊 <b>Range Scan</b>\n\n"
            "Enter the <b>start message ID</b>:\n\n"
            "Format: <code>12345</code>\n\n"
            "You can find message IDs using @idbot or by looking at the message link.",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="⬅️ Back", callback_data="menu:back")]
                ]
            ),
            parse_mode="HTML"
        )
        await state.set_state(ScanStates.enter_start_message)


@router.callback_query(ScanStates.enter_limit, F.data.startswith("scan:limit:"))
async def select_limit(callback: CallbackQuery, state: FSMContext):
    """Select message limit."""
    limit = int(callback.data.split(":")[2])
    
    await callback.answer(f"Selected limit: {limit}")
    await state.update_data(limit=limit)
    await state.set_state(ScanStates.confirm_scan)
    
    await show_confirmation(callback.message, state)


@router.message(ScanStates.enter_start_message)
async def enter_start_message(message: Message, state: FSMContext):
    """Enter start message ID."""
    try:
        start_id = int(message.text.strip())
        await state.update_data(start_message_id=start_id)
        
        # Ask for end message ID
        await message.answer(
            "📊 <b>Enter End Message ID</b>\n\n"
            "Enter the <b>end message ID</b>:\n\n"
            "Format: <code>12345</code>\n\n"
            "Leave empty or type '0' to scan to the latest message.",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="⬅️ Back", callback_data="menu:back")]
                ]
            ),
            parse_mode="HTML"
        )
        await state.set_state(ScanStates.enter_end_message)
        
    except ValueError:
        await message.answer(
            "❌ <b>Invalid message ID</b>\n\n"
            "Please enter a valid number.",
            parse_mode="HTML"
        )


@router.message(ScanStates.enter_end_message)
async def enter_end_message(message: Message, state: FSMContext):
    """Enter end message ID."""
    try:
        text = message.text.strip()
        if text and text != "0":
            end_id = int(text)
            await state.update_data(end_message_id=end_id)
        else:
            await state.update_data(end_message_id=None)
        
        await state.set_state(ScanStates.confirm_scan)
        await show_confirmation(message, state)
        
    except ValueError:
        await message.answer(
            "❌ <b>Invalid message ID</b>\n\n"
            "Please enter a valid number or 0 for latest.",
            parse_mode="HTML"
        )


async def show_confirmation(message: Message, state: FSMContext):
    """Show scan confirmation."""
    data = await state.get_data()
    
    # Get source info
    source_repo = SourceRepository()
    source = await source_repo.get_by_id(data['selected_source_id'])
    
    if not source:
        await message.answer(
            "❌ <b>Source not found</b>\n\n"
            "Please start over with /start.",
            parse_mode="HTML"
        )
        await state.clear()
        return
    
    # Build confirmation text
    text = "🔎 <b>Confirm Scan</b>\n\n"
    text += f"📌 <b>Source:</b> {source.title}\n"
    if source.username:
        text += f"   @{source.username}\n"
    text += f"\n"
    text += f"📊 <b>Mode:</b> {data['scan_mode'].upper()}\n"
    
    if data['scan_mode'] == 'recent':
        text += f"📨 <b>Limit:</b> {data.get('limit', 1000)} messages\n"
    elif data['scan_mode'] == 'range':
        text += f"📨 <b>Range:</b> {data.get('start_message_id')} → {data.get('end_message_id') or 'latest'}\n"
    
    text += "\n<b>Settings:</b>\n"
    text += "✅ Telegram Groups\n"
    text += "✅ Telegram Channels\n"
    text += "✅ Telegram Invites\n"
    text += "✅ WhatsApp Groups\n"
    text += "❌ Personal Accounts (excluded)\n"
    text += "❌ Bots (excluded)\n"
    text += "❌ Other Links (excluded)\n"
    text += "🔄 Duplicates (removed)\n"
    text += "\n<i>Ready to start scanning?</i>"
    
    await message.answer(
        text,
        reply_markup=get_scan_confirmation_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(ScanStates.confirm_scan, F.data == "scan:confirm")
async def confirm_scan(callback: CallbackQuery, state: FSMContext):
    """Confirm and start scan."""
    await callback.answer("🚀 Starting scan...")
    await callback.message.edit_text(
        "🔄 <b>Starting scan...</b>\n\n"
        "Please wait while the scan initializes.",
        parse_mode="HTML"
    )
    
    data = await state.get_data()
    user_id = callback.from_user.id
    
    # Create scan job
    scan_repo = ScanRepository()
    job = await scan_repo.create(
        telegram_user_id=user_id,
        source_id=data['selected_source_id'],
        scan_mode=data['scan_mode'],
        limit=data.get('limit', 1000),
        start_message_id=data.get('start_message_id'),
        end_message_id=data.get('end_message_id')
    )
    
    # Store job ID in state
    await state.update_data(scan_job_id=job.id)
    await state.set_state(ScanStates.scanning)
    
    # Start scan worker
    userbot = UserbotManager()
    try:
        await userbot.initialize()
        scan_worker = ScanWorker(userbot)
        
        # Send progress message
        progress_message = await callback.message.answer(
            "🔎 <b>Scanning...</b>\n\n"
            "📨 Messages: 0 / ?\n"
            "🔗 Links found: 0\n"
            "🟢 Unique links: 0\n\n"
            "⏳ <i>Processing...</i>",
            reply_markup=get_scan_stop_keyboard(job.id),
            parse_mode="HTML"
        )
        
        # Run scan with progress updates
        async def update_progress(stats: Dict[str, Any]):
            total_messages = stats.get('messages_scanned', 0)
            limit = data.get('limit', '?')
            
            progress_text = (
                f"🔎 <b>Scanning...</b>\n\n"
                f"📨 Messages: {total_messages} / {limit}\n"
                f"🔗 Links found: {stats.get('urls_found', 0)}\n"
                f"🟢 Unique links: {stats.get('urls_unique', 0)}\n\n"
                f"📱 Telegram: {stats.get('telegram_count', 0)}\n"
                f"💬 WhatsApp: {stats.get('whatsapp_count', 0)}\n"
                f"👤 Personal: {stats.get('personal_count', 0)}\n"
                f"🤖 Bots: {stats.get('bot_count', 0)}\n"
                f"🔄 Duplicates: {stats.get('duplicate_count', 0)}\n\n"
                f"⏳ <i>Scanning...</i>"
            )
            
            try:
                await progress_message.edit_text(
                    progress_text,
                    reply_markup=get_scan_stop_keyboard(job.id),
                    parse_mode="HTML"
                )
            except Exception:
                pass  # Ignore edit errors (rate limiting)
        
        # Run the scan
        stats = await scan_worker.run_scan(
            job_id=job.id,
            source_id=data['selected_source_id'],
            user_id=user_id,
            scan_mode=data['scan_mode'],
            limit=data.get('limit', 1000),
            start_message_id=data.get('start_message_id'),
            end_message_id=data.get('end_message_id'),
            progress_callback=update_progress
        )
        
        # Show final results
        await show_scan_results(callback.message, job.id, stats)
        
    except Exception as e:
        logger.error(f"Scan failed: {e}")
        await callback.message.answer(
            f"❌ <b>Scan Failed</b>\n\n"
            f"Error: {str(e)}",
            parse_mode="HTML"
        )
    finally:
        await userbot.disconnect()
        await state.clear()


@router.callback_query(ScanStates.scanning, F.data.startswith("scan:stop:"))
async def stop_scan(callback: CallbackQuery, state: FSMContext):
    """Stop current scan."""
    job_id = int(callback.data.split(":")[2])
    
    await callback.answer("🛑 Stopping scan...")
    await callback.message.edit_text(
        "🛑 <b>Stopping scan...</b>\n\n"
        "Please wait while we clean up...",
        parse_mode="HTML"
    )
    
    # Get scan worker and cancel
    userbot = UserbotManager()
    try:
        scan_worker = ScanWorker(userbot)
        scan_worker.cancel()
        
        # Update job status
        scan_repo = ScanRepository()
        await scan_repo.update_status(job_id, 'cancelled')
        
        await callback.message.answer(
            "🛑 <b>Scan Cancelled</b>\n\n"
            "The scan has been stopped.",
            reply_markup=get_main_menu_keyboard(),
            parse_mode="HTML"
        )
    finally:
        await userbot.disconnect()
        await state.clear()


@router.callback_query(ScanStates.confirm_scan, F.data == "scan:cancel")
async def cancel_scan(callback: CallbackQuery, state: FSMContext):
    """Cancel scan before starting."""
    await callback.answer("❌ Scan cancelled")
    await state.clear()
    await callback.message.edit_text(
        "❌ <b>Scan Cancelled</b>\n\n"
        "Returning to main menu.",
        reply_markup=get_main_menu_keyboard(),
        parse_mode="HTML"
    )


async def show_scan_results(message: Message, job_id: int, stats: Dict[str, Any]):
    """Show final scan results."""
    text = "✅ <b>Scan Completed!</b>\n\n"
    text += "📊 <b>Results</b>\n\n"
    text += f"📨 Messages scanned: {stats.get('messages_scanned', 0)}\n"
    text += f"🔗 Links found: {stats.get('urls_found', 0)}\n"
    text += f"🟢 Unique links: {stats.get('urls_unique', 0)}\n\n"
    
    text += "📱 <b>Telegram</b>\n"
    text += f"├─ 👥 Groups: {stats.get('group_count', 0)}\n"
    text += f"├─ 📢 Channels: {stats.get('channel_count', 0)}\n"
    text += f"└─ 🔗 Invites: {stats.get('invite_count', 0)}\n\n"
    
    text += "💬 <b>WhatsApp</b>\n"
    text += f"└─ 👥 Groups: {stats.get('whatsapp_count', 0)}\n\n"
    
    text += "❌ <b>Excluded</b>\n"
    text += f"├─ 👤 Personal: {stats.get('personal_count', 0)}\n"
    text += f"├─ 🤖 Bots: {stats.get('bot_count', 0)}\n"
    text += f"├─ 🔄 Duplicates: {stats.get('duplicate_count', 0)}\n"
    text += f"└─ 🌐 Other: {stats.get('other_count', 0)}\n"
    
    # Build results navigation keyboard
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="📊 View Results", callback_data=f"result:latest:{job_id}"))
    builder.add(InlineKeyboardButton(text="📤 Export", callback_data=f"export:menu:{job_id}"))
    builder.add(InlineKeyboardButton(text="⬅️ Back to Menu", callback_data="menu:back"))
    builder.adjust(1)
    
    await message.answer(
        text,
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )