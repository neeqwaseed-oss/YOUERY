# ai_engineer_agent/ai/prompts.py
"""
قوالب الـ Prompts الجاهزة للاستخدام
"""


class Prompts:
    """مجموعة من قوالب الـ Prompts"""
    
    @staticmethod
    def system_prompt() -> str:
        return """
        أنت مهندس برمجيات ذكي (AI Software Engineer).
        مهمتك هي تطوير، صيانة، وإصلاح مشاريع بايثون.
        لديك القدرة على:
        1. تحليل هيكل المشروع
        2. قراءة وفهم الملفات
        3. كتابة وتعديل الكود
        4. إضافة المكتبات
        5. تشغيل الاختبارات
        6. إصلاح الأخطاء
        7. إعادة تشغيل البوت
        
        يجب أن تكون دقيقًا، واقعيًا، ومنظمًا.
        """
    
    @staticmethod
    def analyze_error(error_log: str) -> str:
        return f"""
        حدث خطأ في البوت. إليك سجل الخطأ:
        {error_log}
        
        المطلوب منك:
        1. تحديد سبب الخطأ بدقة
        2. تحديد الملف الذي يحتاج إلى تعديل
        3. كتابة التصحيح المناسب
        4. التأكد من أن التصحيح يحل المشكلة
        """
    
    @staticmethod
    def create_new_feature(request: str, project_structure: str) -> str:
        return f"""
        طلب المستخدم: {request}
        
        هيكل المشروع الحالي:
        {project_structure}
        
        المطلوب منك:
        1. فهم الطلب
        2. تحديد الملفات المطلوبة
        3. كتابة الكود كاملاً
        4. إضافة الاختبارات
        5. التأكد من أن الكود يعمل
        """
    
    @staticmethod
    def fix_test_failures(test_output: str) -> str:
        return f"""
        فشلت الاختبارات. إليك المخرجات:
        {test_output}
        
        المطلوب منك:
        1. تحليل سبب فشل الاختبارات
        2. تحديد الملفات التي تحتاج إلى تعديل
        3. كتابة التصحيحات
        4. التأكد من أن الاختبارات تنجح
        """
    
    @staticmethod
    def optimize_performance(metrics: dict) -> str:
        return f"""
        مقاييس الأداء الحالية:
        {metrics}
        
        المطلوب منك:
        1. تحليل المقاييس
        2. تحديد أماكن التحسين
        3. كتابة التعديلات المطلوبة
        """