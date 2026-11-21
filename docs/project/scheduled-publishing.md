# Scheduled Publishing

يوجد Workflow باسم `Scheduled Video Publish` يعمل بجدولة كل 6 ساعات:

```cron
0 */6 * * *
```

الجدولة **متوقفة افتراضيًا** لتوفير الموارد. لن يبدأ أي Runner إلا بعد تحقق الشرطين التاليين:

1. إنشاء Repository Variable باسم `VIDEO_AUTOMATION_ENABLED` وقيمتها `true`.
2. وجود الملف `scripts/video_publish.py` الذي ينفذ دورة كاملة وآمنة:
   `generate → approval/state check → YouTube upload`.

MoneyPrinterTurbo حاليًا هو محرك التوليد، لكنه ليس وحده كافيًا لبناء دورة نشر YouTube مستقلة. لذلك لا يجب تفعيل المتغير قبل إضافة publisher حقيقي يحوي:

- اختيار موضوع/قائمة انتظار دون تكرار.
- حفظ state و`video_id` قبل أي retry.
- YouTube OAuth عبر GitHub Secret، دون طباعة token.
- حالة افتراضية `private` أو `scheduled` وبوابة موافقة قبل `public`.
- رفع فيديو واحد فقط في كل دورة.

إعدادات توفير الموارد المضمنة:

- `concurrency` يمنع تشغيل دورتين متزامنتين.
- `timeout-minutes: 45` يمنع Runner عالقًا.
- `edge` هو المسار الافتراضي للصوت.
- لا يتم تثبيت dependencies أو توليد فيديو عندما تكون البوابة مغلقة.
