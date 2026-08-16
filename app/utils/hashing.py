"""
Hashing module - provides hashing utilities for deduplication.
"""

import hashlib
from typing import Optional


def hash_url(url: str) -> str:
    """
    Create a hash of a URL for deduplication.
    
    Args:
        url: URL to hash
        
    Returns:
        SHA-256 hash of the URL
    """
    normalized = url.strip().lower()
    return hashlib.sha256(normalized.encode('utf-8')).hexdigest()


def hash_string(text: str) -> str:
    """
    Create a hash of a string.
    
    Args:
        text: String to hash
        
    Returns:
        SHA-256 hash of the string
    """
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def generate_entity_id(platform: str, entity_type: str, identifier: str) -> str:
    """
    Generate a unique entity ID.
    
    Args:
        platform: Platform (telegram, whatsapp)
        entity_type: Entity type
        identifier: Identifier (username, ID, hash)
        
    Returns:
        Unique entity ID
    """
    source = f"{platform}:{entity_type}:{identifier}"
    return hash_string(source)


def generate_link_id(url: str, source_id: int) -> str:
    """
    Generate a unique link ID.
    
    Args:
        url: URL
        source_id: Source ID
        
    Returns:
        Unique link ID
    """
    source = f"{hash_url(url)}:{source_id}"
    return hash_string(source)