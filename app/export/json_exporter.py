"""
JSON exporter module - exports results as JSON file.
"""

import json
import os
from typing import Dict, Any
from datetime import datetime

from app.database.repositories.link_repo import LinkRepository
from app.database.repositories.result_repo import ResultRepository
from app.database.repositories.scan_repo import ScanRepository
from app.config import config
from app.utils.logger import get_logger

logger = get_logger(__name__)


class JSONExporter:
    """
    Exports scan results as a JSON file.
    """
    
    @classmethod
    async def export(cls, job_id: int) -> str:
        """
        Export scan results to a JSON file.
        
        Args:
            job_id: Scan job ID
            
        Returns:
            Path to the exported file
        """
        logger.info(f"Exporting job {job_id} as JSON")
        
        # Get job info and statistics
        scan_repo = ScanRepository()
        result_repo = ResultRepository()
        link_repo = LinkRepository()
        
        job = await scan_repo.get_by_id(job_id)
        stats = await result_repo.get_statistics(job_id)
        
        if not job:
            raise ValueError(f"Job {job_id} not found")
        
        # Get all links
        all_links = await link_repo.get_by_job(
            scan_job_id=job_id,
            limit=10000,
            offset=0
        )
        
        # Build JSON structure
        data = {
            'job_id': job_id,
            'status': job.status,
            'scan_mode': job.scan_mode,
            'created_at': job.created_at,
            'completed_at': job.completed_at,
            'statistics': stats or {},
            'links': all_links
        }
        
        # Write JSON file
        filename = f"results_job_{job_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        file_path = config.EXPORT_DIR / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"JSON export completed: {file_path}")
        return str(file_path)