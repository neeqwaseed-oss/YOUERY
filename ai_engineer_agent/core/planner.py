# ai_engineer_agent/core/planner.py
import json
from ai.engine import AIEngine
from memory.project_memory import ProjectMemory
from config import PROJECT_PATH


class Planner:
    """وكيل التخطيط - يخطط للمهام ويقسمها إلى خطوات"""
    
    def __init__(self):
        self.ai = AIEngine()
        self.memory = ProjectMemory()
    
    async def create_plan(self, user_request: str) -> dict:
        """إنشاء خطة عمل متكاملة"""
        
        # قراءة حالة المشروع الحالية
        project_state = self.memory.get_state()
        
        # الحصول على هيكل الملفات من المشروع الفعلي
        from tools.file_tool import FileTool
        file_tool = FileTool()
        file_tree = await file_tool.get_file_tree()
        project_state["file_tree"] = file_tree
        
        # إرسال الطلب للذكاء الاصطناعي
        plan = await self.ai.plan_development(user_request, project_state)
        
        return plan
    
    async def create_fix_plan(self, error_log: str) -> dict:
        """إنشاء خطة لإصلاح خطأ"""
        
        project_state = self.memory.get_state()
        
        # إرسال الخطأ للذكاء الاصطناعي
        fix_plan = await self.ai.fix_error(error_log, project_state)
        
        return fix_plan