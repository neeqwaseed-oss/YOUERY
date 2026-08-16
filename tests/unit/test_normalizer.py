"""
Unit tests for URL normalizer module.
"""

import pytest
from app.extractor.normalizer import URLNormalizer


class TestURLNormalizer:
    """Test suite for URLNormalizer."""

    def test_normalize_telegram_urls(self):
        """Test normalizing different Telegram URL variants."""
        variants = [
            ("https://t.me/test", "https://t.me/test"),
            ("http://t.me/test", "https://t.me/test"),
            ("https://telegram.me/test", "https://t.me/test"),
            ("http://telegram.me/test", "https://t.me/test"),
            ("t.me/test", "https://t.me/test"),
            ("telegram.me/test", "https://t.me/test"),
            ("https://t.me/test/", "https://t.me/test"),
        ]
        
        for input_url, expected in variants:
            result = URLNormalizer.normalize(input_url)
            assert result == expected

    def test_normalize_whatsapp_urls(self):
        """Test normalizing different WhatsApp URL variants."""
        variants = [
            ("https://chat.whatsapp.com/ABC123", "https://chat.whatsapp.com/ABC123"),
            ("http://chat.whatsapp.com/ABC123", "https://chat.whatsapp.com/ABC123"),
            ("chat.whatsapp.com/ABC123", "https://chat.whatsapp.com/ABC123"),
            ("https://chat.whatsapp.com/ABC123/", "https://chat.whatsapp.com/ABC123"),
            ("https://wa.me/966500000000", "https://wa.me/966500000000"),
            ("wa.me/966500000000", "https://wa.me/966500000000"),
        ]
        
        for input_url, expected in variants:
            result = URLNormalizer.normalize(input_url)
            assert result == expected

    def test_normalize_remove_tracking_params(self):
        """Test removing tracking parameters."""
        url = "https://example.com?utm_source=google&utm_medium=cpc&fbclid=123&ref=456"
        result = URLNormalizer.normalize(url)
        
        assert "utm_source" not in result
        assert "utm_medium" not in result
        assert "fbclid" not in result
        assert "ref" not in result

    def test_normalize_preserve_important_params(self):
        """Test preserving important parameters."""
        url = "https://api.whatsapp.com/send?phone=966500000000&text=hello"
        result = URLNormalizer.normalize(url)
        
        assert "phone=966500000000" in result
        assert "text=hello" in result

    def test_normalize_remove_default_ports(self):
        """Test removing default ports."""
        url = "https://example.com:443/path"
        result = URLNormalizer.normalize(url)
        assert result == "https://example.com/path"
        
        url = "http://example.com:80/path"
        result = URLNormalizer.normalize(url)
        assert result == "https://example.com/path"

    def test_normalize_handle_multiple_slashes(self):
        """Test handling multiple slashes."""
        url = "https://example.com//path//to//file"
        result = URLNormalizer.normalize(url)
        assert result == "https://example.com/path/to/file"

    def test_normalize_handle_fragments(self):
        """Test handling fragments."""
        url = "https://example.com/path#section"
        result = URLNormalizer.normalize(url)
        assert result == "https://example.com/path#section"

    def test_is_valid_url(self):
        """Test URL validation."""
        valid_urls = [
            "https://example.com",
            "http://example.com",
            "https://t.me/test",
            "https://chat.whatsapp.com/ABC123"
        ]
        
        for url in valid_urls:
            assert URLNormalizer.is_valid_url(url) is True
        
        invalid_urls = [
            "",
            "javascript:alert('test')",
            "data:text/html,<html>",
            "file:///etc/passwd",
            "mailto:user@example.com"
        ]
        
        for url in invalid_urls:
            assert URLNormalizer.is_valid_url(url) is False

    def test_is_same_domain(self):
        """Test domain comparison."""
        assert URLNormalizer.is_same_domain(
            "https://example.com/path1",
            "https://example.com/path2"
        ) is True
        
        assert URLNormalizer.is_same_domain(
            "https://example.com",
            "https://sub.example.com"
        ) is False
        
        assert URLNormalizer.is_same_domain(
            "https://example.com",
            "https://google.com"
        ) is False