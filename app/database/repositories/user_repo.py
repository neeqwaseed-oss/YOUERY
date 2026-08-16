"""
User repository module.
"""

from typing import Optional
from datetime import datetime

from app.database.database import get_database
from app.database.models import User
from app.utils.logger import get_logger

logger = get_logger(__name__)


class UserRepository:
    """Repository for user operations."""
    
    async def create_or_update(
        self,
        telegram_user_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None
    ) -> User:
        """
        Create or update a user.
        
        Args:
            telegram_user_id: Telegram user ID
            username: Username
            first_name: First name
            
        Returns:
            User object
        """
        db = await get_database()
        now = datetime.now().isoformat()
        
        async with db.get_cursor() as cursor:
            # Check if user exists
            cursor.execute(
                "SELECT * FROM users WHERE telegram_user_id = ?",
                (telegram_user_id,)
            )
            row = cursor.fetchone()
            
            if row:
                # Update existing user
                cursor.execute("""
                    UPDATE users 
                    SET username = ?, first_name = ?, updated_at = ?
                    WHERE telegram_user_id = ?
                """, (username, first_name, now, telegram_user_id))
                
                return User(
                    id=row[0],
                    telegram_user_id=row[1],
                    username=username or row[2],
                    first_name=first_name or row[3],
                    created_at=row[4],
                    updated_at=now
                )
            else:
                # Create new user
                cursor.execute("""
                    INSERT INTO users (telegram_user_id, username, first_name, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (telegram_user_id, username, first_name, now, now))
                
                return User(
                    id=cursor.lastrowid,
                    telegram_user_id=telegram_user_id,
                    username=username,
                    first_name=first_name,
                    created_at=now,
                    updated_at=now
                )
    
    async def get_by_telegram_id(self, telegram_user_id: int) -> Optional[User]:
        """
        Get user by Telegram ID.
        
        Args:
            telegram_user_id: Telegram user ID
            
        Returns:
            User object or None
        """
        db = await get_database()
        
        async with db.get_cursor() as cursor:
            cursor.execute(
                "SELECT * FROM users WHERE telegram_user_id = ?",
                (telegram_user_id,)
            )
            row = cursor.fetchone()
            
            if row:
                return User(
                    id=row[0],
                    telegram_user_id=row[1],
                    username=row[2],
                    first_name=row[3],
                    created_at=row[4],
                    updated_at=row[5]
                )
            return None