"""
Unit tests for hashing utilities.
"""

import pytest
from app.utils.hashing import hash_url, hash_string, generate_entity_id, generate_link_id


class TestHashing:
    """Test suite for hashing utilities."""

    def test_hash_url_consistent(self):
        """Test that hash_url produces consistent results."""
        url = "https://t.me/test"
        
        hash1 = hash_url(url)
        hash2 = hash_url(url)
        
        assert hash1 == hash2

    def test_hash_url_different_urls(self):
        """Test that different URLs produce different hashes."""
        url1 = "https://t.me/test1"
        url2 = "https://t.me/test2"
        
        hash1 = hash_url(url1)
        hash2 = hash_url(url2)
        
        assert hash1 != hash2

    def test_hash_url_normalizes_case(self):
        """Test that hash_url normalizes case."""
        url1 = "https://t.me/Test"
        url2 = "https://t.me/test"
        
        hash1 = hash_url(url1)
        hash2 = hash_url(url2)
        
        # Should be the same because normalization ignores case
        assert hash1 == hash2

    def test_hash_string_consistent(self):
        """Test that hash_string produces consistent results."""
        text = "test string"
        
        hash1 = hash_string(text)
        hash2 = hash_string(text)
        
        assert hash1 == hash2

    def test_hash_string_different(self):
        """Test that different strings produce different hashes."""
        text1 = "test string 1"
        text2 = "test string 2"
        
        hash1 = hash_string(text1)
        hash2 = hash_string(text2)
        
        assert hash1 != hash2

    def test_generate_entity_id(self):
        """Test entity ID generation."""
        entity_id1 = generate_entity_id("telegram", "group", "123")
        entity_id2 = generate_entity_id("telegram", "group", "123")
        
        assert entity_id1 == entity_id2
        
        entity_id3 = generate_entity_id("telegram", "channel", "123")
        assert entity_id1 != entity_id3

    def test_generate_link_id(self):
        """Test link ID generation."""
        link_id1 = generate_link_id("https://t.me/test", 123)
        link_id2 = generate_link_id("https://t.me/test", 123)
        
        assert link_id1 == link_id2
        
        link_id3 = generate_link_id("https://t.me/test2", 123)
        assert link_id1 != link_id3

    def test_hash_url_handles_special_characters(self):
        """Test that hash_url handles special characters."""
        url = "https://t.me/test?param=value&another=123"
        hash_result = hash_url(url)
        
        assert len(hash_result) == 64  # SHA-256 produces 64 characters
        assert isinstance(hash_result, str)

    def test_generate_entity_id_with_identifier(self):
        """Test entity ID generation with different identifiers."""
        id1 = generate_entity_id("telegram", "user", "username")
        id2 = generate_entity_id("telegram", "user", "username")
        
        assert id1 == id2