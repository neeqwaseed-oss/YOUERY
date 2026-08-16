# ai_engineer_agent/memory/project_memory.py
import json
import os
from datetime import datetime
from pathlib import Path
from config import MEMORY_PATH


class ProjectMemory:
    """إدارة ذاكرة المشروع"""
    
    def __init__(self):
        self.memory_file = MEMORY_PATH / "project_memory.json"
        self.errors_file = MEMORY_PATH / "errors_log.json"
        self.tasks_file = MEMORY_PATH / "tasks_log.json"
        self._load_memory()
    
    def _load_memory(self):
        """تحميل الذاكرة من الملف"""
        if self.memory_file.exists():
            with open(self.memory_file, 'r') as f:
                self.memory = json.load(f)
        else:
            self.memory = self._default_memory()
            self._save_memory()
        
        if self.errors_file.exists():
            with open(self.errors_file, 'r') as f:
                self.errors = json.load(f)
        else:
            self.errors = {"errors": []}
            self._save_errors()
        
        if self.tasks_file.exists():
            with open(self.tasks_file, 'r') as f:
                self.tasks = json.load(f)
        else:
            self.tasks = {"tasks": []}
            self._save_tasks()
    
    def _default_memory(self) -> dict:
        """ذاكرة افتراضية للمشروع"""
        return {
            "project_name": "Telegram WhatsApp Link Extractor",
            "last_updated": datetime.now().isoformat(),
            "architecture": {
                "framework": "aiogram 3.x, Telethon",
                "database": "SQLite",
                "structure": "modular",
                "key_files": {
                    "main": "app/main.py",
                    "config": "app/config.py",
                    "router": "app/bot/router.py",
                    "database": "app/database/database.py"
                }
            },
            "features": {
                "url_extraction": True,
                "telegram_parser": True,
                "whatsapp_parser": True,
                "export": ["txt", "csv", "json", "xlsx"]
            },
            "known_issues": [],
            "last_health_check": "🟢 Healthy",
            "last_bot_status": "running"
        }
    
    def _save_memory(self):
        """حفظ الذاكرة إلى ملف"""
        self.memory["last_updated"] = datetime.now().isoformat()
        with open(self.memory_file, 'w') as f:
            json.dump(self.memory, f, indent=2)
    
    def _save_errors(self):
        """حفظ سجل الأخطاء"""
        with open(self.errors_file, 'w') as f:
            json.dump(self.errors, f, indent=2)
    
    def _save_tasks(self):
        """حفظ سجل المهام"""
        with open(self.tasks_file, 'w') as f:
            json.dump(self.tasks, f, indent=2)
    
    def get_state(self) -> dict:
        """الحصول على حالة المشروع الحالية"""
        return self.memory
    
    def update_state(self, updates: dict):
        """تحديث حالة المشروع"""
        for key, value in updates.items():
            if key in self.memory:
                self.memory[key] = value
        self._save_memory()
    
    def log_error(self, error: dict):
        """تسجيل خطأ جديد"""
        self.errors["errors"].append({
            **error,
            "timestamp": datetime.now().isoformat()
        })
        self._save_errors()
    
    def is_known_error(self, error_message: str) -> bool:
        """التحقق مما إذا كان الخطأ معروفًا"""
        for error in self.errors["errors"]:
            if error.get("message") == error_message:
                return True
        return False
    
    def log_task(self, task: dict):
        """تسجيل مهمة جديدة"""
        self.tasks["tasks"].append({
            **task,
            "timestamp": datetime.now().isoformat()
        })
        self._save_tasks()
    
    def get_task_history(self) -> list:
        """الحصول على تاريخ المهام"""
        return self.tasks["tasks"]
    
    def get_error_history(self) -> list:
        """الحصول على تاريخ الأخطاء"""
        return self.errors["errors"]