# ai_engineer_agent/bot/telegram_handler.py
import asyncio
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from core.orchestrator import Orchestrator
from core.guardian import Guardian
from memory.project_memory import ProjectMemory
from tools.terminal_tool import TerminalTool
from config import DEV_BOT_TOKEN

router = Router()


class ChatStates(StatesGroup):
    waiting_for_command = State()
    waiting_for_confirmation = State()


# تهيئة النظام
orchestrator = Orchestrator()
guardian = Guardian()
terminal = TerminalTool()
memory = ProjectMemory()


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await message.answer(
        "🤖 <b>AI Engineering Agent</b>\n\n"
        "أنا مهندس البرمجيات الآلي الخاص بك.\n"
        "أستطيع:\n"
        "✅ تطوير ميزات جديدة\n"
        "✅ إصلاح الأخطاء تلقائيًا\n"
        "✅ مراقبة البوت 24/7\n"
        "✅ تحسين الأداء\n\n"
        "ما هو طلبك اليوم؟",
        parse_mode="HTML"
    )
    await state.set_state(ChatStates.waiting_for_command)


@router.message(Command("status"))
async def cmd_status(message: Message):
    """عرض حالة البوت"""
    # الحصول على حالة البوت
    bot_status = terminal.get_bot_status()
    health_status = await guardian.health.check_all()
    
    status_text = f"""
    📊 <b>حالة النظام</b>
    
    🤖 البوت: {bot_status.get('status', 'unknown')}
    🟢 CPU: {health_status.get('cpu_usage', 0)}%
    🟢 RAM: {health_status.get('memory_usage', 0)}%
    🟢 Disk: {health_status.get('disk_usage', 0)}%
    
    📝 السجلات: {'✅' if not health_status.get('has_errors') else '⚠️ يوجد أخطاء'}
    """
    
    await message.answer(status_text, parse_mode="HTML")


@router.message(Command("stop_bot"))
async def cmd_stop_bot(message: Message):
    """إيقاف البوت"""
    result = terminal.stop_bot()
    await message.answer(f"🛑 {result.get('message', 'Bot stopped')}")


@router.message(Command("start_bot"))
async def cmd_start_bot(message: Message):
    """تشغيل البوت"""
    result = terminal.start_bot()
    await message.answer(f"🚀 {result.get('message', 'Bot started')}")


@router.message(Command("history"))
async def cmd_history(message: Message):
    """عرض تاريخ المهام"""
    tasks = memory.get_task_history()
    
    if not tasks:
        await message.answer("📋 لا توجد مهام سابقة.")
        return
    
    history_text = "📋 <b>تاريخ المهام</b>\n\n"
    for task in tasks[-10:]:  # آخر 10 مهام
        history_text += f"• {task.get('timestamp', '')[:19]}: {task.get('request', '')[:50]}...\n"
    
    await message.answer(history_text, parse_mode="HTML")


@router.message(Command("errors"))
async def cmd_errors(message: Message):
    """عرض سجل الأخطاء"""
    errors = memory.get_error_history()
    
    if not errors:
        await message.answer("✅ لا توجد أخطاء مسجلة.")
        return
    
    errors_text = "⚠️ <b>سجل الأخطاء</b>\n\n"
    for error in errors[-10:]:  # آخر 10 أخطاء
        errors_text += f"• {error.get('timestamp', '')[:19]}: {error.get('message', '')}\n"
        if error.get('status') == 'fixed':
            errors_text += "  ✅ تم الإصلاح\n"
        elif error.get('status') == 'failed':
            errors_text += "  ❌ فشل الإصلاح\n"
    
    await message.answer(errors_text, parse_mode="HTML")


@router.message(Command("guardian"))
async def cmd_guardian(message: Message):
    """التحكم في Guardian"""
    args = message.text.split()
    if len(args) > 1 and args[1] == "stop":
        await guardian.stop_monitoring()
        await message.answer("🛡️ Guardian Agent stopped.")
    elif len(args) > 1 and args[1] == "start":
        asyncio.create_task(guardian.start_monitoring())
        await message.answer("🛡️ Guardian Agent started.")
    else:
        await message.answer(
            "🛡️ <b>Guardian Agent</b>\n\n"
            "الأوامر المتاحة:\n"
            "/guardian start - بدء المراقبة\n"
            "/guardian stop - إيقاف المراقبة",
            parse_mode="HTML"
        )


@router.message(ChatStates.waiting_for_command)
async def handle_command(message: Message, state: FSMContext):
    user_request = message.text
    
    # إرسال مؤشر "جاري العمل"
    processing = await message.answer("🧠 <i>جاري تحليل الطلب والتخطيط...</i>", parse_mode="HTML")
    
    try:
        # 1. التخطيط
        plan = await orchestrator.create_plan(user_request)
        
        # 2. إذا كان الطلب يتطلب موافقة
        if plan.get("requires_approval", False):
            # عرض الخطة للمستخدم
            approval_text = f"""
            📋 <b>الخطة المقترحة:</b>
            
            <b>الوصف:</b> {plan.get('description', 'No description')}
            
            <b>الخطوات:</b>
            """
            
            for step in plan.get("steps", []):
                approval_text += f"\n• {step.get('description', '')}"
            
            approval_text += "\n\n<i>هل توافق على تنفيذ هذه الخطة؟ (أرسل 'نعم' أو 'لا')</i>"
            
            await processing.edit_text(approval_text, parse_mode="HTML")
            await state.set_state(ChatStates.waiting_for_confirmation)
            await state.update_data(plan=plan)
            return
        
        # 3. تنفيذ الخطة
        result = await orchestrator.execute_plan(plan)
        
        # 4. إرسال النتيجة
        await processing.edit_text(
            f"✅ <b>تم التنفيذ!</b>\n\n{result.get('summary', 'Done.')}",
            parse_mode="HTML"
        )
        
    except Exception as e:
        await processing.edit_text(f"❌ <b>حدث خطأ:</b>\n\n{str(e)}", parse_mode="HTML")
    
    # إعادة الحالة للاستقبال
    await state.set_state(ChatStates.waiting_for_command)


@router.message(ChatStates.waiting_for_confirmation)
async def handle_confirmation(message: Message, state: FSMContext):
    user_response = message.text.lower().strip()
    
    if user_response in ["نعم", "yes", "y", "ok"]:
        # الموافقة - تنفيذ الخطة
        data = await state.get_data()
        plan = data.get("plan")
        
        processing = await message.answer("🧠 <i>جاري تنفيذ الخطة...</i>", parse_mode="HTML")
        
        try:
            result = await orchestrator.execute_plan(plan)
            await processing.edit_text(
                f"✅ <b>تم التنفيذ!</b>\n\n{result.get('summary', 'Done.')}",
                parse_mode="HTML"
            )
        except Exception as e:
            await processing.edit_text(f"❌ <b>حدث خطأ:</b>\n\n{str(e)}", parse_mode="HTML")
    else:
        # رفض - إلغاء الخطة
        await message.answer("❌ تم إلغاء الخطة.")
    
    await state.set_state(ChatStates.waiting_for_command)


@router.message(Command("help"))
async def cmd_help(message: Message):
    help_text = """
    🤖 <b>AI Engineering Agent - المساعدة</b>
    
    <b>الأوامر المتاحة:</b>
    
    /start - بدء المحادثة
    /status - عرض حالة البوت والنظام
    /start_bot - تشغيل البوت
    /stop_bot - إيقاف البوت
    /history - عرض تاريخ المهام
    /errors - عرض سجل الأخطاء
    /guardian - التحكم في وكيل المراقبة
    /help - عرض هذه المساعدة
    
    <b>كيفية استخدام الوكيل:</b>
    مجرد إرسال طلبك باللغة العربية أو الإنجليزية، وسيقوم الوكيل بتنفيذه.
    
    أمثلة:
    - "أضف أمر /stats يعرض إحصائيات البوت"
    - "البوت يتوقف عند مسح مجموعة كبيرة، أصلحه"
    - "غير لوحة المفاتيح الرئيسية لتكون عمودين"
    """
    
    await message.answer(help_text, parse_mode="HTML")