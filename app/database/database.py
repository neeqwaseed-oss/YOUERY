"""
Database module - handles SQLite database initialization and connections.
"""

import sqlite3
import asyncio
from pathlib import Path
from typing import Optional
from contextlib import asynccontextmanager

from app.config import config
from app.utils.logger import get_logger


logger = get_logger(__name__)


class Database:
    """Database connection manager for SQLite."""

    def __init__(self, db_path: str = None):
        self.db_path = db_path or config.DATABASE_PATH
        self._connection: Optional[sqlite3.Connection] = None
        self._lock = asyncio.Lock()

    async def initialize(self):
        """Initialize database and create tables."""
        logger.info(f"Initializing database at {self.db_path}")

        # Ensure directory exists
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        async with self._lock:
            # Create connection
            self._connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                timeout=30
            )

            # Enable foreign keys
            self._connection.execute("PRAGMA foreign_keys = ON")

            # Create tables
            await self._create_tables()

            logger.info("Database initialized successfully")

    async def _create_tables(self):
        """Create all database tables."""
        cursor = self._connection.cursor()

        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_user_id INTEGER NOT NULL UNIQUE,
                username TEXT,
                first_name TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        # Sources table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_user_id INTEGER NOT NULL,
                telegram_chat_id INTEGER NOT NULL,
                title TEXT,
                username TEXT,
                source_type TEXT NOT NULL,
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE(telegram_user_id, telegram_chat_id)
            )
        """)

        # Scan jobs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scan_jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_user_id INTEGER NOT NULL,
                source_id INTEGER NOT NULL,
                status TEXT NOT NULL,
                scan_mode TEXT NOT NULL,
                start_message_id INTEGER,
                end_message_id INTEGER,
                messages_scanned INTEGER NOT NULL DEFAULT 0,
                urls_found INTEGER NOT NULL DEFAULT 0,
                urls_unique INTEGER NOT NULL DEFAULT 0,
                completed_at TEXT,
                error_message TEXT,
                created_at TEXT NOT NULL,
                started_at TEXT
            )
        """)

        # Extracted links table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS extracted_links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_job_id INTEGER NOT NULL,
                source_id INTEGER NOT NULL,
                message_id INTEGER,
                original_url TEXT NOT NULL,
                normalized_url TEXT NOT NULL,
                platform TEXT NOT NULL,
                link_type TEXT NOT NULL,
                status TEXT NOT NULL,
                entity_id TEXT,
                entity_title TEXT,
                entity_username TEXT,
                created_at TEXT NOT NULL
            )
        """)

        # Unique links table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS unique_links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                normalized_url TEXT NOT NULL UNIQUE,
                platform TEXT NOT NULL,
                link_type TEXT NOT NULL,
                status TEXT NOT NULL,
                entity_id TEXT,
                entity_title TEXT,
                entity_username TEXT,
                first_seen_source_id INTEGER,
                first_seen_message_id INTEGER,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        # Scan statistics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scan_statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_job_id INTEGER NOT NULL UNIQUE,
                telegram_count INTEGER NOT NULL DEFAULT 0,
                whatsapp_count INTEGER NOT NULL DEFAULT 0,
                group_count INTEGER NOT NULL DEFAULT 0,
                channel_count INTEGER NOT NULL DEFAULT 0,
                invite_count INTEGER NOT NULL DEFAULT 0,
                personal_count INTEGER NOT NULL DEFAULT 0,
                bot_count INTEGER NOT NULL DEFAULT 0,
                duplicate_count INTEGER NOT NULL DEFAULT 0,
                other_count INTEGER NOT NULL DEFAULT 0,
                invalid_count INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            )
        """)

        self._connection.commit()
        logger.info("Tables created successfully")

    @asynccontextmanager
    async def get_cursor(self):
        """Get a cursor for database operations."""
        if not self._connection:
            await self.initialize()

        cursor = self._connection.cursor()

        try:
            yield cursor
            self._connection.commit()

        except Exception:
            self._connection.rollback()
            raise

        finally:
            cursor.close()

    async def execute(
        self,
        query: str,
        params: tuple = None
    ) -> sqlite3.Cursor:
        """Execute a query and return cursor."""
        if not self._connection:
            await self.initialize()

        cursor = self._connection.cursor()
        cursor.execute(query, params or ())
        return cursor

    async def close(self):
        """Close database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
            logger.info("Database connection closed")


# Global database instance
_db_instance: Optional[Database] = None


async def get_database() -> Database:
    """Get global database instance."""
    global _db_instance

    if not _db_instance:
        _db_instance = Database()
        await _db_instance.initialize()

    return _db_instance


async def init_database():
    """Initialize database."""
    await get_database()