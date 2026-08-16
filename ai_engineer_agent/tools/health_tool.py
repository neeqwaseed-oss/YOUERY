# ai_engineer_agent/tools/health_tool.py
import psutil
import subprocess
import time
from pathlib import Path
from datetime import datetime
from config import PROJECT_PATH
from tools.terminal_tool import TerminalTool


class HealthTool:
    """أداة لمراقبة صحة البوت"""
    
    def __init__(self):
        self.project_path = PROJECT_PATH
        self.terminal = TerminalTool()
        self.log_file = self.project_path / "logs" / "error.log"
    
    async def check_all(self) -> dict:
        """فحص شامل للصحة"""
        return {
            "timestamp": datetime.now().isoformat(),
            "bot_status": self.check_bot_status(),
            "cpu_usage": psutil.cpu_percent(),
            "memory_usage": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage("/").percent,
            "has_errors": self.has_errors(),
            "errors": self.get_recent_errors()
        }
    
    def check_bot_status(self) -> str:
        """فحص حالة البوت"""
        status = self.terminal.get_bot_status()
        return status.get("status", "unknown")
    
    def has_errors(self) -> bool:
        """التحقق من وجود أخطاء في السجل"""
        if not self.log_file.exists():
            return False
        
        with open(self.log_file, 'r') as f:
            content = f.read()
            return "ERROR" in content or "EXCEPTION" in content or "CRITICAL" in content
    
    def get_recent_errors(self, lines: int = 50) -> list:
        """الحصول على آخر الأخطاء"""
        if not self.log_file.exists():
            return []
        
        with open(self.log_file, 'r') as f:
            all_lines = f.readlines()
            recent = all_lines[-lines:]
            
            errors = []
            for line in recent:
                if "ERROR" in line or "EXCEPTION" in line or "CRITICAL" in line:
                    errors.append(line.strip())
            return errors
    
    def read_logs(self, lines: int = 100) -> str:
        """قراءة السجلات"""
        if not self.log_file.exists():
            return "No log file found"
        
        with open(self.log_file, 'r') as f:
            all_lines = f.readlines()
            return "".join(all_lines[-lines:])
    
    def restart_bot(self) -> dict:
        """إعادة تشغيل البوت"""
        return self.terminal.restart_bot()
    
    def get_performance_metrics(self) -> dict:
        """الحصول على مقاييس الأداء"""
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage("/").percent,
            "network_sent": psutil.net_io_counters().bytes_sent,
            "network_recv": psutil.net_io_counters().bytes_recv,
            "open_files": len(psutil.Process().open_files()),
            "threads": psutil.Process().num_threads()
        }