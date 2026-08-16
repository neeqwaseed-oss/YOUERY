"""
TXT exporter module - exports results as plain text file.
"""

import os
from typing import List, Dict, Any
from datetime import datetime

from app.database.repositories.link_repo import LinkRepository
from app.database.repositories.result_repo import ResultRepository
from app.database.repositories.scan_repo import ScanRepository
from app.config import config
from app.utils.logger import get_logger


logger = get_logger(__name__)


class TXTExporter:
    """
    Exports scan results as a formatted text file.
    """

    @classmethod
    async def export(cls, job_id: int) -> str:
        """
        Export scan results to a TXT file.

        Args:
            job_id: Scan job ID

        Returns:
            Path to the exported file
        """
        logger.info(f"Exporting job {job_id} as TXT")

        # Get job and statistics
        scan_repo = ScanRepository()
        result_repo = ResultRepository()
        link_repo = LinkRepository()

        job = await scan_repo.get_by_id(job_id)
        stats = await result_repo.get_statistics(job_id)

        if not job:
            raise ValueError(f"Job {job_id} not found")

        # Get links by category
        telegram_groups = await link_repo.get_by_job(
            scan_job_id=job_id,
            platform='telegram',
            link_type='public_group',
            status='valid',
            limit=10000,
            offset=0
        )

        telegram_channels = await link_repo.get_by_job(
            scan_job_id=job_id,
            platform='telegram',
            link_type='public_channel',
            status='valid',
            limit=10000,
            offset=0
        )

        telegram_invites = await link_repo.get_by_job(
            scan_job_id=job_id,
            platform='telegram',
            link_type='private_invite',
            status='valid',
            limit=10000,
            offset=0
        )

        whatsapp_groups = await link_repo.get_by_job(
            scan_job_id=job_id,
            platform='whatsapp',
            link_type='group',
            status='valid',
            limit=10000,
            offset=0
        )

        # Build content
        lines = []
        lines.append("=" * 60)
        lines.append("TELEGRAM & WHATSAPP LINK EXTRACTOR - RESULTS")
        lines.append("=" * 60)
        lines.append(f"Job ID: {job_id}")
        lines.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Status: {job.status.upper()}")
        lines.append("=" * 60)
        lines.append("")

        # Statistics
        if stats:
            lines.append("STATISTICS:")
            lines.append(f"  Messages Scanned: {job.messages_scanned}")
            lines.append(f"  URLs Found: {job.urls_found}")
            lines.append(f"  Unique URLs: {job.urls_unique}")
            lines.append("")

            lines.append(f"  Telegram Links: {stats.get('telegram_count', 0)}")
            lines.append(f"  WhatsApp Links: {stats.get('whatsapp_count', 0)}")
            lines.append("")

            lines.append(f"  Groups: {stats.get('group_count', 0)}")
            lines.append(f"  Channels: {stats.get('channel_count', 0)}")
            lines.append(f"  Invites: {stats.get('invite_count', 0)}")
            lines.append("")

            lines.append(
                f"  Excluded Personal: {stats.get('personal_count', 0)}"
            )
            lines.append(
                f"  Excluded Bots: {stats.get('bot_count', 0)}"
            )
            lines.append(
                f"  Duplicates: {stats.get('duplicate_count', 0)}"
            )
            lines.append(
                f"  Other Links: {stats.get('other_count', 0)}"
            )
            lines.append("")

        lines.append("=" * 60)
        lines.append("")

        # Telegram Groups
        if telegram_groups:
            lines.append("TELEGRAM GROUPS:")
            lines.append("-" * 40)

            for i, link in enumerate(telegram_groups, 1):
                url = link.get('original_url', 'N/A')
                title = link.get('entity_title', '')
                username = link.get('entity_username', '')

                lines.append(f"{i}. {url}")

                if title:
                    lines.append(f"   Title: {title}")

                if username:
                    lines.append(f"   Username: @{username}")

                lines.append("")

            lines.append("")

        # Telegram Channels
        if telegram_channels:
            lines.append("TELEGRAM CHANNELS:")
            lines.append("-" * 40)

            for i, link in enumerate(telegram_channels, 1):
                url = link.get('original_url', 'N/A')
                title = link.get('entity_title', '')
                username = link.get('entity_username', '')

                lines.append(f"{i}. {url}")

                if title:
                    lines.append(f"   Title: {title}")

                if username:
                    lines.append(f"   Username: @{username}")

                lines.append("")

            lines.append("")

        # Telegram Invites
        if telegram_invites:
            lines.append("TELEGRAM INVITES:")
            lines.append("-" * 40)

            for i, link in enumerate(telegram_invites, 1):
                url = link.get('original_url', 'N/A')
                title = link.get('entity_title', '')

                lines.append(f"{i}. {url}")

                if title:
                    lines.append(f"   Title: {title}")

                lines.append("")

            lines.append("")

        # WhatsApp Groups
        if whatsapp_groups:
            lines.append("WHATSAPP GROUPS:")
            lines.append("-" * 40)

            for i, link in enumerate(whatsapp_groups, 1):
                url = link.get('original_url', 'N/A')
                lines.append(f"{i}. {url}")

            lines.append("")

        # Write to file
        filename = (
            f"results_job_{job_id}_"
            f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )

        # Use TEMP_DIR instead of EXPORT_DIR
        file_path = config.TEMP_DIR / filename

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

        logger.info(f"TXT export completed: {file_path}")

        return str(file_path)