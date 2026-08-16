"""
Telegram URL parser module - parses and classifies Telegram URLs.
"""

import re
from dataclasses import dataclass
from typing import Optional, Dict, Any

from app.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class TelegramParseResult:
    """Result of parsing a Telegram URL."""
    url: str
    normalized_url: str
    entity_type: str  # user, channel, group, invite
    entity_id: Optional[str] = None
    username: Optional[str] = None
    invite_hash: Optional[str] = None
    is_invite: bool = False
    is_private: bool = False
    is_valid: bool = True
    error: Optional[str] = None


class TelegramParser:
    """
    Parser for Telegram URLs.
    Detects and extracts information from various Telegram URL formats.
    """
    
    # URL patterns
    USERNAME_PATTERN = re.compile(r'^(?:https?://)?(?:t\.me|telegram\.me)/([a-zA-Z0-9_]+)(?:[/?#].*)?$')
    INVITE_HASH_PATTERN = re.compile(r'^(?:https?://)?(?:t\.me|telegram\.me)/(?:joinchat/|\+)([a-zA-Z0-9_\-]+)(?:[/?#].*)?$')
    MESSAGE_PATTERN = re.compile(r'^(?:https?://)?(?:t\.me|telegram\.me)/([a-zA-Z0-9_]+)/(\d+)(?:[/?#].*)?$')
    
    # Entity type constants
    TYPE_USER = 'user'
    TYPE_CHANNEL = 'channel'
    TYPE_GROUP = 'group'
    TYPE_INVITE = 'invite'
    TYPE_MESSAGE = 'message'
    TYPE_UNKNOWN = 'unknown'
    
    @classmethod
    def parse(cls, url: str) -> TelegramParseResult:
        """
        Parse a Telegram URL and extract information.
        
        Args:
            url: The URL to parse
            
        Returns:
            TelegramParseResult with parsed information
        """
        url = url.strip()
        normalized_url = cls.normalize(url)
        
        # Check if it's an invite link
        invite_match = cls.INVITE_HASH_PATTERN.match(url)
        if invite_match:
            hash_value = invite_match.group(1)
            return TelegramParseResult(
                url=url,
                normalized_url=normalized_url,
                entity_type=cls.TYPE_INVITE,
                invite_hash=hash_value,
                is_invite=True,
                is_private=True
            )
        
        # Check if it's a message link
        message_match = cls.MESSAGE_PATTERN.match(url)
        if message_match:
            username = message_match.group(1)
            message_id = message_match.group(2)
            return TelegramParseResult(
                url=url,
                normalized_url=normalized_url,
                entity_type=cls.TYPE_MESSAGE,
                username=username,
                entity_id=message_id,
                is_private=False
            )
        
        # Check if it's a username link
        username_match = cls.USERNAME_PATTERN.match(url)
        if username_match:
            username = username_match.group(1)
            
            # Determine likely entity type based on username conventions
            if username.lower().startswith('@'):
                username = username[1:]
            
            # Check if it's likely a bot
            if username.lower().endswith('bot'):
                return TelegramParseResult(
                    url=url,
                    normalized_url=normalized_url,
                    entity_type=cls.TYPE_USER,
                    username=username,
                    entity_id=username,
                    is_private=True
                )
            
            # Default to channel/group
            return TelegramParseResult(
                url=url,
                normalized_url=normalized_url,
                entity_type=cls.TYPE_CHANNEL,
                username=username,
                entity_id=username,
                is_private=False
            )
        
        return TelegramParseResult(
            url=url,
            normalized_url=normalized_url,
            entity_type=cls.TYPE_UNKNOWN,
            is_valid=False,
            error="Unknown Telegram URL format"
        )
    
    @classmethod
    def normalize(cls, url: str) -> str:
        """
        Normalize a Telegram URL to a canonical form.
        
        Args:
            url: The URL to normalize
            
        Returns:
            Normalized URL string
        """
        url = url.strip()
        
        # Remove trailing slash
        if url.endswith('/'):
            url = url[:-1]
        
        # Remove query parameters and fragments
        if '?' in url:
            url = url.split('?')[0]
        if '#' in url:
            url = url.split('#')[0]
        
        # Normalize scheme
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Normalize domain
        url = url.replace('http://t.me/', 'https://t.me/')
        url = url.replace('https://telegram.me/', 'https://t.me/')
        url = url.replace('http://telegram.me/', 'https://t.me/')
        
        return url
    
    @classmethod
    def classify(cls, url: str) -> Dict[str, Any]:
        """
        Classify a Telegram URL.
        
        Args:
            url: The URL to classify
            
        Returns:
            Dictionary with classification information
        """
        result = cls.parse(url)
        
        classification = {
            'platform': 'telegram',
            'url': url,
            'normalized_url': result.normalized_url,
            'entity_type': result.entity_type,
            'is_valid': result.is_valid,
        }
        
        if result.entity_type == cls.TYPE_INVITE:
            classification['link_type'] = 'private_invite'
            classification['status'] = 'valid'
            classification['invite_hash'] = result.invite_hash
        elif result.entity_type == cls.TYPE_USER:
            classification['link_type'] = 'personal_account'
            classification['status'] = 'excluded'
            classification['username'] = result.username
        elif result.entity_type in [cls.TYPE_CHANNEL, cls.TYPE_GROUP]:
            classification['link_type'] = 'public_group' if result.entity_type == cls.TYPE_GROUP else 'public_channel'
            classification['status'] = 'valid'
            classification['username'] = result.username
        elif result.entity_type == cls.TYPE_MESSAGE:
            classification['link_type'] = 'message'
            classification['status'] = 'valid'
            classification['username'] = result.username
            classification['message_id'] = result.entity_id
        else:
            classification['link_type'] = 'unknown'
            classification['status'] = 'invalid'
        
        return classification
    
    @classmethod
    def is_valid_telegram_url(cls, url: str) -> bool:
        """
        Check if a URL is a valid Telegram URL.
        
        Args:
            url: The URL to check
            
        Returns:
            True if valid Telegram URL, False otherwise
        """
        patterns = [
            cls.USERNAME_PATTERN,
            cls.INVITE_HASH_PATTERN,
            cls.MESSAGE_PATTERN
        ]
        
        for pattern in patterns:
            if pattern.match(url):
                return True
        
        return False