"""
URL extractor module - extracts URLs from message text and entities.
"""

import re
from typing import List, Set, Optional
from dataclasses import dataclass

from app.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ExtractedURL:
    """Represents an extracted URL with metadata."""
    url: str
    start_pos: int
    end_pos: int
    is_entity: bool = False
    message_id: Optional[int] = None


class URLExtractor:
    """
    Extracts URLs from message text and Telegram message entities.
    """
    
    # URL pattern for extracting URLs from text
    URL_PATTERN = re.compile(
        r'(?:(?:https?://)|(?:www\.))?[a-zA-Z0-9\-._~!$&\'()*+,;=:%/@?]+'
        r'(?:\.[a-zA-Z0-9\-._~!$&\'()*+,;=:%/@?]+)+'
        r'(?:[?/#][a-zA-Z0-9\-._~!$&\'()*+,;=:%/@?]*)?'
    )
    
    # Telegram URL patterns
    TELEGRAM_URL_PATTERNS = [
        re.compile(r'https?://t\.me/([a-zA-Z0-9_]+)(?:[?/#][a-zA-Z0-9_\-=&?]*)?'),
        re.compile(r'https?://telegram\.me/([a-zA-Z0-9_]+)(?:[?/#][a-zA-Z0-9_\-=&?]*)?'),
        re.compile(r'https?://t\.me/\+([a-zA-Z0-9_\-]+)'),
        re.compile(r'https?://t\.me/joinchat/([a-zA-Z0-9_\-]+)'),
        re.compile(r't\.me/([a-zA-Z0-9_]+)(?:[?/#][a-zA-Z0-9_\-=&?]*)?'),
        re.compile(r'telegram\.me/([a-zA-Z0-9_]+)(?:[?/#][a-zA-Z0-9_\-=&?]*)?'),
    ]
    
    # WhatsApp URL patterns
    WHATSAPP_URL_PATTERNS = [
        re.compile(r'https?://chat\.whatsapp\.com/([a-zA-Z0-9_\-]+)'),
        re.compile(r'https?://wa\.me/([0-9\+]+)'),
        re.compile(r'https?://api\.whatsapp\.com/send\?phone=([0-9\+]+)'),
        re.compile(r'chat\.whatsapp\.com/([a-zA-Z0-9_\-]+)'),
        re.compile(r'wa\.me/([0-9\+]+)'),
    ]
    
    # Cleanup patterns for trailing punctuation
    TRAILING_PUNCTUATION = re.compile(r'[.,!?;:()\[\]]+$')
    
    @classmethod
    def extract_from_text(cls, text: str, message_id: Optional[int] = None) -> List[ExtractedURL]:
        """
        Extract URLs from plain text.
        
        Args:
            text: The text to extract URLs from
            message_id: Optional message ID for metadata
            
        Returns:
            List of ExtractedURL objects
        """
        if not text:
            return []
        
        urls = []
        for match in cls.URL_PATTERN.finditer(text):
            url = match.group(0)
            
            # Clean trailing punctuation
            url = cls.TRAILING_PUNCTUATION.sub('', url)
            
            # Ensure URL has scheme for proper parsing
            if not url.startswith(('http://', 'https://')):
                if url.startswith('www.'):
                    url = 'https://' + url
                elif any(url.startswith(prefix) for prefix in ['t.me/', 'telegram.me/', 'chat.whatsapp.com/', 'wa.me/']):
                    url = 'https://' + url
            
            urls.append(ExtractedURL(
                url=url,
                start_pos=match.start(),
                end_pos=match.end(),
                message_id=message_id
            ))
        
        return urls
    
    @classmethod
    def extract_from_entities(cls, text: str, entities: List, message_id: Optional[int] = None) -> List[ExtractedURL]:
        """
        Extract URLs from Telegram message entities.
        
        Args:
            text: The message text
            entities: List of Telegram message entities
            message_id: Optional message ID for metadata
            
        Returns:
            List of ExtractedURL objects
        """
        if not entities or not text:
            return []
        
        urls = []
        for entity in entities:
            if hasattr(entity, 'type') and entity.type == 'url':
                url = text[entity.offset:entity.offset + entity.length]
                
                # Clean trailing punctuation
                url = cls.TRAILING_PUNCTUATION.sub('', url)
                
                # Ensure URL has scheme
                if not url.startswith(('http://', 'https://')):
                    if url.startswith('www.'):
                        url = 'https://' + url
                    elif any(url.startswith(prefix) for prefix in ['t.me/', 'telegram.me/', 'chat.whatsapp.com/', 'wa.me/']):
                        url = 'https://' + url
                
                urls.append(ExtractedURL(
                    url=url,
                    start_pos=entity.offset,
                    end_pos=entity.offset + entity.length,
                    is_entity=True,
                    message_id=message_id
                ))
        
        return urls
    
    @classmethod
    def extract_all(cls, text: str, entities: Optional[List] = None, 
                    message_id: Optional[int] = None) -> List[ExtractedURL]:
        """
        Extract all URLs from text and entities, removing duplicates.
        
        Args:
            text: The message text
            entities: Optional list of Telegram entities
            message_id: Optional message ID
            
        Returns:
            List of unique ExtractedURL objects
        """
        all_urls = []
        
        # Extract from text
        text_urls = cls.extract_from_text(text, message_id)
        all_urls.extend(text_urls)
        
        # Extract from entities if provided
        if entities:
            entity_urls = cls.extract_from_entities(text, entities, message_id)
            all_urls.extend(entity_urls)
        
        # Remove duplicates (keep first occurrence)
        seen_urls = set()
        unique_urls = []
        for url_obj in all_urls:
            if url_obj.url not in seen_urls:
                unique_urls.append(url_obj)
                seen_urls.add(url_obj.url)
        
        return unique_urls
    
    @classmethod
    def extract_telegram_urls(cls, text: str, message_id: Optional[int] = None) -> List[ExtractedURL]:
        """
        Extract only Telegram URLs from text.
        
        Args:
            text: The text to extract from
            message_id: Optional message ID
            
        Returns:
            List of Telegram URL objects
        """
        if not text:
            return []
        
        urls = []
        for pattern in cls.TELEGRAM_URL_PATTERNS:
            for match in pattern.finditer(text):
                url = match.group(0)
                if not url.startswith(('http://', 'https://')):
                    url = 'https://' + url
                urls.append(ExtractedURL(
                    url=url,
                    start_pos=match.start(),
                    end_pos=match.end(),
                    message_id=message_id
                ))
        
        # Remove duplicates
        seen_urls = set()
        unique_urls = []
        for url_obj in urls:
            if url_obj.url not in seen_urls:
                unique_urls.append(url_obj)
                seen_urls.add(url_obj.url)
        
        return unique_urls
    
    @classmethod
    def extract_whatsapp_urls(cls, text: str, message_id: Optional[int] = None) -> List[ExtractedURL]:
        """
        Extract only WhatsApp URLs from text.
        
        Args:
            text: The text to extract from
            message_id: Optional message ID
            
        Returns:
            List of WhatsApp URL objects
        """
        if not text:
            return []
        
        urls = []
        for pattern in cls.WHATSAPP_URL_PATTERNS:
            for match in pattern.finditer(text):
                url = match.group(0)
                if not url.startswith(('http://', 'https://')):
                    url = 'https://' + url
                urls.append(ExtractedURL(
                    url=url,
                    start_pos=match.start(),
                    end_pos=match.end(),
                    message_id=message_id
                ))
        
        # Remove duplicates
        seen_urls = set()
        unique_urls = []
        for url_obj in urls:
            if url_obj.url not in seen_urls:
                unique_urls.append(url_obj)
                seen_urls.add(url_obj.url)
        
        return unique_urls