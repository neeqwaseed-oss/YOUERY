"""
Sources keyboards - keyboard builders for sources.
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_sources_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """
    Get sources selection keyboard.
    
    Args:
        user_id: Telegram user ID
        
    Returns:
        InlineKeyboardMarkup with source selection
    """
    builder = InlineKeyboardBuilder()
    
    # Note: This is a placeholder. The actual sources will be loaded dynamically
    # in the handlers based on the user's accessible sources.
    # The keyboard will be built in the scan handler with actual source data.
    
    builder.add(InlineKeyboardButton(text="🔄 Refresh Sources", callback_data="source:refresh"))
    builder.add(InlineKeyboardButton(text="⬅️ Back", callback_data="menu:back"))
    builder.adjust(1)
    
    return builder.as_markup()


def get_source_back_keyboard() -> InlineKeyboardMarkup:
    """
    Get source back navigation keyboard.
    
    Returns:
        InlineKeyboardMarkup with back button
    """
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🔄 Refresh", callback_data="source:refresh"))
    builder.add(InlineKeyboardButton(text="⬅️ Back to Menu", callback_data="menu:back"))
    builder.adjust(1)
    
    return builder.as_markup()