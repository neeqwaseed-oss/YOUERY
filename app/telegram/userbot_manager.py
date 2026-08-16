"""
Userbot manager module - manages Telethon client for userbot operations.
"""

import asyncio
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any

from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.tl.types import Channel, Chat, User
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty

from app.config import config
from app.utils.logger import get_logger

logger = get_logger(__name__)


class UserbotManager:
    """
    Manages Telethon client for userbot operations.
    """
    
    def __init__(self):
        self.client: Optional[TelegramClient] = None
        self.is_initialized = False
        self.session_path = config.SESSION_DIR / f"{config.SESSION_NAME}.session"
        
    async def initialize(self) -> bool:
        """
        Initialize and start the userbot client.
        
        Returns:
            True if initialized successfully, False otherwise
        """
        try:
            if self.is_initialized:
                return True
            
            # Create session directory if it doesn't exist
            self.session_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create client
            self.client = TelegramClient(
                str(self.session_path),
                config.API_ID,
                config.API_HASH,
                system_version="4.16.30-vxCUSTOM"
            )
            
            # Start client
            await self.client.start()
            
            # Get user info to verify connection
            me = await self.client.get_me()
            logger.info(f"Userbot connected as {me.first_name} (ID: {me.id})")
            
            self.is_initialized = True
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize userbot: {e}")
            self.is_initialized = False
            return False
    
    async def disconnect(self):
        """Disconnect the userbot client."""
        if self.client and self.is_initialized:
            try:
                await self.client.disconnect()
                logger.info("Userbot disconnected")
            except Exception as e:
                logger.error(f"Error disconnecting userbot: {e}")
            finally:
                self.is_initialized = False
                self.client = None
    
    async def get_dialogs(self) -> List[Dict[str, Any]]:
        """
        Get list of dialogs (chats/groups/channels) the userbot can access.
        
        Returns:
            List of dialog dictionaries with metadata
        """
        if not self.is_initialized:
            raise ValueError("Userbot not initialized")
        
        try:
            dialogs = await self.client(GetDialogsRequest(
                offset_id=0,
                offset_date=None,
                offset_peer=InputPeerEmpty(),
                limit=100,
                hash=0
            ))
            
            result = []
            for dialog in dialogs.dialogs:
                entity = dialog.peer
                # Get full entity info
                try:
                    full_entity = await self.client.get_entity(entity)
                    
                    dialog_info = {
                        'id': full_entity.id,
                        'title': getattr(full_entity, 'title', None),
                        'username': getattr(full_entity, 'username', None),
                        'type': self._get_entity_type(full_entity),
                        'is_active': True,
                        'dialog': dialog
                    }
                    result.append(dialog_info)
                except Exception as e:
                    logger.warning(f"Failed to get entity info for {entity}: {e}")
                    continue
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to get dialogs: {e}")
            return []
    
    @staticmethod
    def _get_entity_type(entity) -> str:
        """
        Determine the type of Telegram entity.
        
        Args:
            entity: Telethon entity object
            
        Returns:
            Entity type string
        """
        if isinstance(entity, User):
            return 'user'
        elif isinstance(entity, Channel):
            if hasattr(entity, 'megagroup') and entity.megagroup:
                return 'supergroup'
            return 'channel'
        elif isinstance(entity, Chat):
            return 'group'
        return 'unknown'
    
    async def get_entity_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Get entity information by username.
        
        Args:
            username: Telegram username (with or without @)
            
        Returns:
            Entity information dictionary or None if not found
        """
        if not self.is_initialized:
            raise ValueError("Userbot not initialized")
        
        # Remove @ if present
        username = username.lstrip('@')
        
        try:
            entity = await self.client.get_entity(username)
            return {
                'id': entity.id,
                'username': getattr(entity, 'username', None),
                'title': getattr(entity, 'title', None),
                'type': self._get_entity_type(entity),
                'is_bot': getattr(entity, 'bot', False) if isinstance(entity, User) else False,
                'is_verified': getattr(entity, 'verified', False) if isinstance(entity, User) else False,
                'entity': entity
            }
        except Exception as e:
            logger.warning(f"Failed to get entity by username {username}: {e}")
            return None
    
    async def get_entity_by_id(self, entity_id: int) -> Optional[Dict[str, Any]]:
        """
        Get entity information by ID.
        
        Args:
            entity_id: Telegram entity ID
            
        Returns:
            Entity information dictionary or None if not found
        """
        if not self.is_initialized:
            raise ValueError("Userbot not initialized")
        
        try:
            entity = await self.client.get_entity(entity_id)
            return {
                'id': entity.id,
                'username': getattr(entity, 'username', None),
                'title': getattr(entity, 'title', None),
                'type': self._get_entity_type(entity),
                'is_bot': getattr(entity, 'bot', False) if isinstance(entity, User) else False,
                'is_verified': getattr(entity, 'verified', False) if isinstance(entity, User) else False,
                'entity': entity
            }
        except Exception as e:
            logger.warning(f"Failed to get entity by ID {entity_id}: {e}")
            return None
    
    async def resolve_invite_link(self, invite_hash: str) -> Optional[Dict[str, Any]]:
        """
        Get information about an invite link without joining.
        
        Args:
            invite_hash: Invite hash (from t.me/+hash or t.me/joinchat/hash)
            
        Returns:
            Invite information dictionary or None if invalid/expired
        """
        if not self.is_initialized:
            raise ValueError("Userbot not initialized")
        
        try:
            # Try to get invite info using Telethon's built-in method
            # This doesn't join, just gets information
            from telethon.tl.functions.messages import CheckChatInviteRequest
            
            result = await self.client(CheckChatInviteRequest(invite_hash))
            
            if result:
                return {
                    'is_valid': True,
                    'title': getattr(result, 'title', None),
                    'is_channel': getattr(result, 'channel', False),
                    'is_megagroup': getattr(result, 'megagroup', False),
                    'is_public': getattr(result, 'public', False),
                    'participants_count': getattr(result, 'participants_count', 0),
                    'invite_hash': invite_hash
                }
            return None
            
        except Exception as e:
            # This is expected for expired/invalid invites
            logger.debug(f"Invite link {invite_hash} is invalid or expired: {e}")
            return None
    async def initialize(self) -> bool:
    """
    Initialize and start the userbot client.
    
    Returns:
        True if initialized successfully, False otherwise
    """
    try:
        if self.is_initialized:
            return True
        
        # Create session directory if it doesn't exist
        self.session_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Check if session file exists and is valid
        if self.session_path.exists():
            try:
                # Try to load existing session
                self.client = TelegramClient(
                    str(self.session_path),
                    config.API_ID,
                    config.API_HASH,
                    system_version="4.16.30-vxCUSTOM"
                )
                await self.client.connect()
                if await self.client.is_user_authorized():
                    me = await self.client.get_me()
                    logger.info(f"Userbot reconnected as {me.first_name} (ID: {me.id})")
                    self.is_initialized = True
                    return True
            except Exception as e:
                logger.warning(f"Failed to load existing session: {e}")
                # Continue with new session creation
        
        # Create new client
        self.client = TelegramClient(
            str(self.session_path),
            config.API_ID,
            config.API_HASH,
            system_version="4.16.30-vxCUSTOM"
        )
        
        # Start client
        await self.client.start()
        
        # Get user info to verify connection
        me = await self.client.get_me()
        logger.info(f"Userbot connected as {me.first_name} (ID: {me.id})")
        
        self.is_initialized = True
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize userbot: {e}")
        self.is_initialized = False
        return False