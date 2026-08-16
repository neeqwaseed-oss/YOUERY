"""
Resolver worker module - handles entity resolution tasks.
"""

import asyncio
from typing import Dict, Any, Optional, List

from app.telegram.userbot_manager import UserbotManager
from app.telegram.entity_resolver import EntityResolver
from app.telegram.invite_resolver import InviteResolver
from app.database.repositories.link_repo import LinkRepository
from app.database.repositories.result_repo import ResultRepository
from app.utils.logger import get_logger
from app.utils.rate_limiter import RateLimiter

logger = get_logger(__name__)


class ResolverWorker:
    """
    Handles entity resolution for links in the database.
    """
    
    def __init__(self, userbot_manager: UserbotManager):
        self.userbot = userbot_manager
        self.entity_resolver = EntityResolver(userbot_manager)
        self.invite_resolver = InviteResolver(userbot_manager)
        self.link_repo = LinkRepository()
        self.result_repo = ResultRepository()
        self.rate_limiter = RateLimiter(
            max_per_second=2,
            max_per_minute=30
        )
    
    async def resolve_link(self, link_id: int) -> Dict[str, Any]:
        """
        Resolve a single link.
        
        Args:
            link_id: Link ID
            
        Returns:
            Resolution result
        """
        try:
            # Get link from database
            link = await self.link_repo.get_by_id(link_id)
            if not link:
                return {'status': 'error', 'error': 'Link not found'}
            
            # Check if already resolved
            if link.get('status') not in ['pending', 'queued']:
                return {'status': 'already_resolved'}
            
            # Resolve based on platform
            platform = link.get('platform')
            url = link.get('original_url')
            
            if platform == 'telegram':
                result = await self._resolve_telegram_link(url)
            elif platform == 'whatsapp':
                result = await self._resolve_whatsapp_link(url)
            else:
                result = {'status': 'excluded', 'link_type': 'other'}
            
            # Update link in database
            await self.link_repo.update(
                link_id,
                status=result.get('status', 'invalid'),
                link_type=result.get('link_type', 'unknown'),
                entity_id=result.get('entity_id'),
                entity_title=result.get('entity_title'),
                entity_username=result.get('entity_username')
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to resolve link {link_id}: {e}")
            return {'status': 'error', 'error': str(e)}
    
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
        
        # Try to parse the URL
        parsed = self.entity_resolver._parse_telegram_url(url)
        
        if parsed.get('is_invite'):
            # Resolve invite
            invite_hash = parsed.get('invite_hash')
            if invite_hash:
                return await self.invite_resolver.resolve_invite_safe(url)
            
        elif parsed.get('username'):
            # Resolve by username
            username = parsed.get('username')
            return await self.entity_resolver.resolve_by_username(username)
        
        return {
            'status': 'invalid',
            'link_type': 'unknown',
            'error': 'Unable to resolve Telegram link'
        }
    
    async def _resolve_whatsapp_link(self, url: str) -> Dict[str, Any]:
        """
        Resolve a WhatsApp link.
        
        Args:
            url: WhatsApp URL
            
        Returns:
            Resolution result
        """
        # WhatsApp links don't need resolution via Telegram API
        # Just parse and classify
        from app.extractor.whatsapp_parser import WhatsAppParser
        
        result = WhatsAppParser.classify(url)
        if result.get('is_valid'):
            result['status'] = 'valid'
        else:
            result['status'] = 'invalid'
        
        return result
    
    async def resolve_batch(self, link_ids: List[int]) -> List[Dict[str, Any]]:
        """
        Resolve a batch of links.
        
        Args:
            link_ids: List of link IDs
            
        Returns:
            List of resolution results
        """
        results = []
        for link_id in link_ids:
            result = await self.resolve_link(link_id)
            results.append(result)
            # Small delay between resolutions
            await asyncio.sleep(0.5)
        
        return results
    
    async def resolve_pending_links(self, job_id: int, batch_size: int = 50) -> int:
        """
        Resolve all pending links for a job.
        
        Args:
            job_id: Job ID
            batch_size: Number of links to process in each batch
            
        Returns:
            Number of resolved links
        """
        resolved_count = 0
        offset = 0
        
        while True:
            # Get pending links
            pending_links = await self.link_repo.get_by_status(
                job_id, 'pending', limit=batch_size, offset=offset
            )
            
            if not pending_links:
                break
            
            # Resolve batch
            link_ids = [link['id'] for link in pending_links]
            results = await self.resolve_batch(link_ids)
            
            resolved_count += len(results)
            offset += len(results)
            
            # Check if we've processed all
            if len(pending_links) < batch_size:
                break
        
        return resolved_count