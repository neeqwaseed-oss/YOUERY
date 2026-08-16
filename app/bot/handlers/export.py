"""
Export handlers - handle export of results.
"""

import os
from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton, InlineKeyboardMarkup

from app.database.repositories.link_repo import LinkRepository
from app.database.repositories.result_repo import ResultRepository
from app.database.repositories.scan_repo import ScanRepository
from app.export.txt_exporter import TXTExporter
from app.export.csv_exporter import CSVExporter
from app.export.json_exporter import JSONExporter
from app.export.xlsx_exporter import XLSXExporter
from app.config import config
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = Router()


@router.callback_query(F.data.startswith("export:menu:"))
async def export_menu(callback: CallbackQuery):
    """Show export menu for a job."""
    await callback.answer()
    
    job_id = int(callback.data.split(":")[2])
    
    # Get job info
    scan_repo = ScanRepository()
    job = await scan_repo.get_by_id(job_id)
    
    if not job:
        await callback.message.edit_text(
            "❌ <b>Job not found</b>\n\n"
            "The scan job no longer exists.",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="⬅️ Back", callback_data="menu:back")]
                ]
            ),
            parse_mode="HTML"
        )
        return
    
    # Build export menu
    text = f"📤 <b>Export Results - Job #{job_id}</b>\n\n"
    text += f"📊 Links found: {job.urls_found}\n"
    text += f"🟢 Unique links: {job.urls_unique}\n\n"
    text += "Choose export format:"
    
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="📄 TXT", callback_data=f"export:txt:{job_id}"))
    builder.add(InlineKeyboardButton(text="📊 CSV", callback_data=f"export:csv:{job_id}"))
    builder.add(InlineKeyboardButton(text="📝 JSON", callback_data=f"export:json:{job_id}"))
    builder.add(InlineKeyboardButton(text="📊 XLSX", callback_data=f"export:xlsx:{job_id}"))
    builder.add(InlineKeyboardButton(text="⬅️ Back to Results", callback_data=f"result:latest:{job_id}"))
    builder.add(InlineKeyboardButton(text="⬅️ Back to Menu", callback_data="menu:back"))
    builder.adjust(1)
    
    await callback.message.edit_text(
        text,
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("export:txt:"))
async def export_txt(callback: CallbackQuery):
    """Export results as TXT."""
    await callback.answer("📄 Generating TXT export...")
    
    job_id = int(callback.data.split(":")[2])
    
    try:
        # Generate export
        file_path = await TXTExporter.export(job_id)
        
        # Send file
        await callback.message.answer_document(
            document=FSInputFile(file_path),
            caption="📄 <b>TXT Export</b>\n\n"
                    "Your results have been exported as a text file.",
            parse_mode="HTML"
        )
        
        # Clean up
        if os.path.exists(file_path):
            os.remove(file_path)
            
    except Exception as e:
        logger.error(f"TXT export failed: {e}")
        await callback.message.answer(
            f"❌ <b>Export Failed</b>\n\n"
            f"Error: {str(e)}",
            parse_mode="HTML"
        )


@router.callback_query(F.data.startswith("export:csv:"))
async def export_csv(callback: CallbackQuery):
    """Export results as CSV."""
    await callback.answer("📊 Generating CSV export...")
    
    job_id = int(callback.data.split(":")[2])
    
    try:
        # Generate export
        file_path = await CSVExporter.export(job_id)
        
        # Send file
        await callback.message.answer_document(
            document=FSInputFile(file_path),
            caption="📊 <b>CSV Export</b>\n\n"
                    "Your results have been exported as a CSV file.",
            parse_mode="HTML"
        )
        
        # Clean up
        if os.path.exists(file_path):
            os.remove(file_path)
            
    except Exception as e:
        logger.error(f"CSV export failed: {e}")
        await callback.message.answer(
            f"❌ <b>Export Failed</b>\n\n"
            f"Error: {str(e)}",
            parse_mode="HTML"
        )


@router.callback_query(F.data.startswith("export:json:"))
async def export_json(callback: CallbackQuery):
    """Export results as JSON."""
    await callback.answer("📝 Generating JSON export...")
    
    job_id = int(callback.data.split(":")[2])
    
    try:
        # Generate export
        file_path = await JSONExporter.export(job_id)
        
        # Send file
        await callback.message.answer_document(
            document=FSInputFile(file_path),
            caption="📝 <b>JSON Export</b>\n\n"
                    "Your results have been exported as a JSON file.",
            parse_mode="HTML"
        )
        
        # Clean up
        if os.path.exists(file_path):
            os.remove(file_path)
            
    except Exception as e:
        logger.error(f"JSON export failed: {e}")
        await callback.message.answer(
            f"❌ <b>Export Failed</b>\n\n"
            f"Error: {str(e)}",
            parse_mode="HTML"
        )


@router.callback_query(F.data.startswith("export:xlsx:"))
async def export_xlsx(callback: CallbackQuery):
    """Export results as XLSX."""
    await callback.answer("📊 Generating XLSX export...")
    
    job_id = int(callback.data.split(":")[2])
    
    try:
        # Generate export
        file_path = await XLSXExporter.export(job_id)
        
        # Send file
        await callback.message.answer_document(
            document=FSInputFile(file_path),
            caption="📊 <b>XLSX Export</b>\n\n"
                    "Your results have been exported as an Excel file.",
            parse_mode="HTML"
        )
        
        # Clean up
        if os.path.exists(file_path):
            os.remove(file_path)
            
    except Exception as e:
        logger.error(f"XLSX export failed: {e}")
        await callback.message.answer(
            f"❌ <b>Export Failed</b>\n\n"
            f"Error: {str(e)}",
            parse_mode="HTML"
        )


@router.callback_query(F.data.startswith("export:back"))
async def export_back(callback: CallbackQuery):
    """Go back from export menu."""
    await callback.answer()
    await callback.message.edit_text(
        "🔗 <b>Link Extractor</b>\n\n"
        "Choose an operation:",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🔍 استخراج الروابط", callback_data="menu:scan")],
                [InlineKeyboardButton(text="📂 المصادر", callback_data="menu:sources")],
                [InlineKeyboardButton(text="📊 النتائج", callback_data="menu:results")],
                [InlineKeyboardButton(text="📤 التصدير", callback_data="menu:exports")],
                [InlineKeyboardButton(text="⚙️ الإعدادات", callback_data="menu:settings")],
            ]
        ),
        parse_mode="HTML"
    )