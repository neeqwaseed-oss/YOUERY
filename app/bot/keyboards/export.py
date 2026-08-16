"""
Export keyboards - keyboard builders for export operations.
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_export_menu_keyboard() -> InlineKeyboardMarkup:
    """
    Get export menu keyboard.
    
    Returns:
        InlineKeyboardMarkup with export options
    """
    builder = InlineKeyboardBuilder()
    
    builder.add(InlineKeyboardButton(text="📄 TXT", callback_data="export:txt"))
    builder.add(InlineKeyboardButton(text="📊 CSV", callback_data="export:csv"))
    builder.add(InlineKeyboardButton(text="📝 JSON", callback_data="export:json"))
    builder.add(InlineKeyboardButton(text="📊 XLSX", callback_data="export:xlsx"))
    builder.add(InlineKeyboardButton(text="⬅️ Back to Menu", callback_data="menu:back"))
    builder.adjust(1)
    
    return builder.as_markup()