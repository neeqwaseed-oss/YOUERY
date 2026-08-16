"""
Integration tests for scan pipeline.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch

from app.workers.scan_worker import ScanWorker
from app.telegram.userbot_manager import UserbotManager
from app.database.repositories.scan_repo import ScanRepository
from app.database.repositories.source_repo import SourceRepository
from app.database.repositories.link_repo import LinkRepository


@pytest.mark.asyncio
class TestScanPipeline:
    """Integration tests for scan pipeline."""

    @patch('app.telegram.userbot_manager.UserbotManager.initialize')
    @patch('app.telegram.message_reader.MessageReader.read_messages')
    async def test_scan_pipeline_basic(self, mock_read_messages, mock_init):
        """Test basic scan pipeline."""
        # Mock userbot initialization
        mock_init.return_value = True
        
        # Mock message reader
        async def mock_read_generator(*args, **kwargs):
            # Return a batch of test messages
            yield [
                {
                    'id': 1,
                    'text': 'https://t.me/group1',
                    'entities': None
                },
                {
                    'id': 2,
                    'text': 'https://t.me/user1',
                    'entities': None
                },
                {
                    'id': 3,
                    'text': 'https://t.me/bot1',
                    'entities': None
                },
                {
                    'id': 4,
                    'text': 'https://chat.whatsapp.com/ABC123',
                    'entities': None
                },
                {
                    'id': 5,
                    'text': 'https://example.com',
                    'entities': None
                },
                {
                    'id': 6,
                    'text': 'https://t.me/group1',
                    'entities': None
                }
            ]
        
        mock_read_messages.side_effect = mock_read_generator
        
        # Setup
        userbot = UserbotManager()
        scan_worker = ScanWorker(userbot)
        
        # Create job
        scan_repo = ScanRepository()
        job = await scan_repo.create(
            telegram_user_id=123456,
            source_id=789012,
            scan_mode='recent',
            limit=100
        )
        
        # Mock progress callback
        progress_callback = AsyncMock()
        
        # Run scan
        stats = await scan_worker.run_scan(
            job_id=job.id,
            source_id=789012,
            user_id=123456,
            scan_mode='recent',
            limit=100,
            progress_callback=progress_callback
        )
        
        # Verify statistics
        assert stats['messages_scanned'] >= 6
        assert stats['urls_found'] >= 6
        
        # Check links in database
        link_repo = LinkRepository()
        links = await link_repo.get_by_job(job.id)
        
        # Should have deduplicated links
        # group1, user1, bot1, whatsapp, example = 5 unique
        # group1 appears twice but should be deduplicated
        assert len(links) >= 5
        
        # Verify link types
        telegram_links = [l for l in links if l['platform'] == 'telegram']
        whatsapp_links = [l for l in links if l['platform'] == 'whatsapp']
        other_links = [l for l in links if l['platform'] == 'other']
        
        assert len(telegram_links) >= 3  # group1, user1, bot1
        assert len(whatsapp_links) >= 1  # WhatsApp
        assert len(other_links) >= 1  # example.com

    @patch('app.telegram.userbot_manager.UserbotManager.initialize')
    @patch('app.telegram.message_reader.MessageReader.read_messages')
    async def test_scan_pipeline_with_cancellation(self, mock_read_messages, mock_init):
        """Test scan pipeline with cancellation."""
        # Mock userbot initialization
        mock_init.return_value = True
        
        # Mock message reader to yield multiple batches
        async def mock_read_generator(*args, **kwargs):
            # Yield first batch
            yield [
                {'id': 1, 'text': 'https://t.me/test1', 'entities': None},
                {'id': 2, 'text': 'https://t.me/test2', 'entities': None}
            ]
            # Yield second batch
            yield [
                {'id': 3, 'text': 'https://t.me/test3', 'entities': None},
                {'id': 4, 'text': 'https://t.me/test4', 'entities': None}
            ]
        
        mock_read_messages.side_effect = mock_read_generator
        
        # Setup
        userbot = UserbotManager()
        scan_worker = ScanWorker(userbot)
        
        # Create job
        scan_repo = ScanRepository()
        job = await scan_repo.create(
            telegram_user_id=123456,
            source_id=789012,
            scan_mode='recent',
            limit=100
        )
        
        # Cancel after first batch
        async def cancel_after_first():
            await asyncio.sleep(0.1)
            scan_worker.cancel()
        
        asyncio.create_task(cancel_after_first())
        
        # Run scan
        stats = await scan_worker.run_scan(
            job_id=job.id,
            source_id=789012,
            user_id=123456,
            scan_mode='recent',
            limit=100
        )
        
        # Verify cancellation
        assert stats['messages_scanned'] >= 2  # At least first batch
        
        # Check job status
        job_updated = await scan_repo.get_by_id(job.id)
        assert job_updated.status == 'cancelled'

    @patch('app.telegram.userbot_manager.UserbotManager.initialize')
    @patch('app.telegram.message_reader.MessageReader.read_messages')
    async def test_scan_pipeline_entity_resolution(self, mock_read_messages, mock_init):
        """Test scan pipeline with entity resolution."""
        # Mock userbot initialization
        mock_init.return_value = True
        
        # Mock message reader with messages that need entity resolution
        async def mock_read_generator(*args, **kwargs):
            yield [
                {
                    'id': 1,
                    'text': 'https://t.me/testchannel',
                    'entities': None
                },
                {
                    'id': 2,
                    'text': 'https://t.me/testgroup',
                    'entities': None
                },
                {
                    'id': 3,
                    'text': 'https://t.me/+ABC123',
                    'entities': None
                }
            ]
        
        mock_read_messages.side_effect = mock_read_generator
        
        # Setup
        userbot = UserbotManager()
        scan_worker = ScanWorker(userbot)
        
        # Create job
        scan_repo = ScanRepository()
        job = await scan_repo.create(
            telegram_user_id=123456,
            source_id=789012,
            scan_mode='recent',
            limit=100
        )
        
        # Mock entity resolver
        with patch('app.workers.scan_worker.EntityResolver') as MockEntityResolver:
            mock_resolver = Mock()
            mock_resolver.resolve_by_username = AsyncMock()
            mock_resolver.resolve_by_username.side_effect = [
                {
                    'status': 'valid',
                    'link_type': 'public_channel',
                    'entity_id': '123',
                    'entity_title': 'Test Channel',
                    'entity_username': 'testchannel'
                },
                {
                    'status': 'valid',
                    'link_type': 'public_group',
                    'entity_id': '456',
                    'entity_title': 'Test Group',
                    'entity_username': 'testgroup'
                }
            ]
            
            mock_resolver.resolve_invite_hash = AsyncMock()
            mock_resolver.resolve_invite_hash.return_value = {
                'status': 'valid',
                'link_type': 'private_invite',
                'entity_title': 'Test Invite',
                'is_channel': False,
                'is_megagroup': True
            }
            
            MockEntityResolver.return_value = mock_resolver
            
            # Run scan
            stats = await scan_worker.run_scan(
                job_id=job.id,
                source_id=789012,
                user_id=123456,
                scan_mode='recent',
                limit=100
            )
            
            # Verify entity resolution was called
            assert mock_resolver.resolve_by_username.call_count >= 2
            assert mock_resolver.resolve_invite_hash.call_count >= 1
            
            # Verify links in database
            link_repo = LinkRepository()
            links = await link_repo.get_by_job(job.id)
            
            # Should have entity data
            channel_links = [l for l in links if l['link_type'] == 'public_channel']
            group_links = [l for l in links if l['link_type'] == 'public_group']
            invite_links = [l for l in links if l['link_type'] == 'private_invite']
            
            assert len(channel_links) >= 1
            assert len(group_links) >= 1
            assert len(invite_links) >= 1