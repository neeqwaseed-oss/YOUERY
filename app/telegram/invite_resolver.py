"""
Invite resolver module - resolves Telegram invite links.
"""

import re
from typing import Optional, Dict, Any, Tuple

from app.telegram.userbot_manager import UserbotManager
from app.telegram.entity_resolver import EntityResolver
from app.utils.logger import get_logger

logger = get_logger(__name__)


class InviteResolver:
    """
    Resolves Telegram invite links without joining.
    """
    
    def __init__(self, userbot_manager: UserbotManager):
        self.userbot = userbot_manager
        self.entity_resolver = EntityResolver(userbot_manager)
    
    @staticmethod
    def extract_invite_hash(url: str) -> Optional[str]:
        """
        Extract invite hash from URL.
        
        Args:
            url: Telegram invite URL
            
        Returns:
            Invite hash or None if not found
        """
        # Pattern for t.me/+hash
        plus_pattern = re.compile(r'^(?:https?://)?t\.me/(?:joinchat/)?\+([a-zA-Z0-9_\-]+)')
        # Pattern for t.me/joinchat/hash
        joinchat_pattern = re.compile(r'^(?:https?://)?t\.me/joinchat/([a-zA-Z0-9_\-]+)')
        
        match = plus_pattern.match(url)
        if match:
            return match.group(1)
        
        match = joinchat_pattern.match(url)
        if match:
            return match.group(1)
        
        return None
    
    async def resolve_invite(self, url: str) -> Dict[str, Any]:
        """
        Resolve an invite link.
        
        Args:
            url: Invite URL
            
        Returns:
            Resolution result
        """
        # Extract hash
        invite_hash = self.extract_invite_hash(url)
        
        if not invite_hash:
            return {
                'status': 'invalid',
                'link_type': 'private_invite',
                'error': 'Invalid invite URL format'
            }
        
        # Resolve using entity resolver
        result = await self.entity_resolver.resolve_invite_hash(invite_hash)
        
        # Add the URL
        result['url'] = url
        result['invite_hash'] = invite_hash
        
        return result
    
    async def resolve_invite_safe(self, url: str) -> Dict[str, Any]:
        """
        Safe resolve invite link - doesn't fail on errors.
        
        Args:
            url: Invite URL
            
        Returns:
            Resolution result (always returns a dict)
        """
        try:
            return await self.resolve_invite(url)
        except Exception as e:
            logger.error(f"Failed to resolve invite {url}: {e}")
            return {
                'status': 'error',
                'link_type': 'private_invite',
                'error': str(e),
                'url': url
            }