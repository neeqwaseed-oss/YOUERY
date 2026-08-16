"""
Retry module - implements retry decorator with exponential backoff.
"""

import asyncio
import logging
from functools import wraps
from typing import Optional, Callable, Any
from time import sleep

from app.config import config
from app.utils.logger import get_logger

logger = get_logger(__name__)


def retry_async(
    max_retries: int = 3,
    delay: int = 5,
    backoff: int = 2,
    exceptions: tuple = (Exception,)
):
    """
    Retry decorator for async functions with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay in seconds
        backoff: Backoff multiplier
        exceptions: Tuple of exceptions to retry on
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            current_delay = delay
            last_error = None
            
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_error = e
                    logger.warning(
                        f"Attempt {attempt + 1}/{max_retries} failed for {func.__name__}: {e}"
                    )
                    
                    if attempt < max_retries - 1:
                        logger.debug(f"Retrying in {current_delay} seconds...")
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(
                            f"All {max_retries} attempts failed for {func.__name__}"
                        )
                        raise
            
            raise last_error
        
        return wrapper
    return decorator


def retry_sync(
    max_retries: int = 3,
    delay: int = 5,
    backoff: int = 2,
    exceptions: tuple = (Exception,)
):
    """
    Retry decorator for sync functions with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay in seconds
        backoff: Backoff multiplier
        exceptions: Tuple of exceptions to retry on
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            current_delay = delay
            last_error = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_error = e
                    logger.warning(
                        f"Attempt {attempt + 1}/{max_retries} failed for {func.__name__}: {e}"
                    )
                    
                    if attempt < max_retries - 1:
                        logger.debug(f"Retrying in {current_delay} seconds...")
                        sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(
                            f"All {max_retries} attempts failed for {func.__name__}"
                        )
                        raise
            
            raise last_error
        
        return wrapper
    return decorator


def is_retryable_error(error: Exception) -> bool:
    """
    Check if an error is retryable.
    
    Args:
        error: The error to check
        
    Returns:
        True if retryable, False otherwise
    """
    from telethon.errors import FloodWaitError, RPCError
    from aiohttp import ClientError
    from sqlite3 import OperationalError
    
    # These errors are retryable
    retryable_errors = (
        FloodWaitError,
        TimeoutError,
        ConnectionError,
        ClientError,
        RPCError,
        OperationalError
    )
    
    return isinstance(error, retryable_errors)