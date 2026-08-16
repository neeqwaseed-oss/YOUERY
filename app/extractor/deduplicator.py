"""
Deduplicator module - removes duplicate URLs based on normalized form.
"""

from typing import Dict, List, Set, Optional
from dataclasses import dataclass

from app.extractor.normalizer import URLNormalizer
from app.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class DeduplicateResult:
    """Result of deduplication operation."""
    unique_urls: List[str]
    duplicates: List[str]
    duplicate_count: int
    unique_count: int


class Deduplicator:
    """
    Removes duplicate URLs based on normalized form.
    """
    
    @classmethod
    def deduplicate(cls, urls: List[str]) -> DeduplicateResult:
        """
        Deduplicate a list of URLs.
        
        Args:
            urls: List of URLs to deduplicate
            
        Returns:
            DeduplicateResult with unique URLs and duplicate information
        """
        if not urls:
            return DeduplicateResult([], [], 0, 0)
        
        # Normalize all URLs first
        normalized_map: Dict[str, str] = {}  # normalized -> original
        seen_normalized: Set[str] = set()
        duplicates: List[str] = []
        
        for url in urls:
            normalized = URLNormalizer.normalize(url)
            
            if normalized in seen_normalized:
                duplicates.append(url)
            else:
                seen_normalized.add(normalized)
                normalized_map[normalized] = url
        
        unique_urls = list(normalized_map.values())
        
        return DeduplicateResult(
            unique_urls=unique_urls,
            duplicates=duplicates,
            duplicate_count=len(duplicates),
            unique_count=len(unique_urls)
        )
    
    @classmethod
    def deduplicate_with_metadata(cls, urls: List[Dict]) -> List[Dict]:
        """
        Deduplicate URLs with metadata, keeping first occurrence.
        
        Args:
            urls: List of URL dictionaries with metadata
            
        Returns:
            List of unique URL dictionaries
        """
        if not urls:
            return []
        
        seen_normalized: Set[str] = set()
        unique_urls: List[Dict] = []
        
        for url_data in urls:
            url = url_data.get('url', '')
            normalized = URLNormalizer.normalize(url)
            
            if normalized not in seen_normalized:
                seen_normalized.add(normalized)
                url_data['normalized_url'] = normalized
                unique_urls.append(url_data)
            else:
                # Mark as duplicate
                url_data['is_duplicate'] = True
                # Don't add to unique list
        
        return unique_urls
    
    @classmethod
    def get_duplicate_info(cls, urls: List[str]) -> Dict[str, int]:
        """
        Get duplicate information for a list of URLs.
        
        Args:
            urls: List of URLs
            
        Returns:
            Dictionary with URL and count of occurrences
        """
        if not urls:
            return {}
        
        url_counts: Dict[str, int] = {}
        normalized_counts: Dict[str, int] = {}
        
        for url in urls:
            normalized = URLNormalizer.normalize(url)
            normalized_counts[normalized] = normalized_counts.get(normalized, 0) + 1
        
        # Map back to original URLs (keep first occurrence)
        result: Dict[str, int] = {}
        seen_normalized: Set[str] = set()
        
        for url in urls:
            normalized = URLNormalizer.normalize(url)
            if normalized not in seen_normalized:
                seen_normalized.add(normalized)
                result[url] = normalized_counts.get(normalized, 0)
        
        return result