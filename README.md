# YouTube Manager

منصة تطوير تدريجية لإنتاج الفيديوهات وإدارتها، مبنية حاليًا حول [MoneyPrinterTurbo](https://github.com/harry0703/MoneyPrinterTurbo).

## الهيكلة

- `apps/money-printer-turbo/`: المصدر المدمج لـ MoneyPrinterTurbo.
- `tools/windows/`: أدوات التشغيل والتشخيص والتحديث الخاصة بـ Windows.
- `docs/project/`: توثيق المشروع والملفات القديمة المحتفظ بها للتوافق.
- `.github/workflows/blank.yml`: فحص خفيف للكود، وليس تشغيلًا لتوليد الفيديو.

## التشغيل المحلي

على Windows يمكن استخدام `start.bat`. هذا يشغّل التطبيق المحلي فقط ولا ينشئ أي GitHub Actions job.

لتحديث الكود استخدم `update-project.bat`. التحديث يعمل من جذر المستودع، ثم يثبت الاعتمادات داخل مسار التطبيق.

## مبدأ استهلاك الموارد

لا يوجد نشر تلقائي أو جدولة فيديوهات في هذه المرحلة. اختبارات CI تقتصر على فحص Python syntax والملفات الأساسية. موارد الفيديو الاختيارية الثقيلة موضحة في [`docs/project/optional-assets.md`](docs/project/optional-assets.md) ولا تُحفظ داخل Git افتراضيًا.

## المرحلة التالية

سيُضاف orchestration layer منفصل لاحقًا لإدارة `story → video → approval → YouTube upload`، مع الحفاظ على MoneyPrinterTurbo كمحرك إنتاج وعدم تعديل واجهته قبل اكتمال اختبارات التكامل.
