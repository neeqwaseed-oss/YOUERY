"""
CSV exporter module - exports results as CSV file.
"""

import csv
import os
from typing import List, Dict, Any
from datetime import datetime

from app.database.repositories.link_repo import LinkRepository
from app.database.repositories.scan_repo import ScanRepository
from app.config import config
from app.utils.logger import get_logger

logger = get_logger(__name__)


class CSVExporter:
    """
    Exports scan results as a CSV file.
    """
    
    @classmethod
    async def export(cls, job_id: int) -> str:
        """
        Export scan results to a CSV file.
        
        Args:
            job_id: Scan job ID
            
        Returns:
            Path to the exported file
        """
        logger.info(f"Exporting job {job_id} as CSV")
        
        # Get all links for the job
        link_repo = LinkRepository()
        scan_repo = ScanRepository()
        
        job = await scan_repo.get_by_id(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")
        
        # Get all links
        all_links = await link_repo.get_by_job(
            scan_job_id=job_id,
            limit=10000,
            offset=0
        )
        
        # Define CSV columns
        columns = [
            'url', 'platform', 'link_type', 'status',
            'entity_title', 'entity_username', 'source_id', 'message_id',
            'created_at'
        ]
        
        # Write CSV file
        filename = f"results_job_{job_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        file_path = config.EXPORT_DIR / filename
        
        with open(file_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()
            
            for link in all_links:
                row = {
                    'url': link.get('original_url', ''),
                    'platform': link.get('platform', ''),
                    'link_type': link.get('link_type', ''),
                    'status': link.get('status', ''),
                    'entity_title': link.get('entity_title', ''),
                    'entity_username': link.get('entity_username', ''),
                    'source_id': link.get('source_id', ''),
                    'message_id': link.get('message_id', ''),
                    'created_at': link.get('created_at', '')
                }
                writer.writerow(row)
        
        logger.info(f"CSV export completed: {file_path}")
        return str(file_path)