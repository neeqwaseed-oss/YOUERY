"""
Results handlers - display scan results with pagination.
"""

from typing import List, Dict, Any

from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.database.repositories.link_repo import LinkRepository
from app.database.repositories.result_repo import ResultRepository
from app.database.repositories.scan_repo import ScanRepository
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = Router()

# Pagination settings
ITEMS_PER_PAGE = 20


@router.callback_query(F.data.startswith("result:"))
async def show_results_menu(callback: CallbackQuery):
    """Show results menu for a job."""
    await callback.answer()
    
    parts = callback.data.split(":")
    job_id = int(parts[2])
    
    result_repo = ResultRepository()
    scan_repo = ScanRepository()
    
    # Get job info and statistics
    job = await scan_repo.get_by_id(job_id)
    stats = await result_repo.get_statistics(job_id)
    
    if not job:
        await callback.message.edit_text(
            "❌ <b>Job not found</b>\n\n"
            "The scan job no longer exists.",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="⬅️ Back", callback_data="menu:back")]
                ]
            ),
            parse_mode="HTML"
        )
        return
    
    # Build results menu
    text = f"📊 <b>Results for Job #{job_id}</b>\n\n"
    
    if stats:
        text += f"📱 Telegram: {stats.get('telegram_count', 0)}\n"
        text += f"├─ 👥 Groups: {stats.get('group_count', 0)}\n"
        text += f"├─ 📢 Channels: {stats.get('channel_count', 0)}\n"
        text += f"└─ 🔗 Invites: {stats.get('invite_count', 0)}\n\n"
        text += f"💬 WhatsApp: {stats.get('whatsapp_count', 0)}\n"
        text += f"└─ 👥 Groups: {stats.get('group_count', 0)}\n\n"
        text += f"❌ Excluded: {stats.get('personal_count', 0) + stats.get('bot_count', 0)}\n"
        text += f"🔄 Duplicates: {stats.get('duplicate_count', 0)}\n"
    
    # Build navigation keyboard
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="📱 Telegram", callback_data=f"result:telegram:{job_id}"))
    builder.add(InlineKeyboardButton(text="💬 WhatsApp", callback_data=f"result:whatsapp:{job_id}"))
    builder.add(InlineKeyboardButton(text="❌ Excluded", callback_data=f"result:excluded:{job_id}"))
    builder.add(InlineKeyboardButton(text="🔄 Duplicates", callback_data=f"result:duplicates:{job_id}"))
    builder.add(InlineKeyboardButton(text="📤 Export", callback_data=f"export:menu:{job_id}"))
    builder.add(InlineKeyboardButton(text="⬅️ Back", callback_data="menu:back"))
    builder.adjust(1)
    
    await callback.message.edit_text(
        text,
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("result:telegram:"))
async def show_telegram_results(callback: CallbackQuery):
    """Show Telegram results."""
    await callback.answer()
    
    parts = callback.data.split(":")
    job_id = int(parts[2])
    
    await show_filtered_results(callback.message, job_id, platform="telegram")


@router.callback_query(F.data.startswith("result:whatsapp:"))
async def show_whatsapp_results(callback: CallbackQuery):
    """Show WhatsApp results."""
    await callback.answer()
    
    parts = callback.data.split(":")
    job_id = int(parts[2])
    
    await show_filtered_results(callback.message, job_id, platform="whatsapp")


@router.callback_query(F.data.startswith("result:excluded:"))
async def show_excluded_results(callback: CallbackQuery):
    """Show excluded results."""
    await callback.answer()
    
    parts = callback.data.split(":")
    job_id = int(parts[2])
    
    await show_filtered_results(callback.message, job_id, status="excluded")


@router.callback_query(F.data.startswith("result:duplicates:"))
async def show_duplicate_results(callback: CallbackQuery):
    """Show duplicate results."""
    await callback.answer()
    
    parts = callback.data.split(":")
    job_id = int(parts[2])
    
    await show_filtered_results(callback.message, job_id, status="duplicate")


@router.callback_query(F.data.startswith("result:page:"))
async def paginate_results(callback: CallbackQuery):
    """Paginate through results."""
    await callback.answer()
    
    parts = callback.data.split(":")
    job_id = int(parts[2])
    page = int(parts[3])
    filter_type = parts[4] if len(parts) > 4 else "all"
    
    # Determine filter
    platform = None
    status = None
    link_type = None
    
    if filter_type == "telegram":
        platform = "telegram"
    elif filter_type == "whatsapp":
        platform = "whatsapp"
    elif filter_type == "excluded":
        status = "excluded"
    elif filter_type == "duplicates":
        status = "duplicate"
    
    await show_filtered_results(
        callback.message, job_id, 
        platform=platform, status=status, 
        link_type=link_type, page=page
    )


async def show_filtered_results(
    message: CallbackQuery,
    job_id: int,
    platform: str = None,
    status: str = None,
    link_type: str = None,
    page: int = 1
):
    """Show filtered results with pagination."""
    
    link_repo = LinkRepository()
    
    # Calculate offset
    offset = (page - 1) * ITEMS_PER_PAGE
    
    # Get links
    links = await link_repo.get_by_job(
        scan_job_id=job_id,
        platform=platform,
        link_type=link_type,
        status=status,
        limit=ITEMS_PER_PAGE,
        offset=offset
    )
    
    # Get total count
    total_count = await link_repo.count_by_job(
        scan_job_id=job_id,
        platform=platform,
        link_type=link_type,
        status=status
    )
    
    if not links:
        await message.edit_text(
            "📭 <b>No results found</b>\n\n"
            "No links match the selected filter.",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="⬅️ Back to Results", callback_data=f"result:latest:{job_id}")]
                ]
            ),
            parse_mode="HTML"
        )
        return
    
    # Build results text
    title = "📊 Results"
    if platform:
        title = f"📱 {platform.title()}"
    elif status:
        if status == "excluded":
            title = "❌ Excluded"
        elif status == "duplicate":
            title = "🔄 Duplicates"
    
    text = f"{title} (Page {page}/{max(1, (total_count + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE)})\n\n"
    
    for i, link in enumerate(links, 1):
        url = link.get('original_url', 'Unknown')
        if len(url) > 50:
            url = url[:47] + "..."
        
        text += f"{i + offset}. <a href='{link.get('original_url')}'>{url}</a>\n"
        
        if link.get('entity_title'):
            text += f"   📌 {link['entity_title']}\n"
        if link.get('entity_username'):
            text += f"   @{link['entity_username']}\n"
        if link.get('link_type'):
            text += f"   Type: {link['link_type']}\n"
        text += "\n"
    
    # Build pagination keyboard
    builder = InlineKeyboardBuilder()
    
    total_pages = max(1, (total_count + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE)
    
    # Determine filter type for pagination
    filter_type = "all"
    if platform:
        filter_type = platform
    elif status:
        filter_type = status
    
    # Previous page
    if page > 1:
        builder.add(
            InlineKeyboardButton(
                text="⬅️ Previous",
                callback_data=f"result:page:{job_id}:{page - 1}:{filter_type}"
            )
        )
    
    # Next page
    if page < total_pages:
        builder.add(
            InlineKeyboardButton(
                text="➡️ Next",
                callback_data=f"result:page:{job_id}:{page + 1}:{filter_type}"
            )
        )
    
    # Back button
    builder.add(
        InlineKeyboardButton(
            text="⬅️ Back to Results",
            callback_data=f"result:latest:{job_id}"
        )
    )
    
    builder.adjust(2)
    
    await message.edit_text(
        text,
        reply_markup=builder.as_markup(),
        parse_mode="HTML",
        disable_web_page_preview=True
    )