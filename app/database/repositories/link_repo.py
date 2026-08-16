"""
Link repository module.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from app.database.database import get_database
from app.database.models import ExtractedLink
from app.utils.logger import get_logger

logger = get_logger(__name__)


class LinkRepository:
    """Repository for link operations."""
    
    async def create(
        self,
        scan_job_id: int,
        source_id: int,
        message_id: int,
        original_url: str,
        normalized_url: str,
        platform: str,
        link_type: str,
        status: str,
        entity_id: Optional[str] = None,
        entity_title: Optional[str] = None,
        entity_username: Optional[str] = None
    ) -> ExtractedLink:
        """
        Create a new extracted link.
        
        Args:
            scan_job_id: Job ID
            source_id: Source ID
            message_id: Message ID
            original_url: Original URL
            normalized_url: Normalized URL
            platform: Platform (telegram, whatsapp, other)
            link_type: Link type
            status: Status
            entity_id: Entity ID
            entity_title: Entity title
            entity_username: Entity username
            
        Returns:
            ExtractedLink object
        """
        db = await get_database()
        now = datetime.now().isoformat()
        
        async with db.get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO extracted_links 
                (scan_job_id, source_id, message_id, original_url, normalized_url,
                 platform, link_type, status, entity_id, entity_title, 
                 entity_username, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                scan_job_id, source_id, message_id, original_url, normalized_url,
                platform, link_type, status, entity_id, entity_title,
                entity_username, now
            ))
            
            return ExtractedLink(
                id=cursor.lastrowid,
                scan_job_id=scan_job_id,
                source_id=source_id,
                message_id=message_id,
                original_url=original_url,
                normalized_url=normalized_url,
                platform=platform,
                link_type=link_type,
                status=status,
                entity_id=entity_id,
                entity_title=entity_title,
                entity_username=entity_username,
                created_at=now
            )
    
    async def get_by_id(self, link_id: int) -> Optional[Dict[str, Any]]:
        """
        Get link by ID.
        
        Args:
            link_id: Link ID
            
        Returns:
            Link dictionary or None
        """
        db = await get_database()
        
        async with db.get_cursor() as cursor:
            cursor.execute(
                "SELECT * FROM extracted_links WHERE id = ?",
                (link_id,)
            )
            row = cursor.fetchone()
            
            if row:
                return {
                    'id': row[0],
                    'scan_job_id': row[1],
                    'source_id': row[2],
                    'message_id': row[3],
                    'original_url': row[4],
                    'normalized_url': row[5],
                    'platform': row[6],
                    'link_type': row[7],
                    'status': row[8],
                    'entity_id': row[9],
                    'entity_title': row[10],
                    'entity_username': row[11],
                    'created_at': row[12]
                }
            return None
    
    async def get_by_normalized_url(
        self,
        normalized_url: str,
        scan_job_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Get link by normalized URL for a specific job.
        
        Args:
            normalized_url: Normalized URL
            scan_job_id: Job ID
            
        Returns:
            Link dictionary or None
        """
        db = await get_database()
        
        async with db.get_cursor() as cursor:
            cursor.execute(
                "SELECT * FROM extracted_links WHERE normalized_url = ? AND scan_job_id = ?",
                (normalized_url, scan_job_id)
            )
            row = cursor.fetchone()
            
            if row:
                return {
                    'id': row[0],
                    'scan_job_id': row[1],
                    'source_id': row[2],
                    'message_id': row[3],
                    'original_url': row[4],
                    'normalized_url': row[5],
                    'platform': row[6],
                    'link_type': row[7],
                    'status': row[8],
                    'entity_id': row[9],
                    'entity_title': row[10],
                    'entity_username': row[11],
                    'created_at': row[12]
                }
            return None
    
    async def get_by_status(
        self,
        scan_job_id: int,
        status: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get links by status for a job.
        
        Args:
            scan_job_id: Job ID
            status: Status filter
            limit: Maximum number of links
            offset: Offset for pagination
            
        Returns:
            List of link dictionaries
        """
        db = await get_database()
        links = []
        
        async with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT * FROM extracted_links 
                WHERE scan_job_id = ? AND status = ?
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """, (scan_job_id, status, limit, offset))
            rows = cursor.fetchall()
            
            for row in rows:
                links.append({
                    'id': row[0],
                    'scan_job_id': row[1],
                    'source_id': row[2],
                    'message_id': row[3],
                    'original_url': row[4],
                    'normalized_url': row[5],
                    'platform': row[6],
                    'link_type': row[7],
                    'status': row[8],
                    'entity_id': row[9],
                    'entity_title': row[10],
                    'entity_username': row[11],
                    'created_at': row[12]
                })
        
        return links
    
    async def update(
        self,
        link_id: int,
        status: Optional[str] = None,
        link_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        entity_title: Optional[str] = None,
        entity_username: Optional[str] = None
    ) -> bool:
        """
        Update a link.
        
        Args:
            link_id: Link ID
            status: New status
            link_type: New link type
            entity_id: New entity ID
            entity_title: New entity title
            entity_username: New entity username
            
        Returns:
            True if updated successfully
        """
        db = await get_database()
        
        updates = []
        params = []
        
        if status is not None:
            updates.append("status = ?")
            params.append(status)
        if link_type is not None:
            updates.append("link_type = ?")
            params.append(link_type)
        if entity_id is not None:
            updates.append("entity_id = ?")
            params.append(entity_id)
        if entity_title is not None:
            updates.append("entity_title = ?")
            params.append(entity_title)
        if entity_username is not None:
            updates.append("entity_username = ?")
            params.append(entity_username)
        
        if not updates:
            return False
        
        query = f"UPDATE extracted_links SET {', '.join(updates)} WHERE id = ?"
        params.append(link_id)
        
        async with db.get_cursor() as cursor:
            cursor.execute(query, tuple(params))
            return cursor.rowcount > 0
    
    async def get_by_job(
        self,
        scan_job_id: int,
        platform: Optional[str] = None,
        link_type: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get links by job with filters.
        
        Args:
            scan_job_id: Job ID
            platform: Platform filter
            link_type: Link type filter
            status: Status filter
            limit: Maximum number of links
            offset: Offset for pagination
            
        Returns:
            List of link dictionaries
        """
        db = await get_database()
        links = []
        
        query = "SELECT * FROM extracted_links WHERE scan_job_id = ?"
        params = [scan_job_id]
        
        if platform:
            query += " AND platform = ?"
            params.append(platform)
        if link_type:
            query += " AND link_type = ?"
            params.append(link_type)
        if status:
            query += " AND status = ?"
            params.append(status)
        
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        async with db.get_cursor() as cursor:
            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()
            
            for row in rows:
                links.append({
                    'id': row[0],
                    'scan_job_id': row[1],
                    'source_id': row[2],
                    'message_id': row[3],
                    'original_url': row[4],
                    'normalized_url': row[5],
                    'platform': row[6],
                    'link_type': row[7],
                    'status': row[8],
                    'entity_id': row[9],
                    'entity_title': row[10],
                    'entity_username': row[11],
                    'created_at': row[12]
                })
        
        return links
    
    async def count_by_job(
        self,
        scan_job_id: int,
        platform: Optional[str] = None,
        link_type: Optional[str] = None,
        status: Optional[str] = None
    ) -> int:
        """
        Count links by job with filters.
        
        Args:
            scan_job_id: Job ID
            platform: Platform filter
            link_type: Link type filter
            status: Status filter
            
        Returns:
            Count of links
        """
        db = await get_database()
        
        query = "SELECT COUNT(*) FROM extracted_links WHERE scan_job_id = ?"
        params = [scan_job_id]
        
        if platform:
            query += " AND platform = ?"
            params.append(platform)
        if link_type:
            query += " AND link_type = ?"
            params.append(link_type)
        if status:
            query += " AND status = ?"
            params.append(status)
        
        async with db.get_cursor() as cursor:
            cursor.execute(query, tuple(params))
            row = cursor.fetchone()
            return row[0] if row else 0