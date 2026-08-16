"""
Main menu keyboards.
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """
    Get main menu keyboard with operation buttons.
    
    Returns:
        InlineKeyboardMarkup: Keyboard with main menu options
    """
    builder = InlineKeyboardBuilder()
    
    buttons = [
        InlineKeyboardButton(text="🔍 استخراج الروابط", callback_data="menu:scan"),
        InlineKeyboardButton(text="📂 المصادر", callback_data="menu:sources"),
        InlineKeyboardButton(text="📊 النتائج", callback_data="menu:results"),
        InlineKeyboardButton(text="📤 التصدير", callback_data="menu:exports"),
        InlineKeyboardButton(text="⚙️ الإعدادات", callback_data="menu:settings"),
    ]
    
    for button in buttons:
        builder.add(button)
    
    builder.adjust(1)  # One button per row
    return builder.as_markup()


def get_back_keyboard() -> InlineKeyboardMarkup:
    """
    Get back button keyboard.
    
    Returns:
        InlineKeyboardMarkup: Keyboard with back button
    """
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="⬅️ رجوع", callback_data="menu:back"))
    return builder.as_markup()