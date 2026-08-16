"""
Rate limiter module - implements rate limiting for API calls.
"""

import asyncio
import time
from typing import Optional
from collections import deque

from app.config import config
from app.utils.logger import get_logger

logger = get_logger(__name__)


class RateLimiter:
    """
    Rate limiter for API calls.
    Limits requests per second and per minute.
    """
    
    def __init__(
        self,
        max_per_second: int = 2,
        max_per_minute: int = 30
    ):
        self.max_per_second = max_per_second
        self.max_per_minute = max_per_minute
        
        # Track request timestamps
        self.second_window = deque(maxlen=max_per_second)
        self.minute_window = deque(maxlen=max_per_minute)
        
        # Lock for thread safety
        self._lock = asyncio.Lock()
    
    async def wait_if_needed(self):
        """
        Wait if rate limit is exceeded.
        """
        async with self._lock:
            now = time.time()
            
            # Clean old entries
            while self.second_window and self.second_window[0] < now - 1:
                self.second_window.popleft()
            
            while self.minute_window and self.minute_window[0] < now - 60:
                self.minute_window.popleft()
            
            # Check if we need to wait
            if len(self.second_window) >= self.max_per_second:
                wait_time = 1 - (now - self.second_window[0])
                if wait_time > 0:
                    logger.debug(f"Rate limit reached, waiting {wait_time:.2f}s")
                    await asyncio.sleep(wait_time)
                    await self.wait_if_needed()  # Recursive check
                    return
            
            if len(self.minute_window) >= self.max_per_minute:
                wait_time = 60 - (now - self.minute_window[0])
                if wait_time > 0:
                    logger.debug(f"Minute rate limit reached, waiting {wait_time:.2f}s")
                    await asyncio.sleep(wait_time)
                    await self.wait_if_needed()  # Recursive check
                    return
            
            # Add current request
            self.second_window.append(now)
            self.minute_window.append(now)
    
    async def acquire(self):
        """
        Acquire a rate limit slot.
        """
        await self.wait_if_needed()
    
    @property
    def current_rate(self) -> dict:
        """
        Get current rate information.
        
        Returns:
            Dictionary with current rate stats
        """
        now = time.time()
        
        # Clean old entries
        while self.second_window and self.second_window[0] < now - 1:
            self.second_window.popleft()
        
        while self.minute_window and self.minute_window[0] < now - 60:
            self.minute_window.popleft()
        
        return {
            'per_second': len(self.second_window),
            'per_minute': len(self.minute_window),
            'max_per_second': self.max_per_second,
            'max_per_minute': self.max_per_minute
        }