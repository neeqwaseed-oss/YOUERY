# ai_engineer_agent/core/guardian.py
import asyncio
import time
from datetime import datetime

from tools.health_tool import HealthTool
from tools.test_tool import TestTool
from tools.terminal_tool import TerminalTool
from core.planner import Planner
from core.developer import Developer
from memory.project_memory import ProjectMemory
from ai.engine import AIEngine
from config import HEALTH_CHECK_INTERVAL, MAX_AUTO_FIX_ATTEMPTS, AUTO_FIX_LEVEL


class Guardian:
    """وكيل الصيانة - مراقبة مستمرة وإصلاح تلقائي"""
    
    def __init__(self):
        self.health = HealthTool()
        self.test_tool = TestTool()
        self.terminal = TerminalTool()
        self.planner = Planner()
        self.developer = Developer()
        self.memory = ProjectMemory()
        self.ai = AIEngine()
        self.fix_attempts = 0
        self.is_running = False
    
    async def start_monitoring(self):
        """بدء حلقة المراقبة"""
        self.is_running = True
        print("🛡️ Guardian Agent is watching...")
        
        while self.is_running:
            try:
                # 1. فحص صحة البوت
                health_status = await self.health.check_all()
                
                # 2. تحديث الذاكرة
                self.memory.update_state({
                    "last_health_check": health_status["timestamp"],
                    "last_bot_status": health_status["bot_status"]
                })
                
                # 3. إذا كان البوت ميتًا
                if health_status["bot_status"] == "stopped":
                    await self.handle_crash(health_status)
                
                # 4. إذا كانت هناك أخطاء
                elif health_status["has_errors"]:
                    await self.handle_errors(health_status["errors"])
                
                # 5. فحص الأداء (إذا كان البوت يعمل)
                elif health_status["bot_status"] == "running":
                    if health_status["cpu_usage"] > 80:
                        await self.handle_high_cpu()
                    if health_status["memory_usage"] > 80:
                        await self.handle_high_memory()
                
                # الانتظار حتى الفحص التالي
                await asyncio.sleep(HEALTH_CHECK_INTERVAL)
                
            except Exception as e:
                print(f"⚠️ Guardian error: {e}")
                await asyncio.sleep(10)
    
    async def stop_monitoring(self):
        """إيقاف حلقة المراقبة"""
        self.is_running = False
        print("🛡️ Guardian Agent stopped")
    
    async def handle_crash(self, health_status: dict):
        """معالجة انهيار البوت"""
        print("🚨 Bot crashed! Analyzing...")
        
        # قراءة السجلات
        logs = self.health.read_logs()
        
        # التحقق من مستوى الاستقلالية
        if AUTO_FIX_LEVEL in ["safe", "moderate", "full"]:
            if self.fix_attempts < MAX_AUTO_FIX_ATTEMPTS:
                # إنشاء خطة إصلاح
                fix_plan = await self.planner.create_fix_plan(logs)
                
                if fix_plan.get("files"):
                    # تطبيق التصحيح
                    await self.developer.modify_files(fix_plan["files"])
                    
                    # تشغيل الاختبارات
                    test_result = self.test_tool.run()
                    
                    if test_result["success"]:
                        # إعادة تشغيل البوت
                        self.terminal.restart_bot()
                        self.fix_attempts = 0
                        print("✅ Bot recovered successfully!")
                        
                        # تسجيل الإصلاح
                        self.memory.log_error({
                            "message": "Bot crashed and recovered",
                            "fix": fix_plan,
                            "status": "success"
                        })
                    else:
                        self.fix_attempts += 1
                        print(f"❌ Fix failed. Attempt {self.fix_attempts}/{MAX_AUTO_FIX_ATTEMPTS}")
                        
                        # تسجيل الفشل
                        self.memory.log_error({
                            "message": "Bot crashed, fix failed",
                            "fix": fix_plan,
                            "test_output": test_result["stderr"],
                            "status": "failed"
                        })
            else:
                print("⚠️ Max attempts reached. Stopping auto-fix.")
                # إرسال إشعار للمطور
                await self.notify_admin("❌ Bot crashed and auto-fix failed. Manual intervention required.")
    
    async def handle_errors(self, errors: list):
        """معالجة الأخطاء غير الحرجة"""
        for error in errors:
            # التحقق مما إذا كان الخطأ معروفًا
            if self.memory.is_known_error(error):
                print(f"ℹ️ Known error: {error}")
                continue
            
            # محاولة الإصلاح التلقائي
            if AUTO_FIX_LEVEL in ["moderate", "full"]:
                fix_plan = await self.planner.create_fix_plan(error)
                
                if fix_plan.get("files"):
                    await self.developer.modify_files(fix_plan["files"])
                    
                    # تسجيل الخطأ والحل
                    self.memory.log_error({
                        "message": error,
                        "fix": fix_plan,
                        "status": "fixed"
                    })
                    
                    print(f"✅ Fixed error: {error}")
    
    async def handle_high_cpu(self):
        """معالجة ارتفاع استخدام CPU"""
        print("⚠️ High CPU usage detected")
        # يمكن إضافة تحسينات هنا
    
    async def handle_high_memory(self):
        """معالجة ارتفاع استخدام الذاكرة"""
        print("⚠️ High memory usage detected")
        # يمكن إضافة تحسينات هنا
    
    async def notify_admin(self, message: str):
        """إرسال إشعار للمطور"""
        # سيتم تنفيذه في واجهة التواصل
        print(f"📨 Notification: {message}")