"""
Message reader module - reads messages from Telegram sources.
"""

import asyncio
from typing import List, Dict, Any, Optional, AsyncGenerator
from datetime import datetime

from telethon.tl.functions.messages import GetHistoryRequest
from telethon.errors import FloodWaitError, RPCError

from app.telegram.userbot_manager import UserbotManager
from app.utils.logger import get_logger
from app.utils.rate_limiter import RateLimiter

logger = get_logger(__name__)


class MessageReader:
    """
    Reads messages from Telegram channels/groups.
    """
    
    def __init__(self, userbot_manager: UserbotManager):
        self.userbot = userbot_manager
        self.rate_limiter = RateLimiter(
            max_per_second=2,
            max_per_minute=30
        )
    
    async def read_messages(
        self,
        source_id: int,
        limit: int = 1000,
        start_message_id: Optional[int] = None,
        end_message_id: Optional[int] = None,
        cancel_flag: Optional[callable] = None
    ) -> AsyncGenerator[List[Dict[str, Any]], None]:
        """
        Read messages from a source.
        
        Args:
            source_id: Telegram chat ID
            limit: Maximum number of messages to read
            start_message_id: Starting message ID (for range mode)
            end_message_id: Ending message ID (for range mode)
            cancel_flag: Optional function to check cancellation
            
        Yields:
            Batches of message dictionaries
        """
        if not self.userbot.is_initialized:
            raise ValueError("Userbot not initialized")
        
        try:
            # Get entity
            entity = await self.userbot.get_entity_by_id(source_id)
            if not entity:
                raise ValueError(f"Source {source_id} not found")
            
            # Calculate offset based on mode
            offset_id = 0
            if end_message_id:
                offset_id = end_message_id + 1
            
            # Read messages in batches
            current_limit = limit
            messages_read = 0
            
            while messages_read < limit:
                # Check cancellation
                if cancel_flag and cancel_flag():
                    logger.info(f"Message reading cancelled for source {source_id}")
                    break
                
                # Apply rate limiting
                await self.rate_limiter.wait_if_needed()
                
                try:
                    # Fetch messages
                    result = await self.userbot.client(GetHistoryRequest(
                        peer=entity['entity'],
                        offset_id=offset_id,
                        offset_date=None,
                        add_offset=0,
                        limit=min(100, current_limit),
                        max_id=0,
                        min_id=0,
                        hash=0
                    ))
                    
                    if not result.messages:
                        break
                    
                    # Process messages
                    batch = []
                    for message in result.messages:
                        # Check if we've reached the start message (for range mode)
                        if start_message_id and message.id < start_message_id:
                            continue
                        
                        # Extract message data
                        message_data = {
                            'id': message.id,
                            'source_id': source_id,
                            'text': message.text or '',
                            'date': message.date.isoformat() if message.date else None,
                            'from_id': message.from_id.user_id if message.from_id else None,
                            'reply_to_msg_id': message.reply_to_msg_id,
                            'media': message.media is not None,
                            'entities': message.entities if hasattr(message, 'entities') else None
                        }
                        batch.append(message_data)
                    
                    yield batch
                    
                    messages_read += len(batch)
                    current_limit -= len(batch)
                    
                    # Update offset for next batch
                    if result.messages:
                        offset_id = result.messages[-1].id
                    
                    # Small delay to prevent flooding
                    await asyncio.sleep(0.5)
                    
                except FloodWaitError as e:
                    wait_time = e.seconds
                    logger.warning(f"Flood wait for {wait_time} seconds")
                    await asyncio.sleep(wait_time)
                    continue
                    
                except RPCError as e:
                    logger.error(f"RPC error reading messages: {e}")
                    break
                    
                except Exception as e:
                    logger.error(f"Error reading messages: {e}")
                    break
            
        except Exception as e:
            logger.error(f"Failed to read messages from source {source_id}: {e}")
            raise
    
    async def count_messages(self, source_id: int) -> int:
        """
        Count total messages in a source.
        
        Args:
            source_id: Telegram chat ID
            
        Returns:
            Number of messages
        """
        if not self.userbot.is_initialized:
            raise ValueError("Userbot not initialized")
        
        try:
            entity = await self.userbot.get_entity_by_id(source_id)
            if not entity:
                return 0
            
            # Use get_participants to estimate message count for channels
            # For groups, get history to estimate
            result = await self.userbot.client(GetHistoryRequest(
                peer=entity['entity'],
                offset_id=0,
                offset_date=None,
                add_offset=0,
                limit=1,
                max_id=0,
                min_id=0,
                hash=0
            ))
            
            if result.messages:
                # Use the ID of the latest message as an estimate
                return result.messages[0].id
            
            return 0
            
        except Exception as e:
            logger.error(f"Failed to count messages in source {source_id}: {e}")
            return 0