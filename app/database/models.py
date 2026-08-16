"""
Database models module - defines data models.
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class User:
    """User model."""
    id: Optional[int] = None
    telegram_user_id: Optional[int] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@dataclass
class Source:
    """Source model."""
    id: Optional[int] = None
    telegram_user_id: Optional[int] = None
    telegram_chat_id: Optional[int] = None
    title: Optional[str] = None
    username: Optional[str] = None
    source_type: Optional[str] = None
    is_active: bool = True
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@dataclass
class ScanJob:
    """Scan job model."""
    id: Optional[int] = None
    telegram_user_id: Optional[int] = None
    source_id: Optional[int] = None
    status: str = 'queued'
    scan_mode: str = 'recent'
    start_message_id: Optional[int] = None
    end_message_id: Optional[int] = None
    messages_scanned: int = 0
    urls_found: int = 0
    urls_unique: int = 0
    completed_at: Optional[str] = None
    error_message: Optional[str] = None
    created_at: Optional[str] = None
    started_at: Optional[str] = None


@dataclass
class ExtractedLink:
    """Extracted link model."""
    id: Optional[int] = None
    scan_job_id: Optional[int] = None
    source_id: Optional[int] = None
    message_id: Optional[int] = None
    original_url: Optional[str] = None
    normalized_url: Optional[str] = None
    platform: str = 'other'
    link_type: str = 'unknown'
    status: str = 'pending'
    entity_id: Optional[str] = None
    entity_title: Optional[str] = None
    entity_username: Optional[str] = None
    created_at: Optional[str] = None


@dataclass
class UniqueLink:
    """Unique link model."""
    id: Optional[int] = None
    normalized_url: Optional[str] = None
    platform: str = 'other'
    link_type: str = 'unknown'
    status: str = 'pending'
    entity_id: Optional[str] = None
    entity_title: Optional[str] = None
    entity_username: Optional[str] = None
    first_seen_source_id: Optional[int] = None
    first_seen_message_id: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@dataclass
class ScanStatistics:
    """Scan statistics model."""
    id: Optional[int] = None
    scan_job_id: Optional[int] = None
    telegram_count: int = 0
    whatsapp_count: int = 0
    group_count: int = 0
    channel_count: int = 0
    invite_count: int = 0
    personal_count: int = 0
    bot_count: int = 0
    duplicate_count: int = 0
    other_count: int = 0
    invalid_count: int = 0
    created_at: Optional[str] = None