# ai_engineer_agent/ai/engine.py
import json
import openai
from config import OPENAI_API_KEY, AI_MODEL, AI_MAX_TOKENS, AI_TEMPERATURE

openai.api_key = OPENAI_API_KEY


class AIEngine:
    """محرك الذكاء الاصطناعي"""
    
    def __init__(self, model: str = None):
        self.model = model or AI_MODEL
        self.max_tokens = AI_MAX_TOKENS
        self.temperature = AI_TEMPERATURE
    
    async def analyze(self, prompt: str, context: dict = None) -> dict:
        """إرسال طلب للذكاء الاصطناعي مع السياق"""
        
        system_prompt = """
        أنت مهندس برمجيات ذكي (AI Software Engineer).
        مهمتك هي تحليل المشاكل، كتابة الكود، وتخطيط الحلول.
        يجب أن تكون دقيقًا وواقعيًا.
        الرد يجب أن يكون JSON فقط.
        لا تكتب أي شيء خارج JSON.
        """
        
        if context:
            full_prompt = f"""
            السياق الحالي للمشروع:
            {json.dumps(context, indent=2)}
            
            الطلب:
            {prompt}
            """
        else:
            full_prompt = prompt
        
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": full_prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            content = response.choices[0].message.content
            
            # استخراج JSON من الرد
            start = content.find("{")
            end = content.rfind("}") + 1
            if start != -1 and end > start:
                return json.loads(content[start:end])
            else:
                return {"error": "No JSON found in response", "raw": content}
                
        except json.JSONDecodeError as e:
            return {"error": f"JSON parsing error: {e}", "raw": content}
        except Exception as e:
            return {"error": f"AI request failed: {e}", "raw": str(e)}
    
    async def fix_error(self, error_log: str, project_context: dict) -> dict:
        """تحليل خطأ واقتراح إصلاح"""
        prompt = f"""
        حدث خطأ في البوت. إليك سجل الخطأ:
        {error_log}
        
        المطلوب:
        1. تحليل سبب الخطأ
        2. كتابة التصحيح المناسب
        3. تحديد الملفات التي تحتاج إلى تعديل
        
        الرد بصيغة JSON:
        {{
            "cause": "سبب الخطأ",
            "files": [
                {{
                    "path": "مسار الملف",
                    "content": "المحتوى الجديد الكامل للملف"
                }}
            ],
            "explanation": "شرح ما تم إصلاحه"
        }}
        """
        
        return await self.analyze(prompt, project_context)
    
    async def plan_development(self, user_request: str, project_state: dict) -> dict:
        """تخطيط مهمة تطويرية"""
        prompt = f"""
        طلب المستخدم: {user_request}
        
        المطلوب:
        1. تحليل الطلب
        2. تقسيم الطلب إلى خطوات قابلة للتنفيذ
        3. تحديد الملفات التي تحتاج إلى تعديل أو إنشاء
        4. تحديد المكتبات الجديدة المطلوبة
        5. تحديد الاختبارات المطلوبة
        
        الرد بصيغة JSON:
        {{
            "task_id": "رقم المهمة (اختياري)",
            "description": "وصف المهمة",
            "steps": [
                {{
                    "step": 1,
                    "action": "analyze|create|modify|test|deploy",
                    "files": ["مسار الملف"],
                    "description": "وصف الخطوة"
                }}
            ],
            "libraries": ["مكتبة1", "مكتبة2"],
            "requires_approval": true|false,
            "estimated_time": "تقدير الوقت"
        }}
        """
        
        return await self.analyze(prompt, project_state)