"""
Unit tests for WhatsApp parser module.
"""

import pytest
from app.extractor.whatsapp_parser import WhatsAppParser


class TestWhatsAppParser:
    """Test suite for WhatsAppParser."""

    def test_parse_group_url(self):
        """Test parsing group URL."""
        result = WhatsAppParser.parse("https://chat.whatsapp.com/ABC123")
        
        assert result.entity_type == 'group'
        assert result.group_id == 'ABC123'
        assert result.is_valid is True

    def test_parse_group_without_scheme(self):
        """Test parsing group URL without scheme."""
        result = WhatsAppParser.parse("chat.whatsapp.com/ABC123")
        
        assert result.entity_type == 'group'
        assert result.group_id == 'ABC123'
        assert result.is_valid is True

    def test_parse_contact_wa_me(self):
        """Test parsing contact URL with wa.me."""
        result = WhatsAppParser.parse("https://wa.me/966500000000")
        
        assert result.entity_type == 'contact'
        assert result.phone_number == '966500000000'
        assert result.is_valid is True

    def test_parse_contact_api(self):
        """Test parsing contact URL with API."""
        result = WhatsAppParser.parse("https://api.whatsapp.com/send?phone=966500000000")
        
        assert result.entity_type == 'contact'
        assert result.phone_number == '966500000000'
        assert result.is_valid is True

    def test_parse_unknown_url(self):
        """Test parsing unknown URL."""
        result = WhatsAppParser.parse("https://example.com")
        
        assert result.entity_type == 'unknown'
        assert result.is_valid is False
        assert result.error is not None

    def test_normalize_url(self):
        """Test URL normalization."""
        variants = [
            "https://chat.whatsapp.com/ABC123",
            "http://chat.whatsapp.com/ABC123",
            "chat.whatsapp.com/ABC123"
        ]
        
        normalized = WhatsAppParser.normalize("https://chat.whatsapp.com/ABC123")
        for variant in variants:
            result = WhatsAppParser.normalize(variant)
            assert result == normalized

    def test_normalize_remove_trailing_slash(self):
        """Test removing trailing slash."""
        result = WhatsAppParser.normalize("https://chat.whatsapp.com/ABC123/")
        assert result == "https://chat.whatsapp.com/ABC123"

    def test_normalize_remove_query_params(self):
        """Test removing query parameters (except API)."""
        result = WhatsAppParser.normalize("https://chat.whatsapp.com/ABC123?param=value")
        assert result == "https://chat.whatsapp.com/ABC123"

    def test_normalize_preserve_api_params(self):
        """Test preserving API query parameters."""
        result = WhatsAppParser.normalize("https://api.whatsapp.com/send?phone=966500000000&text=hello")
        assert "send?phone=966500000000" in result

    def test_classify_group(self):
        """Test classifying group URL."""
        classification = WhatsAppParser.classify("https://chat.whatsapp.com/ABC123")
        
        assert classification['platform'] == 'whatsapp'
        assert classification['link_type'] == 'group'
        assert classification['status'] == 'valid'
        assert classification['group_id'] == 'ABC123'

    def test_classify_contact(self):
        """Test classifying contact URL."""
        classification = WhatsAppParser.classify("https://wa.me/966500000000")
        
        assert classification['platform'] == 'whatsapp'
        assert classification['link_type'] == 'contact'
        assert classification['status'] == 'valid'
        assert classification['phone_number'] == '966500000000'

    def test_is_valid_whatsapp_url(self):
        """Test validating WhatsApp URLs."""
        valid_urls = [
            "https://chat.whatsapp.com/ABC123",
            "chat.whatsapp.com/ABC123",
            "https://wa.me/966500000000",
            "wa.me/966500000000",
            "https://api.whatsapp.com/send?phone=966500000000"
        ]
        
        for url in valid_urls:
            assert WhatsAppParser.is_valid_whatsapp_url(url) is True
        
        invalid_urls = [
            "https://example.com",
            "https://t.me/test",
            "https://t.me/+ABC123"
        ]
        
        for url in invalid_urls:
            assert WhatsAppParser.is_valid_whatsapp_url(url) is False