# ai_engineer_agent/tools/git_tool.py
import subprocess
from pathlib import Path
from config import PROJECT_PATH, GIT_ENABLED, GIT_AUTO_COMMIT


class GitTool:
    """أداة للتعامل مع Git"""
    
    def __init__(self):
        self.project_path = PROJECT_PATH
        self.enabled = GIT_ENABLED
    
    def _run_git(self, args: list) -> dict:
        """تشغيل أمر Git"""
        if not self.enabled:
            return {"success": False, "message": "Git is disabled"}
        
        try:
            result = subprocess.run(
                ["git"] + args,
                cwd=self.project_path,
                capture_output=True,
                text=True
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def status(self) -> dict:
        """حالة Git"""
        return self._run_git(["status"])
    
    def add_all(self) -> dict:
        """إضافة جميع التغييرات"""
        return self._run_git(["add", "."])
    
    def commit(self, message: str) -> dict:
        """إنشاء commit"""
        result = self.add_all()
        if not result["success"]:
            return result
        return self._run_git(["commit", "-m", message])
    
    def push(self) -> dict:
        """رفع التغييرات"""
        return self._run_git(["push"])
    
    def pull(self) -> dict:
        """سحب التغييرات"""
        return self._run_git(["pull"])
    
    def create_branch(self, branch_name: str) -> dict:
        """إنشاء فرع جديد"""
        return self._run_git(["checkout", "-b", branch_name])
    
    def checkout(self, branch_name: str) -> dict:
        """التبديل إلى فرع"""
        return self._run_git(["checkout", branch_name])
    
    def auto_commit(self, message: str = "Auto-commit by AI Agent") -> dict:
        """commit تلقائي"""
        if not GIT_AUTO_COMMIT:
            return {"success": False, "message": "Auto-commit is disabled"}
        return self.commit(message)