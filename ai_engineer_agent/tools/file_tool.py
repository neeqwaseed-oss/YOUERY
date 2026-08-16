# ai_engineer_agent/tools/file_tool.py
import os
import shutil
from pathlib import Path
from datetime import datetime
import aiofiles
from config import PROJECT_PATH


class FileTool:
    """أداة للتعامل مع الملفات"""
    
    def __init__(self):
        self.project_path = PROJECT_PATH
    
    async def read_file(self, relative_path: str) -> str:
        """قراءة محتوى ملف"""
        full_path = self.project_path / relative_path
        if not full_path.exists():
            return "FILE_NOT_FOUND"
        async with aiofiles.open(full_path, 'r', encoding='utf-8') as f:
            return await f.read()
    
    async def write_file(self, relative_path: str, content: str, backup: bool = True) -> dict:
        """كتابة محتوى إلى ملف"""
        full_path = self.project_path / relative_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        result = {"path": relative_path, "status": "written"}
        
        if backup and full_path.exists():
            # إنشاء نسخة احتياطية
            backup_path = full_path.with_suffix(f".backup.{int(datetime.now().timestamp())}")
            shutil.copy(full_path, backup_path)
            result["backup"] = str(backup_path)
        
        async with aiofiles.open(full_path, 'w', encoding='utf-8') as f:
            await f.write(content)
        
        return result
    
    async def create_file(self, relative_path: str, content: str) -> dict:
        """إنشاء ملف جديد"""
        return await self.write_file(relative_path, content, backup=False)
    
    async def delete_file(self, relative_path: str) -> dict:
        """حذف ملف"""
        full_path = self.project_path / relative_path
        if full_path.exists():
            os.remove(full_path)
            return {"path": relative_path, "status": "deleted"}
        return {"path": relative_path, "status": "not_found"}
    
    async def list_files(self, directory: str = "") -> list:
        """سرد الملفات في دليل"""
        full_path = self.project_path / directory
        if not full_path.exists():
            return []
        
        files = []
        for item in full_path.iterdir():
            if item.is_file():
                files.append(str(item.relative_to(self.project_path)))
            elif item.is_dir():
                files.append(str(item.relative_to(self.project_path)) + "/")
        return files
    
    async def get_file_tree(self) -> str:
        """الحصول على هيكل الملفات كنص"""
        tree = []
        for root, dirs, files in os.walk(self.project_path):
            if "__pycache__" in root or ".git" in root or ".venv" in root:
                continue
            level = root.replace(str(self.project_path), "").count(os.sep)
            indent = " " * 4 * level
            tree.append(f"{indent}{Path(root).name}/")
            subindent = " " * 4 * (level + 1)
            for f in files:
                if not f.endswith(('.pyc', '.pyo', '.db', '.session', '.log')):
                    tree.append(f"{subindent}{f}")
        return "\n".join(tree)