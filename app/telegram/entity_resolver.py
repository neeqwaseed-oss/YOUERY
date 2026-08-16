"""
Entity resolver module - resolves Telegram entities and classifies them.
"""

from typing import Dict, Any, Optional, Tuple

from app.telegram.userbot_manager import UserbotManager
from app.utils.logger import get_logger
from app.utils.retry import retry_async

logger = get_logger(__name__)


class EntityResolver:
    """
    Resolves Telegram entities and determines their type.
    """
    
    # Entity type constants
    TYPE_USER = 'personal_account'
    TYPE_BOT = 'bot'
    TYPE_GROUP = 'public_group'
    TYPE_CHANNEL = 'public_channel'
    TYPE_INVITE = 'private_invite'
    TYPE_UNKNOWN = 'unknown'
    
    def __init__(self, userbot_manager: UserbotManager):
        self.userbot = userbot_manager
    
    @retry_async(max_retries=3, delay=5, backoff=2)
    async def resolve_by_username(self, username: str) -> Dict[str, Any]:
        """
        Resolve entity by username.
        
        Args:
            username: Telegram username (with or without @)
            
        Returns:
            Entity resolution result
        """
        if not self.userbot.is_initialized:
            raise ValueError("Userbot not initialized")
        
        # Remove @ if present
        username = username.lstrip('@')
        
        try:
            entity_info = await self.userbot.get_entity_by_username(username)
            
            if not entity_info:
                return {
                    'status': 'invalid',
                    'link_type': self.TYPE_UNKNOWN,
                    'error': 'Entity not found'
                }
            
            # Classify entity
            return await self._classify_entity(entity_info)
            
        except Exception as e:
            logger.error(f"Failed to resolve entity by username {username}: {e}")
            return {
                'status': 'error',
                'link_type': self.TYPE_UNKNOWN,
                'error': str(e)
            }
    
    @retry_async(max_retries=3, delay=5, backoff=2)
    async def resolve_by_id(self, entity_id: int) -> Dict[str, Any]:
        """
        Resolve entity by ID.
        
        Args:
            entity_id: Telegram entity ID
            
        Returns:
            Entity resolution result
        """
        if not self.userbot.is_initialized:
            raise ValueError("Userbot not initialized")
        
        try:
            entity_info = await self.userbot.get_entity_by_id(entity_id)
            
            if not entity_info:
                return {
                    'status': 'invalid',
                    'link_type': self.TYPE_UNKNOWN,
                    'error': 'Entity not found'
                }
            
            # Classify entity
            return await self._classify_entity(entity_info)
            
        except Exception as e:
            logger.error(f"Failed to resolve entity by ID {entity_id}: {e}")
            return {
                'status': 'error',
                'link_type': self.TYPE_UNKNOWN,
                'error': str(e)
            }
    
    async def _classify_entity(self, entity_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classify a resolved entity.
        
        Args:
            entity_info: Entity information dictionary
            
        Returns:
            Classification result
        """
        entity_type = entity_info.get('type', 'unknown')
        is_bot = entity_info.get('is_bot', False)
        
        result = {
            'status': 'valid',
            'entity_id': entity_info.get('id'),
            'entity_title': entity_info.get('title'),
            'entity_username': entity_info.get('username'),
            'is_bot': is_bot
        }
        
        if entity_type == 'user':
            if is_bot:
                result['link_type'] = self.TYPE_BOT
                result['status'] = 'excluded'
            else:
                result['link_type'] = self.TYPE_USER
                result['status'] = 'excluded'
                
        elif entity_type == 'group':
            result['link_type'] = self.TYPE_GROUP
            result['status'] = 'valid'
            
        elif entity_type == 'supergroup':
            result['link_type'] = self.TYPE_GROUP
            result['status'] = 'valid'
            
        elif entity_type == 'channel':
            result['link_type'] = self.TYPE_CHANNEL
            result['status'] = 'valid'
            
        else:
            result['link_type'] = self.TYPE_UNKNOWN
            result['status'] = 'invalid'
        
        return result
    
    @retry_async(max_retries=2, delay=3, backoff=2)
    async def resolve_invite_hash(self, invite_hash: str) -> Dict[str, Any]:
        """
        Resolve an invite link hash.
        
        Args:
            invite_hash: Invite hash from t.me/+hash or t.me/joinchat/hash
            
        Returns:
            Invite resolution result
        """
        if not self.userbot.is_initialized:
            raise ValueError("Userbot not initialized")
        
        try:
            invite_info = await self.userbot.resolve_invite_link(invite_hash)
            
            if invite_info and invite_info.get('is_valid'):
                return {
                    'status': 'valid',
                    'link_type': self.TYPE_INVITE,
                    'entity_title': invite_info.get('title'),
                    'is_channel': invite_info.get('is_channel'),
                    'is_megagroup': invite_info.get('is_megagroup'),
                    'invite_hash': invite_hash
                }
            else:
                return {
                    'status': 'invalid',
                    'link_type': self.TYPE_INVITE,
                    'error': 'Invalid or expired invite'
                }
                
        except Exception as e:
            logger.error(f"Failed to resolve invite hash {invite_hash}: {e}")
            return {
                'status': 'error',
                'link_type': self.TYPE_INVITE,
                'error': str(e)
            }