# 📁 بنية المشروع

```
facebook-manager/
├── frontend/                    # React App
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── PostEditor.tsx
│   │   │   ├── ScheduledPosts.tsx
│   │   │   └── Analytics.tsx
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── services/
│   │   │   └── api.ts
│   │   ├── types/
│   │   └── App.tsx
│   ├── package.json
│   └── .env.local
│
├── backend/                     # Node.js + Express
│   ├── src/
│   │   ├── routes/
│   │   │   ├── posts.ts
│   │   │   ├── auth.ts
│   │   │   └── schedule.ts
│   │   ├── controllers/
│   │   ├── models/
│   │   │   ├── Post.ts
│   │   │   └── User.ts
│   │   ├── services/
│   │   │   ├── facebookService.ts
│   │   │   ├── scheduleService.ts
│   │   │   └── authService.ts
│   │   ├── middleware/
│   │   │   └── auth.ts
│   │   ├── config/
│   │   │   └── database.ts
│   │   └── index.ts
│   ├── package.json
│   └── .env
│
├── database/
│   └── schemas/
│       ├── posts.schema.ts
│       └── schedules.schema.ts
│
├── docs/
│   ├── API.md
│   ├── FACEBOOK_SETUP_AR.md
│   └── DEPLOYMENT.md
│
├── .gitignore
└── README.md
```

## المميزات الرئيسية:

### Frontend (React):
- لوحة تحكم جميلة
- محرر منشورات متقدم
- جدول زمني للمنشورات
- إحصائيات وتحليلات
- إدارة المسودات

### Backend (Node.js):
- API للمنشورات
- نظام جدولة تلقائي (Cron Jobs)
- تكامل Facebook Graph API
- مصادقة آمنة
- إدارة الأخطاء والتنبيهات

### Database (MongoDB):
- تخزين المنشورات
- جدولة المنشورات
- سجلات المستخدمين
- تتبع حالة النشر
