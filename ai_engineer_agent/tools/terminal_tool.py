# ai_engineer_agent/tools/terminal_tool.py
import subprocess
import os
import signal
from pathlib import Path
from config import PROJECT_PATH


class TerminalTool:
    """أداة لتشغيل أوامر النظام"""
    
    def __init__(self):
        self.project_path = PROJECT_PATH
        self.bot_process = None
    
    def run_command(self, command: list, cwd: str = None) -> dict:
        """تشغيل أمر وإرجاع النتيجة"""
        cwd = cwd or self.project_path
        try:
            result = subprocess.run(
                command,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=60
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": "Command timed out",
                "returncode": -1
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "returncode": -1
            }
    
    def start_bot(self) -> dict:
        """تشغيل البوت في الخلفية"""
        if self.bot_process and self.bot_process.poll() is None:
            return {"success": True, "message": "Bot already running"}
        
        try:
            self.bot_process = subprocess.Popen(
                ["python", "-m", "app.main"],
                cwd=self.project_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                start_new_session=True
            )
            return {"success": True, "message": "Bot started successfully"}
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def stop_bot(self) -> dict:
        """إيقاف البوت"""
        if self.bot_process and self.bot_process.poll() is None:
            os.killpg(os.getpgid(self.bot_process.pid), signal.SIGTERM)
            self.bot_process.wait()
            return {"success": True, "message": "Bot stopped"}
        return {"success": False, "message": "Bot not running"}
    
    def restart_bot(self) -> dict:
        """إعادة تشغيل البوت"""
        self.stop_bot()
        return self.start_bot()
    
    def get_bot_status(self) -> dict:
        """الحصول على حالة البوت"""
        if self.bot_process and self.bot_process.poll() is None:
            return {"status": "running", "pid": self.bot_process.pid}
        return {"status": "stopped", "pid": None}
    
    def install_package(self, package: str) -> dict:
        """تثبيت حزمة Python"""
        return self.run_command(["pip", "install", package])
    
    def install_requirements(self) -> dict:
        """تثبيت المتطلبات من requirements.txt"""
        req_file = self.project_path / "requirements.txt"
        if not req_file.exists():
            return {"success": False, "message": "requirements.txt not found"}
        return self.run_command(["pip", "install", "-r", str(req_file)])