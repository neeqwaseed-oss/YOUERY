# ai_engineer_agent/core/developer.py
import asyncio
from typing import Dict, Any, List

from tools.file_tool import FileTool
from tools.terminal_tool import TerminalTool
from tools.test_tool import TestTool
from tools.git_tool import GitTool
from ai.engine import AIEngine
from config import PROJECT_PATH


class Developer:
    """وكيل التطوير - ينفذ مهام التطوير الفعلية"""
    
    def __init__(self):
        self.file_tool = FileTool()
        self.terminal = TerminalTool()
        self.test_tool = TestTool()
        self.git = GitTool()
        self.ai = AIEngine()
        self.project_path = PROJECT_PATH
    
    async def execute_step(self, step: dict) -> dict:
        """تنفيذ خطوة واحدة من الخطة"""
        action = step.get("action")
        files = step.get("files", [])
        description = step.get("description", "")
        
        print(f"📝 Executing: {description}")
        
        if action == "analyze":
            # تحليل ملف لفهمه
            result = await self.analyze_files(files)
        elif action == "create":
            # إنشاء ملف جديد
            result = await self.create_files(files)
        elif action == "modify":
            # تعديل ملف موجود
            result = await self.modify_files(files)
        elif action == "test":
            # تشغيل الاختبارات
            result = self.test_tool.run()
        elif action == "deploy":
            # تشغيل البوت
            result = self.terminal.start_bot()
        elif action == "install":
            # تثبيت مكتبة
            result = self.terminal.install_package(files[0])
        else:
            result = {"error": f"Unknown action: {action}"}
        
        # تسجيل التغييرات في Git
        if self.git.enabled and action in ["create", "modify"]:
            self.git.auto_commit(f"Auto: {description}")
        
        return {"step": step, "result": result}
    
    async def analyze_files(self, files: List[str]) -> dict:
        """قراءة وتحليل ملفات متعددة"""
        content = {}
        for file in files:
            content[file] = await self.file_tool.read_file(file)
        return {"files": content}
    
    async def create_files(self, files: List[dict]) -> dict:
        """إنشاء ملفات جديدة"""
        results = []
        for file in files:
            if isinstance(file, dict):
                path = file.get("path")
                content = file.get("content", "")
            else:
                path = file
                content = ""
            
            result = await self.file_tool.create_file(path, content)
            results.append(result)
        return {"files": results}
    
    async def modify_files(self, files: List[dict]) -> dict:
        """تعديل ملفات موجودة"""
        results = []
        for file in files:
            if isinstance(file, dict):
                path = file.get("path")
                content = file.get("content", "")
            else:
                path = file
                content = ""
            
            result = await self.file_tool.write_file(path, content)
            results.append(result)
        return {"files": results}