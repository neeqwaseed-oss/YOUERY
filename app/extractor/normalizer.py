"""
URL normalizer module - normalizes URLs to canonical forms.
"""

import re
from typing import Optional
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode

from app.utils.logger import get_logger

logger = get_logger(__name__)


class URLNormalizer:
    """
    Normalizes URLs to canonical forms for deduplication.
    """
    
    # Patterns for cleaning URLs
    TRAILING_SLASH = re.compile(r'/+$')
    LEADING_SLASH = re.compile(r'^/+')
    MULTIPLE_SLASHES = re.compile(r'/{2,}')
    
    # Common tracking parameters to remove
    TRACKING_PARAMS = [
        'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
        'fbclid', 'gclid', 'msclkid', 'ref', 'source', 'si', 'ei',
        'mibextid', 'igshid', 'mc_cid', 'mc_eid', 'trk', 'trkCampaign'
    ]
    
    @classmethod
    def normalize(cls, url: str) -> str:
        """
        Normalize a URL to canonical form.
        
        Args:
            url: The URL to normalize
            
        Returns:
            Normalized URL string
        """
        if not url:
            return ""
        
        # Basic cleanup
        url = url.strip()
        
        # Add scheme if missing
        if not url.startswith(('http://', 'https://')):
            if url.startswith('t.me/') or url.startswith('telegram.me/'):
                url = 'https://' + url
            elif url.startswith('chat.whatsapp.com/') or url.startswith('wa.me/'):
                url = 'https://' + url
            else:
                url = 'https://' + url
        
        # Parse URL
        try:
            parsed = urlparse(url)
        except Exception as e:
            logger.warning(f"Failed to parse URL {url}: {e}")
            return url
        
        # Normalize scheme (prefer https)
        scheme = 'https' if parsed.scheme in ('http', 'https') else parsed.scheme
        
        # Normalize domain (lowercase)
        netloc = parsed.netloc.lower()
        
        # Remove default ports
        netloc = netloc.replace(':443', '').replace(':80', '')
        
        # Normalize path
        path = parsed.path
        path = cls.MULTIPLE_SLASHES.sub('/', path)
        path = cls.LEADING_SLASH.sub('', path)
        
        # Remove trailing slash for non-root paths
        if path and path != '/' and path.endswith('/'):
            path = path[:-1]
        
        # Clean query parameters
        query = cls._clean_query_params(parsed.query)
        
        # Reconstruct URL
        normalized = urlunparse((scheme, netloc, path, parsed.params, query, parsed.fragment))
        
        return normalized
    
    @classmethod
    def _clean_query_params(cls, query: str) -> str:
        """
        Remove tracking parameters from query string.
        
        Args:
            query: Query string
            
        Returns:
            Cleaned query string
        """
        if not query:
            return ''
        
        try:
            params = parse_qs(query, keep_blank_values=True)
            
            # Remove tracking parameters
            for param in cls.TRACKING_PARAMS:
                params.pop(param, None)
            
            # Rebuild query string
            if params:
                return urlencode(params, doseq=True)
            return ''
        except Exception:
            return query
    
    @classmethod
    def is_valid_url(cls, url: str) -> bool:
        """
        Check if a URL is valid.
        
        Args:
            url: The URL to check
            
        Returns:
            True if valid, False otherwise
        """
        if not url or len(url) < 5:
            return False
        
        url = url.strip()
        
        # Check for common invalid patterns
        invalid_patterns = [
            r'^javascript:', r'^data:', r'^file:', r'^ftp:',
            r'^mailto:', r'^tel:', r'^sms:', r'^about:'
        ]
        
        for pattern in invalid_patterns:
            if re.match(pattern, url, re.IGNORECASE):
                return False
        
        # Basic URL validation
        try:
            parsed = urlparse(url)
            return bool(parsed.scheme and parsed.netloc)
        except Exception:
            return False
    
    @classmethod
    def is_same_domain(cls, url1: str, url2: str) -> bool:
        """
        Check if two URLs are on the same domain.
        
        Args:
            url1: First URL
            url2: Second URL
            
        Returns:
            True if same domain, False otherwise
        """
        try:
            parsed1 = urlparse(url1)
            parsed2 = urlparse(url2)
            return parsed1.netloc.lower() == parsed2.netloc.lower()
        except Exception:
            return False