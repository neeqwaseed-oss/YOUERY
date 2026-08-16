"""
Scan keyboards - keyboard builders for scan operations.
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_scan_menu_keyboard() -> InlineKeyboardMarkup:
    """
    Get scan mode selection keyboard.
    
    Returns:
        InlineKeyboardMarkup with scan mode options
    """
    builder = InlineKeyboardBuilder()
    
    buttons = [
        InlineKeyboardButton(text="📨 Recent Messages", callback_data="scan:mode:recent"),
        InlineKeyboardButton(text="📊 Full Scan", callback_data="scan:mode:full"),
        InlineKeyboardButton(text="📐 Range Scan", callback_data="scan:mode:range"),
        InlineKeyboardButton(text="⬅️ Back", callback_data="menu:back"),
    ]
    
    for button in buttons:
        builder.add(button)
    
    builder.adjust(1)
    return builder.as_markup()


def get_scan_confirmation_keyboard() -> InlineKeyboardMarkup:
    """
    Get scan confirmation keyboard.
    
    Returns:
        InlineKeyboardMarkup with confirm/cancel buttons
    """
    builder = InlineKeyboardBuilder()
    
    builder.add(InlineKeyboardButton(text="🚀 Start Scan", callback_data="scan:confirm"))
    builder.add(InlineKeyboardButton(text="❌ Cancel", callback_data="scan:cancel"))
    builder.adjust(2)
    
    return builder.as_markup()


def get_scan_stop_keyboard(job_id: int) -> InlineKeyboardMarkup:
    """
    Get scan stop keyboard.
    
    Args:
        job_id: Scan job ID
        
    Returns:
        InlineKeyboardMarkup with stop button
    """
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🛑 Stop Scan", callback_data=f"scan:stop:{job_id}"))
    return builder.as_markup()