"""
Unit tests for Telegram parser module.
"""

import pytest
from app.extractor.telegram_parser import TelegramParser


class TestTelegramParser:
    """Test suite for TelegramParser."""

    def test_parse_username_url(self):
        """Test parsing username URL."""
        result = TelegramParser.parse("https://t.me/testuser")
        
        assert result.entity_type == 'channel'
        assert result.username == 'testuser'
        assert result.is_valid is True
        assert result.is_invite is False

    def test_parse_username_without_scheme(self):
        """Test parsing username URL without scheme."""
        result = TelegramParser.parse("t.me/testuser")
        
        assert result.entity_type == 'channel'
        assert result.username == 'testuser'
        assert result.is_valid is True

    def test_parse_telegram_me_variant(self):
        """Test parsing telegram.me variant."""
        result = TelegramParser.parse("https://telegram.me/testuser")
        
        assert result.entity_type == 'channel'
        assert result.username == 'testuser'
        assert result.is_valid is True

    def test_parse_invite_plus(self):
        """Test parsing invite link with +."""
        result = TelegramParser.parse("https://t.me/+ABC123")
        
        assert result.entity_type == 'invite'
        assert result.invite_hash == 'ABC123'
        assert result.is_invite is True
        assert result.is_valid is True

    def test_parse_invite_joinchat(self):
        """Test parsing invite link with joinchat."""
        result = TelegramParser.parse("https://t.me/joinchat/ABC123")
        
        assert result.entity_type == 'invite'
        assert result.invite_hash == 'ABC123'
        assert result.is_invite is True
        assert result.is_valid is True

    def test_parse_message_link(self):
        """Test parsing message link."""
        result = TelegramParser.parse("https://t.me/testuser/123")
        
        assert result.entity_type == 'message'
        assert result.username == 'testuser'
        assert result.entity_id == '123'
        assert result.is_valid is True

    def test_parse_unknown_url(self):
        """Test parsing unknown URL."""
        result = TelegramParser.parse("https://example.com")
        
        assert result.entity_type == 'unknown'
        assert result.is_valid is False
        assert result.error is not None

    def test_normalize_url(self):
        """Test URL normalization."""
        variants = [
            "https://t.me/test",
            "http://t.me/test",
            "https://telegram.me/test",
            "http://telegram.me/test",
            "t.me/test",
            "telegram.me/test"
        ]
        
        normalized = TelegramParser.normalize("https://t.me/test")
        for variant in variants:
            result = TelegramParser.normalize(variant)
            assert result == normalized

    def test_normalize_remove_trailing_slash(self):
        """Test removing trailing slash."""
        result = TelegramParser.normalize("https://t.me/test/")
        assert result == "https://t.me/test"

    def test_normalize_remove_query_params(self):
        """Test removing query parameters."""
        result = TelegramParser.normalize("https://t.me/test?param=value")
        assert result == "https://t.me/test"

    def test_classify_username(self):
        """Test classifying username URL."""
        classification = TelegramParser.classify("https://t.me/testuser")
        
        assert classification['platform'] == 'telegram'
        assert classification['link_type'] == 'public_channel'
        assert classification['status'] == 'valid'
        assert classification['username'] == 'testuser'

    def test_classify_invite(self):
        """Test classifying invite URL."""
        classification = TelegramParser.classify("https://t.me/+ABC123")
        
        assert classification['platform'] == 'telegram'
        assert classification['link_type'] == 'private_invite'
        assert classification['status'] == 'valid'
        assert classification['invite_hash'] == 'ABC123'

    def test_classify_bot_username(self):
        """Test classifying bot username."""
        classification = TelegramParser.classify("https://t.me/testbot")
        
        assert classification['platform'] == 'telegram'
        assert classification['link_type'] == 'personal_account'
        assert classification['status'] == 'excluded'
        assert classification['username'] == 'testbot'

    def test_is_valid_telegram_url(self):
        """Test validating Telegram URLs."""
        valid_urls = [
            "https://t.me/test",
            "t.me/test",
            "https://t.me/+ABC123",
            "https://t.me/joinchat/ABC123",
            "https://t.me/test/123"
        ]
        
        for url in valid_urls:
            assert TelegramParser.is_valid_telegram_url(url) is True
        
        invalid_urls = [
            "https://example.com",
            "https://chat.whatsapp.com/ABC123",
            "https://wa.me/966500000000"
        ]
        
        for url in invalid_urls:
            assert TelegramParser.is_valid_telegram_url(url) is False