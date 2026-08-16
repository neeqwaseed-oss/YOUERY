"""
Integration tests for database operations.
"""

import pytest
import asyncio
from datetime import datetime

from app.database.database import Database, get_database
from app.database.repositories.user_repo import UserRepository
from app.database.repositories.source_repo import SourceRepository
from app.database.repositories.scan_repo import ScanRepository
from app.database.repositories.link_repo import LinkRepository
from app.database.repositories.result_repo import ResultRepository


@pytest.mark.asyncio
class TestDatabase:
    """Integration tests for database layer."""

    async def test_user_crud(self):
        """Test user CRUD operations."""
        repo = UserRepository()
        
        # Create user
        user = await repo.create_or_update(
            telegram_user_id=123456,
            username="testuser",
            first_name="Test User"
        )
        
        assert user.telegram_user_id == 123456
        assert user.username == "testuser"
        assert user.first_name == "Test User"
        
        # Update user
        updated = await repo.create_or_update(
            telegram_user_id=123456,
            username="newusername",
            first_name="New Name"
        )
        
        assert updated.username == "newusername"
        assert updated.first_name == "New Name"
        
        # Get user
        found = await repo.get_by_telegram_id(123456)
        assert found is not None
        assert found.telegram_user_id == 123456
        assert found.username == "newusername"

    async def test_source_crud(self):
        """Test source CRUD operations."""
        user_repo = UserRepository()
        source_repo = SourceRepository()
        
        # Create user first
        await user_repo.create_or_update(
            telegram_user_id=123456,
            username="testuser"
        )
        
        # Create source
        source = await source_repo.create(
            telegram_user_id=123456,
            telegram_chat_id=789012,
            title="Test Channel",
            username="testchannel",
            source_type="channel"
        )
        
        assert source.telegram_user_id == 123456
        assert source.telegram_chat_id == 789012
        assert source.title == "Test Channel"
        assert source.source_type == "channel"
        
        # Get source by ID
        found = await source_repo.get_by_id(source.id)
        assert found is not None
        assert found.title == "Test Channel"
        
        # Get sources by user
        sources = await source_repo.get_by_user(123456)
        assert len(sources) >= 1
        
        # Update activity
        updated = await source_repo.update_activity(source.id, False)
        assert updated is True
        
        # Verify update
        found = await source_repo.get_by_id(source.id)
        assert found.is_active is False

    async def test_scan_job_crud(self):
        """Test scan job CRUD operations."""
        user_repo = UserRepository()
        source_repo = SourceRepository()
        scan_repo = ScanRepository()
        
        # Create user and source
        await user_repo.create_or_update(
            telegram_user_id=123456,
            username="testuser"
        )
        
        source = await source_repo.create(
            telegram_user_id=123456,
            telegram_chat_id=789012,
            title="Test Channel",
            source_type="channel"
        )
        
        # Create scan job
        job = await scan_repo.create(
            telegram_user_id=123456,
            source_id=source.id,
            scan_mode="recent",
            limit=1000
        )
        
        assert job.telegram_user_id == 123456
        assert job.source_id == source.id
        assert job.scan_mode == "recent"
        assert job.status == "queued"
        
        # Update progress
        updated = await scan_repo.update_progress(
            job.id,
            messages_scanned=100,
            urls_found=10,
            urls_unique=8
        )
        
        assert updated is True
        
        # Verify progress
        found = await scan_repo.get_by_id(job.id)
        assert found.messages_scanned == 100
        assert found.urls_found == 10
        assert found.urls_unique == 8
        
        # Update status
        updated = await scan_repo.update_status(job.id, 'completed')
        assert updated is True
        
        # Get jobs by user
        jobs = await scan_repo.get_by_user(123456)
        assert len(jobs) >= 1
        assert jobs[0].status == 'completed'

    async def test_link_crud(self):
        """Test link CRUD operations."""
        user_repo = UserRepository()
        source_repo = SourceRepository()
        scan_repo = ScanRepository()
        link_repo = LinkRepository()
        
        # Setup
        await user_repo.create_or_update(
            telegram_user_id=123456,
            username="testuser"
        )
        
        source = await source_repo.create(
            telegram_user_id=123456,
            telegram_chat_id=789012,
            title="Test Channel",
            source_type="channel"
        )
        
        job = await scan_repo.create(
            telegram_user_id=123456,
            source_id=source.id,
            scan_mode="recent"
        )
        
        # Create link
        link = await link_repo.create(
            scan_job_id=job.id,
            source_id=source.id,
            message_id=1,
            original_url="https://t.me/test",
            normalized_url="https://t.me/test",
            platform="telegram",
            link_type="public_channel",
            status="valid",
            entity_id="123",
            entity_title="Test Channel",
            entity_username="testchannel"
        )
        
        assert link.scan_job_id == job.id
        assert link.platform == "telegram"
        assert link.link_type == "public_channel"
        assert link.status == "valid"
        
        # Get by ID
        found = await link_repo.get_by_id(link.id)
        assert found is not None
        assert found['original_url'] == "https://t.me/test"
        
        # Get by normalized URL
        found = await link_repo.get_by_normalized_url("https://t.me/test", job.id)
        assert found is not None
        assert found['platform'] == "telegram"
        
        # Get by job
        links = await link_repo.get_by_job(job.id)
        assert len(links) >= 1
        
        # Update link
        updated = await link_repo.update(
            link.id,
            status="excluded",
            link_type="personal_account"
        )
        assert updated is True
        
        # Verify update
        found = await link_repo.get_by_id(link.id)
        assert found['status'] == "excluded"
        assert found['link_type'] == "personal_account"

    async def test_statistics(self):
        """Test statistics operations."""
        user_repo = UserRepository()
        source_repo = SourceRepository()
        scan_repo = ScanRepository()
        result_repo = ResultRepository()
        
        # Setup
        await user_repo.create_or_update(
            telegram_user_id=123456,
            username="testuser"
        )
        
        source = await source_repo.create(
            telegram_user_id=123456,
            telegram_chat_id=789012,
            title="Test Channel",
            source_type="channel"
        )
        
        job = await scan_repo.create(
            telegram_user_id=123456,
            source_id=source.id,
            scan_mode="recent"
        )
        
        # Save statistics
        stats_data = {
            'telegram_count': 10,
            'whatsapp_count': 5,
            'group_count': 3,
            'channel_count': 2,
            'invite_count': 5,
            'personal_count': 2,
            'bot_count': 1,
            'duplicate_count': 4,
            'other_count': 0,
            'invalid_count': 0
        }
        
        saved = await result_repo.save_statistics(job.id, stats_data)
        assert saved is True
        
        # Get statistics
        stats = await result_repo.get_statistics(job.id)
        assert stats is not None
        assert stats['telegram_count'] == 10
        assert stats['whatsapp_count'] == 5
        assert stats['group_count'] == 3
        assert stats['channel_count'] == 2
        
        # Get job summary
        summary = await result_repo.get_job_summary(job.id)
        assert summary is not None
        assert summary['job']['id'] == job.id
        assert summary['statistics']['telegram_count'] == 10