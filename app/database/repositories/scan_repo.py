"""
Scan job repository module.
"""

from typing import Optional, List
from datetime import datetime

from app.database.database import get_database
from app.database.models import ScanJob
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ScanRepository:
    """Repository for scan job operations."""
    
    async def create(
        self,
        telegram_user_id: int,
        source_id: int,
        scan_mode: str = 'recent',
        limit: int = 1000,
        start_message_id: Optional[int] = None,
        end_message_id: Optional[int] = None
    ) -> ScanJob:
        """
        Create a new scan job.
        
        Args:
            telegram_user_id: User ID
            source_id: Source ID
            scan_mode: Scan mode
            limit: Message limit
            start_message_id: Starting message ID
            end_message_id: Ending message ID
            
        Returns:
            ScanJob object
        """
        db = await get_database()
        now = datetime.now().isoformat()
        
        async with db.get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO scan_jobs 
                (telegram_user_id, source_id, status, scan_mode, 
                 start_message_id, end_message_id, messages_scanned, 
                 urls_found, urls_unique, created_at, started_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                telegram_user_id, source_id, 'queued', scan_mode,
                start_message_id, end_message_id, 0, 0, 0,
                now, now
            ))
            
            return ScanJob(
                id=cursor.lastrowid,
                telegram_user_id=telegram_user_id,
                source_id=source_id,
                status='queued',
                scan_mode=scan_mode,
                start_message_id=start_message_id,
                end_message_id=end_message_id,
                created_at=now,
                started_at=now
            )
    
    async def get_by_id(self, job_id: int) -> Optional[ScanJob]:
        """
        Get scan job by ID.
        
        Args:
            job_id: Job ID
            
        Returns:
            ScanJob object or None
        """
        db = await get_database()
        
        async with db.get_cursor() as cursor:
            cursor.execute(
                "SELECT * FROM scan_jobs WHERE id = ?",
                (job_id,)
            )
            row = cursor.fetchone()
            
            if row:
                return ScanJob(
                    id=row[0],
                    telegram_user_id=row[1],
                    source_id=row[2],
                    status=row[3],
                    scan_mode=row[4],
                    start_message_id=row[5],
                    end_message_id=row[6],
                    messages_scanned=row[7],
                    urls_found=row[8],
                    urls_unique=row[9],
                    completed_at=row[10],
                    error_message=row[11],
                    created_at=row[12],
                    started_at=row[13]
                )
            return None
    
    async def update_status(
        self,
        job_id: int,
        status: str,
        error_message: Optional[str] = None
    ) -> bool:
        """
        Update job status.
        
        Args:
            job_id: Job ID
            status: New status
            error_message: Error message if failed
            
        Returns:
            True if updated successfully
        """
        db = await get_database()
        
        async with db.get_cursor() as cursor:
            if status in ['completed', 'failed', 'cancelled']:
                now = datetime.now().isoformat()
                cursor.execute("""
                    UPDATE scan_jobs 
                    SET status = ?, completed_at = ?, error_message = ?
                    WHERE id = ?
                """, (status, now, error_message, job_id))
            else:
                cursor.execute("""
                    UPDATE scan_jobs 
                    SET status = ?, error_message = ?
                    WHERE id = ?
                """, (status, error_message, job_id))
            
            return cursor.rowcount > 0
    
    async def update_progress(
        self,
        job_id: int,
        messages_scanned: int,
        urls_found: int,
        urls_unique: int
    ) -> bool:
        """
        Update job progress.
        
        Args:
            job_id: Job ID
            messages_scanned: Number of messages scanned
            urls_found: Number of URLs found
            urls_unique: Number of unique URLs
            
        Returns:
            True if updated successfully
        """
        db = await get_database()
        
        async with db.get_cursor() as cursor:
            cursor.execute("""
                UPDATE scan_jobs 
                SET messages_scanned = ?, urls_found = ?, urls_unique = ?
                WHERE id = ?
            """, (messages_scanned, urls_found, urls_unique, job_id))
            
            return cursor.rowcount > 0
    
    async def update_completed_at(self, job_id: int) -> bool:
        """
        Update completed_at timestamp.
        
        Args:
            job_id: Job ID
            
        Returns:
            True if updated successfully
        """
        db = await get_database()
        now = datetime.now().isoformat()
        
        async with db.get_cursor() as cursor:
            cursor.execute("""
                UPDATE scan_jobs 
                SET completed_at = ?
                WHERE id = ?
            """, (now, job_id))
            
            return cursor.rowcount > 0
    
    async def get_by_user(self, telegram_user_id: int) -> List[ScanJob]:
        """
        Get all scan jobs for a user.
        
        Args:
            telegram_user_id: User ID
            
        Returns:
            List of ScanJob objects
        """
        db = await get_database()
        jobs = []
        
        async with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT * FROM scan_jobs 
                WHERE telegram_user_id = ?
                ORDER BY created_at DESC
            """, (telegram_user_id,))
            rows = cursor.fetchall()
            
            for row in rows:
                jobs.append(ScanJob(
                    id=row[0],
                    telegram_user_id=row[1],
                    source_id=row[2],
                    status=row[3],
                    scan_mode=row[4],
                    start_message_id=row[5],
                    end_message_id=row[6],
                    messages_scanned=row[7],
                    urls_found=row[8],
                    urls_unique=row[9],
                    completed_at=row[10],
                    error_message=row[11],
                    created_at=row[12],
                    started_at=row[13]
                ))
        
        return jobs