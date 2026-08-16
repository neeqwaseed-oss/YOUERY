"""
Unit tests for deduplicator module.
"""

import pytest
from app.extractor.deduplicator import Deduplicator


class TestDeduplicator:
    """Test suite for Deduplicator."""

    def test_deduplicate_basic(self):
        """Test basic deduplication."""
        urls = [
            "https://t.me/test",
            "https://t.me/test",
            "https://t.me/test"
        ]
        
        result = Deduplicator.deduplicate(urls)
        
        assert result.unique_count == 1
        assert result.duplicate_count == 2
        assert len(result.unique_urls) == 1
        assert len(result.duplicates) == 2

    def test_deduplicate_with_variants(self):
        """Test deduplication with URL variants."""
        urls = [
            "https://t.me/test",
            "http://t.me/test",
            "https://telegram.me/test",
            "t.me/test"
        ]
        
        result = Deduplicator.deduplicate(urls)
        
        assert result.unique_count == 1
        assert result.duplicate_count == 3

    def test_deduplicate_with_whatsapp(self):
        """Test deduplication with WhatsApp URLs."""
        urls = [
            "https://chat.whatsapp.com/ABC123",
            "chat.whatsapp.com/ABC123",
            "https://chat.whatsapp.com/ABC123"
        ]
        
        result = Deduplicator.deduplicate(urls)
        
        assert result.unique_count == 1
        assert result.duplicate_count == 2

    def test_deduplicate_mixed_urls(self):
        """Test deduplication with mixed URLs."""
        urls = [
            "https://t.me/test1",
            "https://t.me/test2",
            "https://t.me/test1",  # duplicate
            "https://chat.whatsapp.com/ABC123",
            "https://example.com",
            "https://example.com"  # duplicate
        ]
        
        result = Deduplicator.deduplicate(urls)
        
        assert result.unique_count == 4
        assert result.duplicate_count == 2
        assert len(result.unique_urls) == 4

    def test_deduplicate_empty_list(self):
        """Test deduplication with empty list."""
        result = Deduplicator.deduplicate([])
        
        assert result.unique_count == 0
        assert result.duplicate_count == 0
        assert len(result.unique_urls) == 0

    def test_deduplicate_with_metadata(self):
        """Test deduplication with metadata."""
        urls_with_metadata = [
            {'url': 'https://t.me/test', 'source': 'A'},
            {'url': 'https://t.me/test', 'source': 'B'},
            {'url': 'https://t.me/test2', 'source': 'C'}
        ]
        
        result = Deduplicator.deduplicate_with_metadata(urls_with_metadata)
        
        assert len(result) == 2
        assert result[0]['url'] == 'https://t.me/test'
        assert result[1]['url'] == 'https://t.me/test2'
        assert 'normalized_url' in result[0]

    def test_get_duplicate_info(self):
        """Test getting duplicate information."""
        urls = [
            "https://t.me/test",
            "https://t.me/test",
            "https://t.me/test2",
            "https://t.me/test3",
            "https://t.me/test3"
        ]
        
        result = Deduplicator.get_duplicate_info(urls)
        
        assert result["https://t.me/test"] == 2
        assert result["https://t.me/test2"] == 1
        assert result["https://t.me/test3"] == 2

    def test_deduplicate_telegram_variants(self):
        """Test deduplication with Telegram variants."""
        urls = [
            "https://t.me/test",
            "https://telegram.me/test",
            "http://t.me/test",
            "t.me/test",
            "telegram.me/test"
        ]
        
        result = Deduplicator.deduplicate(urls)
        
        assert result.unique_count == 1
        assert result.duplicate_count == 4

    def test_deduplicate_with_trailing_slash(self):
        """Test deduplication with trailing slash variants."""
        urls = [
            "https://t.me/test",
            "https://t.me/test/",
            "https://t.me/test//"
        ]
        
        result = Deduplicator.deduplicate(urls)
        
        assert result.unique_count == 1
        assert result.duplicate_count == 2