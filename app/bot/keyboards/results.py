"""
Results keyboards - keyboard builders for results navigation.
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_results_menu_keyboard() -> InlineKeyboardMarkup:
    """
    Get results menu keyboard.
    
    Returns:
        InlineKeyboardMarkup with results navigation
    """
    builder = InlineKeyboardBuilder()
    
    builder.add(InlineKeyboardButton(text="📱 Telegram", callback_data="result:telegram"))
    builder.add(InlineKeyboardButton(text="💬 WhatsApp", callback_data="result:whatsapp"))
    builder.add(InlineKeyboardButton(text="❌ Excluded", callback_data="result:excluded"))
    builder.add(InlineKeyboardButton(text="🔄 Duplicates", callback_data="result:duplicates"))
    builder.add(InlineKeyboardButton(text="⬅️ Back to Menu", callback_data="menu:back"))
    builder.adjust(1)
    
    return builder.as_markup()