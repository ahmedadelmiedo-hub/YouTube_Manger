# Optional Assets

للحفاظ على حجم المستودع واستهلاك الشبكة منخفضًا، لا تُحفظ الموارد التالية داخل Git:

- `apps/money-printer-turbo/resource/songs/`: موسيقى خلفية اختيارية.
- `STHeitiLight.ttc` و`MicrosoftYaHeiNormal.ttc` و`MicrosoftYaHeiBold.ttc`: خطوط كبيرة غير مطلوبة للبدء.

الخط الموجود حاليًا `STHeitiMedium.ttc` هو الخط الأساسي المستخدم افتراضيًا في إعدادات MoneyPrinterTurbo ويدعم النص العربي. يمكن إضافة الخطوط أو الأغاني محليًا عند الحاجة، دون إدخالها في commit.

لا تضع مفاتيح API أو `config.toml` أو نماذج Whisper داخل المستودع. استخدم ملفات الإعداد المحلية أو Secrets في بيئة التشغيل.
