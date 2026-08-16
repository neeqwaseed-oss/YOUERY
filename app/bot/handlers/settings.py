"""
Settings handlers - manage bot settings.
"""

from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.config import config
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = Router()


@router.callback_query(F.data == "menu:settings")
async def menu_settings(callback: CallbackQuery):
    """Show settings menu."""
    await callback.answer()
    
    # Build settings status
    settings_text = "⚙️ <b>Settings</b>\n\n"
    
    # WhatsApp settings
    settings_text += "💬 <b>WhatsApp</b>\n"
    settings_text += f"├─ Groups: {'✅' if config.INCLUDE_WHATSAPP_GROUPS else '❌'} Enabled\n"
    settings_text += f"└─ Contacts: {'✅' if config.INCLUDE_WHATSAPP_CONTACTS else '❌'} Disabled\n\n"
    
    # Telegram settings
    settings_text += "📱 <b>Telegram</b>\n"
    settings_text += f"├─ Personal Accounts: {'❌' if config.EXCLUDE_PERSONAL_ACCOUNTS else '✅'} Excluded\n"
    settings_text += f"├─ Bots: {'❌' if config.EXCLUDE_BOTS else '✅'} Excluded\n"
    settings_text += f"└─ Duplicates: {'❌' if config.EXCLUDE_DUPLICATES else '✅'} Excluded\n\n"
    
    settings_text += "📊 <b>Scan Defaults</b>\n"
    settings_text += f"└─ Max Messages: {config.MAX_MESSAGES_PER_SCAN}\n"
    
    # Build settings keyboard
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="💬 Toggle WhatsApp Groups", callback_data="settings:toggle_whatsapp_groups"))
    builder.add(InlineKeyboardButton(text="👤 Toggle Personal Accounts", callback_data="settings:toggle_personal"))
    builder.add(InlineKeyboardButton(text="🤖 Toggle Bots", callback_data="settings:toggle_bots"))
    builder.add(InlineKeyboardButton(text="🔄 Toggle Duplicates", callback_data="settings:toggle_duplicates"))
    builder.add(InlineKeyboardButton(text="⬅️ Back to Menu", callback_data="menu:back"))
    builder.adjust(1)
    
    await callback.message.edit_text(
        settings_text,
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "settings:toggle_whatsapp_groups")
async def toggle_whatsapp_groups(callback: CallbackQuery):
    """Toggle WhatsApp groups setting."""
    await callback.answer()
    
    # Toggle setting
    config.INCLUDE_WHATSAPP_GROUPS = not config.INCLUDE_WHATSAPP_GROUPS
    status = "✅ Enabled" if config.INCLUDE_WHATSAPP_GROUPS else "❌ Disabled"
    
    await callback.message.edit_text(
        f"💬 WhatsApp Groups: {status}\n\n"
        "Setting updated successfully.",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="⬅️ Back to Settings", callback_data="menu:settings")]
            ]
        ),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "settings:toggle_personal")
async def toggle_personal_accounts(callback: CallbackQuery):
    """Toggle personal accounts setting."""
    await callback.answer()
    
    # Toggle setting
    config.EXCLUDE_PERSONAL_ACCOUNTS = not config.EXCLUDE_PERSONAL_ACCOUNTS
    status = "✅ Included" if not config.EXCLUDE_PERSONAL_ACCOUNTS else "❌ Excluded"
    
    await callback.message.edit_text(
        f"👤 Personal Accounts: {status}\n\n"
        "Setting updated successfully.",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="⬅️ Back to Settings", callback_data="menu:settings")]
            ]
        ),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "settings:toggle_bots")
async def toggle_bots(callback: CallbackQuery):
    """Toggle bots setting."""
    await callback.answer()
    
    # Toggle setting
    config.EXCLUDE_BOTS = not config.EXCLUDE_BOTS
    status = "✅ Included" if not config.EXCLUDE_BOTS else "❌ Excluded"
    
    await callback.message.edit_text(
        f"🤖 Bots: {status}\n\n"
        "Setting updated successfully.",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="⬅️ Back to Settings", callback_data="menu:settings")]
            ]
        ),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "settings:toggle_duplicates")
async def toggle_duplicates(callback: CallbackQuery):
    """Toggle duplicates setting."""
    await callback.answer()
    
    # Toggle setting
    config.EXCLUDE_DUPLICATES = not config.EXCLUDE_DUPLICATES
    status = "✅ Included" if not config.EXCLUDE_DUPLICATES else "❌ Excluded"
    
    await callback.message.edit_text(
        f"🔄 Duplicates: {status}\n\n"
        "Setting updated successfully.",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="⬅️ Back to Settings", callback_data="menu:settings")]
            ]
        ),
        parse_mode="HTML"
    )