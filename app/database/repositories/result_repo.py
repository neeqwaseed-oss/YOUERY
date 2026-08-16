"""
Result repository module.
"""

from typing import Dict, Any, Optional
from datetime import datetime

from app.database.database import get_database
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ResultRepository:
    """Repository for result and statistics operations."""
    
    async def save_statistics(self, job_id: int, stats: Dict[str, int]) -> bool:
        """
        Save scan statistics.
        
        Args:
            job_id: Job ID
            stats: Statistics dictionary
            
        Returns:
            True if saved successfully
        """
        db = await get_database()
        now = datetime.now().isoformat()
        
        async with db.get_cursor() as cursor:
            # Check if statistics already exist
            cursor.execute(
                "SELECT id FROM scan_statistics WHERE scan_job_id = ?",
                (job_id,)
            )
            row = cursor.fetchone()
            
            if row:
                # Update existing
                cursor.execute("""
                    UPDATE scan_statistics 
                    SET telegram_count = ?, whatsapp_count = ?,
                        group_count = ?, channel_count = ?,
                        invite_count = ?, personal_count = ?,
                        bot_count = ?, duplicate_count = ?,
                        other_count = ?, invalid_count = ?
                    WHERE scan_job_id = ?
                """, (
                    stats.get('telegram_count', 0),
                    stats.get('whatsapp_count', 0),
                    stats.get('group_count', 0),
                    stats.get('channel_count', 0),
                    stats.get('invite_count', 0),
                    stats.get('personal_count', 0),
                    stats.get('bot_count', 0),
                    stats.get('duplicate_count', 0),
                    stats.get('other_count', 0),
                    stats.get('invalid_count', 0),
                    job_id
                ))
            else:
                # Insert new
                cursor.execute("""
                    INSERT INTO scan_statistics 
                    (scan_job_id, telegram_count, whatsapp_count,
                     group_count, channel_count, invite_count,
                     personal_count, bot_count, duplicate_count,
                     other_count, invalid_count, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    job_id,
                    stats.get('telegram_count', 0),
                    stats.get('whatsapp_count', 0),
                    stats.get('group_count', 0),
                    stats.get('channel_count', 0),
                    stats.get('invite_count', 0),
                    stats.get('personal_count', 0),
                    stats.get('bot_count', 0),
                    stats.get('duplicate_count', 0),
                    stats.get('other_count', 0),
                    stats.get('invalid_count', 0),
                    now
                ))
            
            return True
    
    async def get_statistics(self, job_id: int) -> Optional[Dict[str, Any]]:
        """
        Get statistics for a job.
        
        Args:
            job_id: Job ID
            
        Returns:
            Statistics dictionary or None
        """
        db = await get_database()
        
        async with db.get_cursor() as cursor:
            cursor.execute(
                "SELECT * FROM scan_statistics WHERE scan_job_id = ?",
                (job_id,)
            )
            row = cursor.fetchone()
            
            if row:
                return {
                    'id': row[0],
                    'scan_job_id': row[1],
                    'telegram_count': row[2],
                    'whatsapp_count': row[3],
                    'group_count': row[4],
                    'channel_count': row[5],
                    'invite_count': row[6],
                    'personal_count': row[7],
                    'bot_count': row[8],
                    'duplicate_count': row[9],
                    'other_count': row[10],
                    'invalid_count': row[11],
                    'created_at': row[12]
                }
            return None
    
    async def get_job_summary(self, job_id: int) -> Optional[Dict[str, Any]]:
        """
        Get summary for a job including job info and statistics.
        
        Args:
            job_id: Job ID
            
        Returns:
            Summary dictionary or None
        """
        db = await get_database()
        
        async with db.get_cursor() as cursor:
            # Get job info
            cursor.execute("""
                SELECT j.*, s.title as source_title, s.username as source_username,
                       s.source_type
                FROM scan_jobs j
                LEFT JOIN sources s ON j.source_id = s.id
                WHERE j.id = ?
            """, (job_id,))
            job_row = cursor.fetchone()
            
            if not job_row:
                return None
            
            # Get statistics
            stats = await self.get_statistics(job_id)
            
            # Count links by type
            cursor.execute("""
                SELECT platform, link_type, status, COUNT(*) as count
                FROM extracted_links
                WHERE scan_job_id = ?
                GROUP BY platform, link_type, status
            """, (job_id,))
            links_rows = cursor.fetchall()
            
            links_by_type = {}
            for row in links_rows:
                key = f"{row[0]}_{row[1]}_{row[2]}"
                links_by_type[key] = row[3]
            
            return {
                'job': {
                    'id': job_row[0],
                    'status': job_row[3],
                    'scan_mode': job_row[4],
                    'messages_scanned': job_row[7],
                    'urls_found': job_row[8],
                    'urls_unique': job_row[9],
                    'created_at': job_row[12],
                    'started_at': job_row[13],
                    'completed_at': job_row[10]
                },
                'source': {
                    'id': job_row[2],
                    'title': job_row[14],
                    'username': job_row[15],
                    'type': job_row[16]
                },
                'statistics': stats,
                'links_by_type': links_by_type
            }