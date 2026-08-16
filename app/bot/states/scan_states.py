"""
FSM states for scan operations.
"""

from aiogram.fsm.state import State, StatesGroup


class ScanStates(StatesGroup):
    """States for the scan workflow."""
    
    select_source = State()
    select_mode = State()
    enter_limit = State()
    enter_start_message = State()
    enter_end_message = State()
    confirm_scan = State()
    scanning = State()