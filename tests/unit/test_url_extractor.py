"""
Unit tests for URL extractor module.
"""

import pytest
from app.extractor.url_extractor import URLExtractor, ExtractedURL


class TestURLExtractor:
    """Test suite for URLExtractor."""

    def test_extract_from_text_simple_urls(self):
        """Test extracting simple URLs from text."""
        text = "Check this link: https://t.me/test and https://chat.whatsapp.com/ABC123"
        urls = URLExtractor.extract_from_text(text)
        
        assert len(urls) == 2
        assert urls[0].url == "https://t.me/test"
        assert urls[1].url == "https://chat.whatsapp.com/ABC123"

    def test_extract_from_text_without_scheme(self):
        """Test extracting URLs without scheme."""
        text = "Links: t.me/test and chat.whatsapp.com/ABC123"
        urls = URLExtractor.extract_from_text(text)
        
        assert len(urls) == 2
        assert urls[0].url == "https://t.me/test"
        assert urls[1].url == "https://chat.whatsapp.com/ABC123"

    def test_extract_from_text_with_punctuation(self):
        """Test extracting URLs with trailing punctuation."""
        text = "Check https://t.me/test, and https://chat.whatsapp.com/ABC123!"
        urls = URLExtractor.extract_from_text(text)
        
        assert len(urls) == 2
        assert urls[0].url == "https://t.me/test"
        assert urls[1].url == "https://chat.whatsapp.com/ABC123"

    def test_extract_from_text_multiple_urls(self):
        """Test extracting multiple URLs from text."""
        text = "URLs: https://t.me/test1, https://t.me/test2, https://t.me/test3"
        urls = URLExtractor.extract_from_text(text)
        
        assert len(urls) == 3
        assert urls[0].url == "https://t.me/test1"
        assert urls[1].url == "https://t.me/test2"
        assert urls[2].url == "https://t.me/test3"

    def test_extract_from_text_telegram_variants(self):
        """Test extracting different Telegram URL variants."""
        text = """
        https://t.me/test
        https://telegram.me/test
        http://t.me/test
        t.me/test
        telegram.me/test
        """
        urls = URLExtractor.extract_from_text(text)
        
        assert len(urls) == 5
        assert all(url.url.startswith("https://") for url in urls)

    def test_extract_from_text_whatsapp_variants(self):
        """Test extracting different WhatsApp URL variants."""
        text = """
        https://chat.whatsapp.com/ABC123
        https://wa.me/966500000000
        https://api.whatsapp.com/send?phone=966500000000
        chat.whatsapp.com/ABC123
        wa.me/966500000000
        """
        urls = URLExtractor.extract_from_text(text)
        
        assert len(urls) == 5
        assert all(url.url.startswith("https://") for url in urls)

    def test_extract_from_entities(self):
        """Test extracting URLs from Telegram entities."""
        text = "Check this link: https://t.me/test"
        
        # Mock entities
        class MockEntity:
            def __init__(self, offset, length, type):
                self.offset = offset
                self.length = length
                self.type = type
        
        entities = [
            MockEntity(offset=16, length=19, type='url')
        ]
        
        urls = URLExtractor.extract_from_entities(text, entities)
        
        assert len(urls) == 1
        assert urls[0].url == "https://t.me/test"
        assert urls[0].is_entity is True

    def test_extract_all_with_entities(self):
        """Test extract_all with both text and entities."""
        text = "Check https://t.me/test1 and https://t.me/test2"
        
        class MockEntity:
            def __init__(self, offset, length, type):
                self.offset = offset
                self.length = length
                self.type = type
        
        entities = [
            MockEntity(offset=6, length=19, type='url')
        ]
        
        urls = URLExtractor.extract_all(text, entities)
        
        # Should contain URLs from both text and entities, deduplicated
        assert len(urls) >= 2
        assert any(u.url == "https://t.me/test1" for u in urls)
        assert any(u.url == "https://t.me/test2" for u in urls)

    def test_extract_telegram_urls(self):
        """Test extracting only Telegram URLs."""
        text = """
        Telegram: https://t.me/test
        WhatsApp: https://chat.whatsapp.com/ABC123
        Other: https://example.com
        """
        urls = URLExtractor.extract_telegram_urls(text)
        
        assert len(urls) == 1
        assert urls[0].url == "https://t.me/test"

    def test_extract_whatsapp_urls(self):
        """Test extracting only WhatsApp URLs."""
        text = """
        Telegram: https://t.me/test
        WhatsApp: https://chat.whatsapp.com/ABC123
        Other: https://example.com
        """
        urls = URLExtractor.extract_whatsapp_urls(text)
        
        assert len(urls) == 1
        assert urls[0].url == "https://chat.whatsapp.com/ABC123"

    def test_extract_from_text_empty(self):
        """Test extracting from empty text."""
        urls = URLExtractor.extract_from_text("")
        assert len(urls) == 0

    def test_extract_from_text_no_urls(self):
        """Test extracting from text with no URLs."""
        text = "This is just plain text with no URLs."
        urls = URLExtractor.extract_from_text(text)
        assert len(urls) == 0