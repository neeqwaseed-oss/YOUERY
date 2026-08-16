"""
Source repository module.
"""

from typing import List, Optional
from datetime import datetime

from app.database.database import get_database
from app.database.models import Source
from app.utils.logger import get_logger

logger = get_logger(__name__)


class SourceRepository:
    """Repository for source operations."""
    
    async def create(
        self,
        telegram_user_id: int,
        telegram_chat_id: int,
        title: Optional[str] = None,
        username: Optional[str] = None,
        source_type: str = 'group'
    ) -> Source:
        """
        Create a new source.
        
        Args:
            telegram_user_id: User ID
            telegram_chat_id: Telegram chat ID
            title: Source title
            username: Source username
            source_type: Source type (group, supergroup, channel)
            
        Returns:
            Source object
        """
        db = await get_database()
        now = datetime.now().isoformat()
        
        async with db.get_cursor() as cursor:
            cursor.execute("""
                INSERT OR IGNORE INTO sources 
                (telegram_user_id, telegram_chat_id, title, username, source_type, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (telegram_user_id, telegram_chat_id, title, username, source_type, now, now))
            
            # Get the source (either newly created or existing)
            cursor.execute(
                "SELECT * FROM sources WHERE telegram_user_id = ? AND telegram_chat_id = ?",
                (telegram_user_id, telegram_chat_id)
            )
            row = cursor.fetchone()
            
            if row:
                return Source(
                    id=row[0],
                    telegram_user_id=row[1],
                    telegram_chat_id=row[2],
                    title=row[3],
                    username=row[4],
                    source_type=row[5],
                    is_active=bool(row[6]),
                    created_at=row[7],
                    updated_at=row[8]
                )
            raise ValueError("Failed to create or retrieve source")
    
    async def get_by_id(self, source_id: int) -> Optional[Source]:
        """
        Get source by ID.
        
        Args:
            source_id: Source ID
            
        Returns:
            Source object or None
        """
        db = await get_database()
        
        async with db.get_cursor() as cursor:
            cursor.execute(
                "SELECT * FROM sources WHERE id = ?",
                (source_id,)
            )
            row = cursor.fetchone()
            
            if row:
                return Source(
                    id=row[0],
                    telegram_user_id=row[1],
                    telegram_chat_id=row[2],
                    title=row[3],
                    username=row[4],
                    source_type=row[5],
                    is_active=bool(row[6]),
                    created_at=row[7],
                    updated_at=row[8]
                )
            return None
    
    async def get_by_user(self, telegram_user_id: int) -> List[Source]:
        """
        Get all sources for a user.
        
        Args:
            telegram_user_id: User ID
            
        Returns:
            List of Source objects
        """
        db = await get_database()
        sources = []
        
        async with db.get_cursor() as cursor:
            cursor.execute(
                "SELECT * FROM sources WHERE telegram_user_id = ? AND is_active = 1",
                (telegram_user_id,)
            )
            rows = cursor.fetchall()
            
            for row in rows:
                sources.append(Source(
                    id=row[0],
                    telegram_user_id=row[1],
                    telegram_chat_id=row[2],
                    title=row[3],
                    username=row[4],
                    source_type=row[5],
                    is_active=bool(row[6]),
                    created_at=row[7],
                    updated_at=row[8]
                ))
        
        return sources
    
    async def update_activity(self, source_id: int, is_active: bool) -> bool:
        """
        Update source active status.
        
        Args:
            source_id: Source ID
            is_active: Active status
            
        Returns:
            True if updated successfully
        """
        db = await get_database()
        now = datetime.now().isoformat()
        
        async with db.get_cursor() as cursor:
            cursor.execute("""
                UPDATE sources 
                SET is_active = ?, updated_at = ?
                WHERE id = ?
            """, (1 if is_active else 0, now, source_id))
            
            return cursor.rowcount > 0