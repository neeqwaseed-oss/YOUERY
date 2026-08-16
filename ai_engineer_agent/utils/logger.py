# ai_engineer_agent/utils/logger.py
import logging
import sys
from pathlib import Path
from config import LOG_PATH


def setup_logging(level: str = "INFO"):
    """إعداد نظام السجل"""
    
    # إنشاء مجلد السجل
    LOG_PATH.mkdir(exist_ok=True)
    
    # إعداد التنسيق
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # إعداد المعالج (Console)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # إعداد المعالج (File)
    file_handler = logging.FileHandler(LOG_PATH / "agent.log", encoding='utf-8')
    file_handler.setFormatter(formatter)
    
    # تكوين الجذر
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    logging.info(f"📝 Logging configured with level: {level}")