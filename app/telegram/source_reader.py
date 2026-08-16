"""
Source reader module - reads sources (channels/groups) the userbot can access.
"""

from typing import List, Dict, Any, Optional

from app.telegram.userbot_manager import UserbotManager
from app.utils.logger import get_logger

logger = get_logger(__name__)


class SourceReader:
    """
    Reads and manages sources (channels/groups) the userbot can access.
    """
    
    def __init__(self, userbot_manager: UserbotManager):
        self.userbot = userbot_manager
    
    async def get_accessible_sources(self) -> List[Dict[str, Any]]:
        """
        Get all sources the userbot can access.
        
        Returns:
            List of source dictionaries
        """
        if not self.userbot.is_initialized:
            logger.error("Userbot not initialized")
            return []
        
        try:
            dialogs = await self.userbot.get_dialogs()
            
            # Filter to only groups, supergroups, and channels
            sources = []
            for dialog in dialogs:
                if dialog['type'] in ['group', 'supergroup', 'channel']:
                    sources.append({
                        'id': dialog['id'],
                        'title': dialog['title'] or f"Chat {dialog['id']}",
                        'username': dialog['username'],
                        'type': dialog['type'],
                        'is_active': True
                    })
            
            logger.info(f"Found {len(sources)} accessible sources")
            return sources
            
        except Exception as e:
            logger.error(f"Failed to get accessible sources: {e}")
            return []
    
    async def get_source_by_id(self, source_id: int) -> Optional[Dict[str, Any]]:
        """
        Get source information by ID.
        
        Args:
            source_id: Telegram chat ID
            
        Returns:
            Source dictionary or None if not found
        """
        if not self.userbot.is_initialized:
            logger.error("Userbot not initialized")
            return None
        
        try:
            entity = await self.userbot.get_entity_by_id(source_id)
            if entity:
                return {
                    'id': entity['id'],
                    'title': entity.get('title') or f"Chat {entity['id']}",
                    'username': entity.get('username'),
                    'type': entity['type'],
                    'is_active': True
                }
            return None
            
        except Exception as e:
            logger.error(f"Failed to get source by ID {source_id}: {e}")
            return None
    
    async def refresh_sources(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Refresh sources for a user.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Updated list of sources
        """
        sources = await self.get_accessible_sources()
        # This will be used with database in Phase 4
        return sources