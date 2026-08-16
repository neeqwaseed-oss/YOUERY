"""
Scan worker module - handles scan jobs with progress tracking.
"""

import asyncio
import time
from typing import Optional, List, Dict, Any, Callable
from datetime import datetime

from app.telegram.userbot_manager import UserbotManager
from app.telegram.message_reader import MessageReader
from app.telegram.entity_resolver import EntityResolver
from app.telegram.invite_resolver import InviteResolver
from app.extractor.url_extractor import URLExtractor
from app.extractor.telegram_parser import TelegramParser
from app.extractor.whatsapp_parser import WhatsAppParser
from app.extractor.normalizer import URLNormalizer
from app.extractor.deduplicator import Deduplicator
from app.database.repositories.scan_repo import ScanRepository
from app.database.repositories.link_repo import LinkRepository
from app.database.repositories.result_repo import ResultRepository
from app.database.repositories.source_repo import SourceRepository
from app.utils.logger import get_logger
from app.utils.rate_limiter import RateLimiter

logger = get_logger(__name__)


class ScanWorker:
    """
    Handles scan jobs with progress tracking and cancellation.
    """
    
    def __init__(self, userbot_manager: UserbotManager):
        self.userbot = userbot_manager
        self.message_reader = MessageReader(userbot_manager)
        self.entity_resolver = EntityResolver(userbot_manager)
        self.invite_resolver = InviteResolver(userbot_manager)
        self.scan_repo = ScanRepository()
        self.link_repo = LinkRepository()
        self.result_repo = ResultRepository()
        self.source_repo = SourceRepository()
        self.rate_limiter = RateLimiter(
            max_per_second=2,
            max_per_minute=30
        )
        self.cancelled = False
        self.current_job_id: Optional[int] = None
    
    def cancel(self):
        """Cancel the current scan job."""
        self.cancelled = True
        logger.info(f"Scan job {self.current_job_id} cancelled")
    
    def is_cancelled(self) -> bool:
        """Check if the current scan job is cancelled."""
        return self.cancelled
    
    async def run_scan(
        self,
        job_id: int,
        source_id: int,
        user_id: int,
        scan_mode: str,
        limit: int = 1000,
        start_message_id: Optional[int] = None,
        end_message_id: Optional[int] = None,
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Run a scan job.
        
        Args:
            job_id: Job ID
            source_id: Source ID
            user_id: User ID
            scan_mode: Scan mode (recent, full, range)
            limit: Message limit
            start_message_id: Starting message ID
            end_message_id: Ending message ID
            progress_callback: Optional callback for progress updates
            
        Returns:
            Scan result dictionary
        """
        self.current_job_id = job_id
        self.cancelled = False
        
        logger.info(f"Starting scan job {job_id} for source {source_id}")
        
        # Update job status to running
        await self.scan_repo.update_status(job_id, 'running')
        
        try:
            # Ensure userbot is initialized
            if not self.userbot.is_initialized:
                await self.userbot.initialize()
            
            # Get source info
            source = await self.source_repo.get_by_id(source_id)
            if not source:
                raise ValueError(f"Source {source_id} not found")
            
            # Statistics
            stats = {
                'messages_scanned': 0,
                'urls_found': 0,
                'urls_unique': 0,
                'telegram_count': 0,
                'whatsapp_count': 0,
                'group_count': 0,
                'channel_count': 0,
                'invite_count': 0,
                'personal_count': 0,
                'bot_count': 0,
                'duplicate_count': 0,
                'other_count': 0,
                'invalid_count': 0
            }
            
            # Process messages
            async for message_batch in self.message_reader.read_messages(
                source_id=source_id,
                limit=limit,
                start_message_id=start_message_id,
                end_message_id=end_message_id,
                cancel_flag=self.is_cancelled
            ):
                # Check cancellation
                if self.is_cancelled():
                    break
                
                # Process each message in batch
                for message in message_batch:
                    # Extract URLs
                    extracted_urls = URLExtractor.extract_all(
                        text=message['text'],
                        entities=message.get('entities'),
                        message_id=message['id']
                    )
                    
                    if extracted_urls:
                        stats['urls_found'] += len(extracted_urls)
                        
                        # Process each URL
                        for url_obj in extracted_urls:
                            url = url_obj.url
                            
                            # Normalize URL
                            normalized_url = URLNormalizer.normalize(url)
                            
                            # Check if already processed (deduplication)
                            existing_link = await self.link_repo.get_by_normalized_url(
                                normalized_url, job_id
                            )
                            
                            if existing_link:
                                stats['duplicate_count'] += 1
                                continue
                            
                            # Classify URL
                            classification = await self._classify_url(url)
                            
                            # Save link
                            await self.link_repo.create(
                                scan_job_id=job_id,
                                source_id=source_id,
                                message_id=message['id'],
                                original_url=url,
                                normalized_url=normalized_url,
                                platform=classification.get('platform', 'other'),
                                link_type=classification.get('link_type', 'unknown'),
                                status=classification.get('status', 'invalid'),
                                entity_id=classification.get('entity_id'),
                                entity_title=classification.get('entity_title'),
                                entity_username=classification.get('entity_username')
                            )
                            
                            # Update stats based on classification
                            self._update_stats(stats, classification)
                            stats['urls_unique'] += 1
                
                stats['messages_scanned'] += len(message_batch)
                
                # Update progress
                if progress_callback:
                    await progress_callback(stats)
                
                # Update job progress in database
                await self.scan_repo.update_progress(
                    job_id,
                    messages_scanned=stats['messages_scanned'],
                    urls_found=stats['urls_found'],
                    urls_unique=stats['urls_unique']
                )
                
                # Check cancellation
                if self.is_cancelled():
                    break
            
            # Save statistics
            await self.result_repo.save_statistics(job_id, stats)
            
            # Update job status
            if self.is_cancelled():
                await self.scan_repo.update_status(job_id, 'cancelled')
                logger.info(f"Scan job {job_id} cancelled")
            else:
                await self.scan_repo.update_status(job_id, 'completed')
                await self.scan_repo.update_completed_at(job_id)
                logger.info(f"Scan job {job_id} completed")
            
            return stats
            
        except Exception as e:
            logger.error(f"Scan job {job_id} failed: {e}")
            await self.scan_repo.update_status(
                job_id, 'failed', error_message=str(e)
            )
            raise
    
    async def _resolve_telegram_link(self, url: str) -> Dict[str, Any]:
        """
        Resolve a Telegram link.
        
        Args:
            url: Telegram URL
            
        Returns:
            Resolution result
        """
        # Apply rate limiting
        await self.rate_limiter.wait_if_needed()
        
        # Try to parse the URL using TelegramParser
        parsed = TelegramParser.parse(url)
        
        if parsed.is_invite:
            # Resolve invite
            invite_hash = parsed.invite_hash
            if invite_hash:
                return await self.invite_resolver.resolve_invite_safe(url)
        
        elif parsed.username:
            # Resolve by username
            username = parsed.username
            return await self.entity_resolver.resolve_by_username(username)
        
        return {
            'status': 'invalid',
            'link_type': 'unknown',
            'error': 'Unable to resolve Telegram link'
        }

    async def _classify_url(self, url: str) -> Dict[str, Any]:
        """
        Classify a URL.
        
        Args:
            url: URL to classify
            
        Returns:
            Classification dictionary
        """
        # Check if Telegram URL
        if TelegramParser.is_valid_telegram_url(url):
            result = TelegramParser.classify(url)
            
            # Resolve Telegram link using the dedicated resolver
            resolved = await self._resolve_telegram_link(url)
            if resolved:
                result.update(resolved)
            
            return result
        
        # Check if WhatsApp URL
        elif WhatsAppParser.is_valid_whatsapp_url(url):
            return WhatsAppParser.classify(url)
        
        # Other URL
        return {
            'platform': 'other',
            'link_type': 'other',
            'status': 'excluded'
        }
    
    def _update_stats(self, stats: Dict[str, int], classification: Dict[str, Any]):
        """
        Update statistics based on classification.
        
        Args:
            stats: Statistics dictionary
            classification: Classification dictionary
        """
        platform = classification.get('platform', 'other')
        link_type = classification.get('link_type', 'unknown')
        status = classification.get('status', 'invalid')
        
        if platform == 'telegram':
            stats['telegram_count'] += 1
            if link_type == 'personal_account':
                stats['personal_count'] += 1
            elif link_type == 'bot':
                stats['bot_count'] += 1
            elif link_type == 'public_group':
                stats['group_count'] += 1
            elif link_type == 'public_channel':
                stats['channel_count'] += 1
            elif link_type == 'private_invite':
                stats['invite_count'] += 1
                
        elif platform == 'whatsapp':
            stats['whatsapp_count'] += 1
            if link_type == 'group':
                stats['group_count'] += 1
                
        elif platform == 'other':
            stats['other_count'] += 1
            
        if status == 'invalid':
            stats['invalid_count'] += 1