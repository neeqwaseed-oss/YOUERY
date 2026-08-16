# ai_engineer_agent/core/orchestrator.py
import asyncio
from typing import Dict, Any
from datetime import datetime

from core.planner import Planner
from core.developer import Developer
from memory.project_memory import ProjectMemory
from tools.test_tool import TestTool
from tools.terminal_tool import TerminalTool
from tools.git_tool import GitTool
from ai.engine import AIEngine


class Orchestrator:
    """المنسق الرئيسي بين الوكيلات"""
    
    def __init__(self):
        self.planner = Planner()
        self.developer = Developer()
        self.memory = ProjectMemory()
        self.test_tool = TestTool()
        self.terminal = TerminalTool()
        self.git = GitTool()
        self.ai = AIEngine()
        self.current_task = None
    
    async def create_plan(self, user_request: str) -> dict:
        """إنشاء خطة عمل بناءً على طلب المستخدم"""
        
        # الحصول على حالة المشروع
        project_state = self.memory.get_state()
        
        # الحصول على هيكل الملفات
        file_tree = await self.developer.file_tool.get_file_tree()
        project_state["file_tree"] = file_tree
        
        # تخطيط المهمة
        plan = await self.ai.plan_development(user_request, project_state)
        
        # تسجيل المهمة
        task_record = {
            "request": user_request,
            "plan": plan,
            "timestamp": datetime.now().isoformat()
        }
        self.memory.log_task(task_record)
        
        return plan
    
    async def execute_plan(self, plan: dict) -> dict:
        """تنفيذ خطة العمل"""
        
        results = []
        steps = plan.get("steps", [])
        
        for step in steps:
            # تنفيذ الخطوة
            result = await self.developer.execute_step(step)
            results.append(result)
            
            # إذا كانت الخطوة تتطلب اختبارات
            if step.get("action") == "test":
                test_result = self.test_tool.run()
                if not test_result["success"]:
                    # إصلاح الأخطاء
                    fix_plan = await self.fix_issues(test_result["stderr"])
                    if fix_plan:
                        await self.developer.execute_step(fix_plan)
            
            # إذا كانت الخطوة تتطلب تشغيل البوت
            if step.get("action") == "deploy":
                self.terminal.restart_bot()
        
        # تسجيل النتيجة
        self.memory.update_state({
            "last_updated": datetime.now().isoformat(),
            "last_operation": plan.get("description", "Unknown")
        })
        
        return {
            "success": True,
            "results": results,
            "summary": f"Completed {len(steps)} steps"
        }
    
    async def fix_issues(self, error_output: str) -> dict:
        """إصلاح المشاكل التي ظهرت في الاختبارات"""
        
        project_state = self.memory.get_state()
        
        # طلب الإصلاح من الذكاء الاصطناعي
        fix_plan = await self.ai.fix_error(error_output, project_state)
        
        if fix_plan.get("files"):
            return {
                "action": "modify",
                "files": fix_plan["files"],
                "description": "Fixing test failures"
            }
        return None