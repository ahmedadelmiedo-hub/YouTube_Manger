# 📱 Facebook Page Manager Pro

محاكي كامل لإدارة صفحات الفيسبوك مع نظام نشر مجدول تلقائي!

## ✨ المميزات

✅ **لوحة تحكم شاملة** - إدارة جميع جوانب صفحتك  
✅ **جدولة المنشورات** - اضبط موعد النشر والنشر التلقائي  
✅ **محرر متقدم** - دعم الصور والفيديوهات والنصوص  
✅ **إحصائيات فورية** - تابع أداء المنشورات  
✅ **مسودات ذكية** - احفظ عملك واكمل لاحقاً  
✅ **API آمنة** - تكامل آمن مع Facebook  
✅ **نظام إخطارات** - تنبيهات عند فشل أو نجاح النشر  

## 🚀 البدء السريع

### المتطلبات:
- Node.js 18+
- MongoDB
- Facebook App (مع صلاحيات)

### التثبيت:

```bash
# استنساخ المشروع
git clone https://github.com/ahmedadelmiedo-hub/YouTube_Manger.git
cd YouTube_Manger
git checkout dev/facebook-manager

# إعداد Backend
cd backend
npm install
cp .env.example .env
# قم بتعديل .env بـ بيانات فيسبوك

# إعداد Frontend
cd ../frontend
npm install
cp .env.example .env.local

# تشغيل التطبيق
# Terminal 1 - Backend
cd backend
npm run dev

# Terminal 2 - Frontend
cd frontend
npm start
```

## 📚 الوثائق

- [شرح الحصول على Facebook Token](./FACEBOOK_SETUP_AR.md)
- [API Documentation](./docs/API.md)
- [نشر المشروع](./docs/DEPLOYMENT.md)

## 🔐 الأمان

⚠️ **لا تشارك أبداً:**
- Access Tokens
- App Secrets
- Database URLs

استخدم `.env` و `.env.local` فقط!

## 🤝 المساهمة

نرحب بأي مساهمات! قم بـ:
1. Fork المشروع
2. إنشاء فرع جديد (`git checkout -b feature/amazing-feature`)
3. Commit التغييرات
4. Push لـ الفرع
5. فتح Pull Request

## 📞 الدعم

إذا واجهت أي مشاكل:
1. اقرأ [FACEBOOK_SETUP_AR.md](./FACEBOOK_SETUP_AR.md)
2. تحقق من الـ Issues
3. افتح Issue جديدة

---

**Made with ❤️ by ahmedadelmiedo-hub**
