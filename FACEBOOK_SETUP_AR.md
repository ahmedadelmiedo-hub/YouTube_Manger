# 🔐 شرح الحصول على Facebook Access Token

## الخطوة 1️⃣: إنشاء Facebook App

1. اذهب لـ [Facebook Developers](https://developers.facebook.com/)
2. اضغط **My Apps** → **Create App**
3. اختر **Business** كنوع التطبيق
4. ملء البيانات:
   - **App Name**: Facebook Page Manager
   - **App Purpose**: Select suitable category
   - **App Contact Email**: بريدك
5. اضغط **Create App**

---

## الخطوة 2️⃣: إضافة منتج Facebook Login

1. في لوحة التحكم، اضغط **+ Add Product**
2. ابحث عن **Facebook Login**
3. اختر **Web**
4. اتبع التعليمات

---

## الخطوة 3️⃣: الحصول على Page Access Token

### الطريقة السهلة (للاختبار):

1. اذهب لـ [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. في الأعلى يسار، اختر تطبيقك من القائمة المنسدلة
3. في الـ Token dropdown، اختر **Get Page Access Token**
4. اختر صفحتك من القائمة
5. انسخ الـ Token

### الطريقة الاحترافية (للإنتاج):

```bash
# استخدم User Access Token من App Dashboard
GET https://graph.facebook.com/v18.0/me/accounts
?access_token=YOUR_USER_ACCESS_TOKEN
```

ستحصل على جميع صفحاتك مع Tokens خاصة بكل صفحة.

---

## الخطوة 4️⃣: تخزين Token بأمان

**لا تضع التوكن مباشرة في الكود!** استخدم `.env`:

```env
FACEBOOK_PAGE_ID=500963653091071
FACEBOOK_PAGE_ACCESS_TOKEN=your_token_here
FACEBOOK_APP_ID=your_app_id
FACEBOOK_APP_SECRET=your_app_secret
```

---

## الخطوة 5️⃣: الصلاحيات المطلوبة

تأكد من تفعيل الصلاحيات التالية:

- ✅ **pages_manage_posts** - نشر منشورات
- ✅ **pages_read_engagement** - قراءة التعليقات والتفاعلات
- ✅ **pages_manage_metadata** - إدارة بيانات الصفحة
- ✅ **pages_read_user_content** - قراءة محتوى المستخدمين
- ✅ **instagram_basic** - إذا كان لديك حساب Instagram مرتبط

---

## ✅ تحقق من صحة التوكن:

```bash
curl -i -X GET \
  "https://graph.facebook.com/v18.0/me?fields=id,name&access_token=YOUR_PAGE_ACCESS_TOKEN"
```

إذا اشتغل، هتشوف معلومات صفحتك ✨

---

## 🔄 تجديد التوكن

ـ Page Access Tokens لا تنتهي تلقائياً لكن User Access Tokens تنتهي بعد 60 يوم.
تأكد من التجديد الدوري!

---

**بعد ما تجيب التوكن، روح وضعه في ملف `.env` في المشروع!**