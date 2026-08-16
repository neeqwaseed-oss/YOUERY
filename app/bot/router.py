"""
Main router for the bot.
"""

from aiogram import Router

# Import all handlers
from app.bot.handlers import start, sources, scan, results, export, settings

# Create main router
router = Router()

# Include all sub-routers
router.include_router(start.router)
router.include_router(sources.router)
router.include_router(scan.router)
router.include_router(results.router)
router.include_router(export.router)
router.include_router(settings.router)