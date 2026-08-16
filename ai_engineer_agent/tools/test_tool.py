# ai_engineer_agent/tools/test_tool.py
import subprocess
from pathlib import Path
from config import PROJECT_PATH, TEST_TIMEOUT


class TestTool:
    """أداة لتشغيل الاختبارات"""
    
    def __init__(self):
        self.project_path = PROJECT_PATH
    
    def run(self, test_path: str = None) -> dict:
        """تشغيل الاختبارات"""
        cmd = ["pytest", "-q", "--tb=short"]
        if test_path:
            cmd.append(test_path)
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=TEST_TIMEOUT
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "passed": result.returncode == 0
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": "Tests timed out",
                "returncode": -1,
                "passed": False
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "returncode": -1,
                "passed": False
            }
    
    def run_with_retry(self, max_retries: int = 3) -> dict:
        """تشغيل الاختبارات مع إعادة المحاولة"""
        for attempt in range(max_retries):
            result = self.run()
            if result["success"]:
                return result
        return result
    
    def get_test_files(self) -> list:
        """الحصول على قائمة ملفات الاختبار"""
        test_dir = self.project_path / "tests"
        if not test_dir.exists():
            return []
        
        files = []
        for item in test_dir.rglob("test_*.py"):
            if item.is_file():
                files.append(str(item.relative_to(self.project_path)))
        return files