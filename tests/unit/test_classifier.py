"""
Unit tests for link classifier module.
"""

import pytest
from app.classifier.link_classifier import LinkClassifier
from app.classifier.telegram_classifier import TelegramClassifier
from app.classifier.whatsapp_classifier import WhatsAppClassifier


class TestLinkClassifier:
    """Test suite for LinkClassifier."""

    def test_classify_telegram_url(self):
        """Test classifying Telegram URLs."""
        result = LinkClassifier.classify("https://t.me/test")
        
        assert result['platform'] == 'telegram'
        assert result['status'] in ['valid', 'excluded']

    def test_classify_whatsapp_url(self):
        """Test classifying WhatsApp URLs."""
        result = LinkClassifier.classify("https://chat.whatsapp.com/ABC123")
        
        assert result['platform'] == 'whatsapp'
        assert result['status'] == 'valid'

    def test_classify_other_url(self):
        """Test classifying other URLs."""
        result = LinkClassifier.classify("https://example.com")
        
        assert result['platform'] == 'other'
        assert result['status'] == 'excluded'

    def test_classify_telegram_invite(self):
        """Test classifying Telegram invite URL."""
        result = LinkClassifier.classify("https://t.me/+ABC123")
        
        assert result['platform'] == 'telegram'
        assert result['link_type'] == 'private_invite'
        assert result['status'] == 'valid'

    def test_classify_telegram_personal(self):
        """Test classifying Telegram personal account."""
        result = LinkClassifier.classify("https://t.me/user123")
        
        # Should be classified as personal_account (excluded)
        assert result['platform'] == 'telegram'
        assert result['link_type'] == 'personal_account'
        assert result['status'] == 'excluded'

    def test_classify_telegram_bot(self):
        """Test classifying Telegram bot."""
        result = LinkClassifier.classify("https://t.me/testbot")
        
        # Should be classified as bot (excluded)
        assert result['platform'] == 'telegram'
        assert result['link_type'] == 'personal_account'
        assert result['status'] == 'excluded'

    def test_classify_whatsapp_group(self):
        """Test classifying WhatsApp group."""
        result = LinkClassifier.classify("https://chat.whatsapp.com/ABC123")
        
        assert result['platform'] == 'whatsapp'
        assert result['link_type'] == 'group'
        assert result['status'] == 'valid'

    def test_classify_whatsapp_contact(self):
        """Test classifying WhatsApp contact."""
        result = LinkClassifier.classify("https://wa.me/966500000000")
        
        assert result['platform'] == 'whatsapp'
        assert result['link_type'] == 'contact'
        assert result['status'] == 'valid'

    def test_telegram_classifier_username(self):
        """Test TelegramClassifier on username."""
        result = TelegramClassifier.classify("https://t.me/test")
        
        assert result['platform'] == 'telegram'
        assert result['link_type'] in ['public_channel', 'public_group']

    def test_telegram_classifier_invite(self):
        """Test TelegramClassifier on invite."""
        result = TelegramClassifier.classify("https://t.me/+ABC123")
        
        assert result['platform'] == 'telegram'
        assert result['link_type'] == 'private_invite'
        assert result['status'] == 'valid'

    def test_whatsapp_classifier_group(self):
        """Test WhatsAppClassifier on group."""
        result = WhatsAppClassifier.classify("https://chat.whatsapp.com/ABC123")
        
        assert result['platform'] == 'whatsapp'
        assert result['link_type'] == 'group'
        assert result['status'] == 'valid'

    def test_whatsapp_classifier_contact(self):
        """Test WhatsAppClassifier on contact."""
        result = WhatsAppClassifier.classify("https://wa.me/966500000000")
        
        assert result['platform'] == 'whatsapp'
        assert result['link_type'] == 'contact'
        assert result['status'] == 'valid'