"""
WhatsApp URL parser module - parses and classifies WhatsApp URLs.
"""

import re
from dataclasses import dataclass
from typing import Optional, Dict, Any

from app.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class WhatsAppParseResult:
    """Result of parsing a WhatsApp URL."""
    url: str
    normalized_url: str
    entity_type: str  # group, contact
    group_id: Optional[str] = None
    phone_number: Optional[str] = None
    is_valid: bool = True
    error: Optional[str] = None


class WhatsAppParser:
    """
    Parser for WhatsApp URLs.
    Detects and extracts information from various WhatsApp URL formats.
    """
    
    # URL patterns
    GROUP_PATTERN = re.compile(r'^(?:https?://)?chat\.whatsapp\.com/([a-zA-Z0-9_\-]+)(?:[/?#].*)?$')
    CONTACT_PATTERN = re.compile(r'^(?:https?://)?wa\.me/([0-9\+]+)(?:[/?#].*)?$')
    API_CONTACT_PATTERN = re.compile(r'^(?:https?://)?api\.whatsapp\.com/send\?phone=([0-9\+]+)(?:&.*)?$')
    
    # Entity type constants
    TYPE_GROUP = 'group'
    TYPE_CONTACT = 'contact'
    TYPE_UNKNOWN = 'unknown'
    
    @classmethod
    def parse(cls, url: str) -> WhatsAppParseResult:
        """
        Parse a WhatsApp URL and extract information.
        
        Args:
            url: The URL to parse
            
        Returns:
            WhatsAppParseResult with parsed information
        """
        url = url.strip()
        normalized_url = cls.normalize(url)
        
        # Check if it's a group invite link
        group_match = cls.GROUP_PATTERN.match(url)
        if group_match:
            group_id = group_match.group(1)
            return WhatsAppParseResult(
                url=url,
                normalized_url=normalized_url,
                entity_type=cls.TYPE_GROUP,
                group_id=group_id,
                is_valid=True
            )
        
        # Check if it's a contact link (wa.me)
        contact_match = cls.CONTACT_PATTERN.match(url)
        if contact_match:
            phone_number = contact_match.group(1)
            return WhatsAppParseResult(
                url=url,
                normalized_url=normalized_url,
                entity_type=cls.TYPE_CONTACT,
                phone_number=phone_number,
                is_valid=True
            )
        
        # Check if it's an API contact link
        api_match = cls.API_CONTACT_PATTERN.match(url)
        if api_match:
            phone_number = api_match.group(1)
            return WhatsAppParseResult(
                url=url,
                normalized_url=normalized_url,
                entity_type=cls.TYPE_CONTACT,
                phone_number=phone_number,
                is_valid=True
            )
        
        return WhatsAppParseResult(
            url=url,
            normalized_url=normalized_url,
            entity_type=cls.TYPE_UNKNOWN,
            is_valid=False,
            error="Unknown WhatsApp URL format"
        )
    
    @classmethod
    def normalize(cls, url: str) -> str:
        """
        Normalize a WhatsApp URL to a canonical form.
        
        Args:
            url: The URL to normalize
            
        Returns:
            Normalized URL string
        """
        url = url.strip()
        
        # Remove trailing slash
        if url.endswith('/'):
            url = url[:-1]
        
        # Remove query parameters and fragments (except for API calls)
        if '?' in url and not url.startswith(('https://api.whatsapp.com/send?', 'http://api.whatsapp.com/send?')):
            url = url.split('?')[0]
        if '#' in url:
            url = url.split('#')[0]
        
        # Normalize scheme
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        return url
    
    @classmethod
    def classify(cls, url: str) -> Dict[str, Any]:
        """
        Classify a WhatsApp URL.
        
        Args:
            url: The URL to classify
            
        Returns:
            Dictionary with classification information
        """
        result = cls.parse(url)
        
        classification = {
            'platform': 'whatsapp',
            'url': url,
            'normalized_url': result.normalized_url,
            'entity_type': result.entity_type,
            'is_valid': result.is_valid,
        }
        
        if result.entity_type == cls.TYPE_GROUP:
            classification['link_type'] = 'group'
            classification['status'] = 'valid'
            classification['group_id'] = result.group_id
        elif result.entity_type == cls.TYPE_CONTACT:
            classification['link_type'] = 'contact'
            classification['status'] = 'valid'
            classification['phone_number'] = result.phone_number
        else:
            classification['link_type'] = 'unknown'
            classification['status'] = 'invalid'
        
        return classification
    
    @classmethod
    def is_valid_whatsapp_url(cls, url: str) -> bool:
        """
        Check if a URL is a valid WhatsApp URL.
        
        Args:
            url: The URL to check
            
        Returns:
            True if valid WhatsApp URL, False otherwise
        """
        patterns = [
            cls.GROUP_PATTERN,
            cls.CONTACT_PATTERN,
            cls.API_CONTACT_PATTERN
        ]
        
        for pattern in patterns:
            if pattern.match(url):
                return True
        
        return False