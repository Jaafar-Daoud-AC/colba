<div dir="rtl">

# 📦 دليل نشر الإصدارات باحتراف داخل مستودع واحد

هذا الدليل يشرح كيف تحتفظ بكل إصدارات **كولبا** (القديمة على سطح المكتب والحديثة على الويب) في **مستودع GitHub واحد** بدون فوضى، وكيف تنشر أي إصدار جديد مستقبلًا بخطوات ثابتة.

---

## 1) الفكرة الأساسية

المشكلة الشائعة: وضع الإصدارات داخل المجلد نفسه بأسماء مثل `colaba.0.1.5.py` و`colaba.0.1.6.py` و`app_final.py` و`app_final2.py`. هذا يخلق فوضى، ويصعب معرفة أيها الحالي.

الحل الاحترافي يعتمد على ثلاثة أدوات يوفّرها Git وGitHub:

| الأداة | وظيفتها |
|--------|---------|
| **الفروع (Branches)** | فصل الأجيال المختلفة من المشروع (الويب الحالي ≠ سطح المكتب القديم) |
| **الوسوم (Tags)** | وضع علامة ثابتة على نقطة معيّنة في التاريخ، مثل `v1.0.0` |
| **الإصدارات (Releases)** | صفحة على GitHub مرتبطة بوسم، فيها شرح التغييرات وملفات للتحميل |

**القاعدة الذهبية:** رقم الإصدار يعيش في **الوسم**، وليس في **اسم الملف**. الملف يبقى `app.py` أو `colaba.py` دائمًا، ويتغيّر محتواه بين الإصدارات.

---

## 2) الشكل النهائي للمستودع

```
المستودع: colba
│
├── الفرع main              ← الإصدار الحالي (تطبيق الويب) فقط
│     └── وسم v1.0.0، ثم v1.0.1، v1.1.0 ... مستقبلًا
│
└── الفرع legacy/desktop    ← تاريخ برنامج سطح المكتب القديم
      ├── وسم v0.1.3
      ├── وسم v0.1.4
      ├── ...
      └── وسم v0.1.9
```

- **الزائر** يفتح المستودع فيرى الإصدار الحالي نظيفًا.
- **المهتم بالتاريخ** يدخل الفرع `legacy/desktop` أو صفحة Releases.
- **Render** يراقب الفرع `main` فقط، فلا تتأثر النسخة المنشورة بأي شيء في الفروع الأخرى.

---

## 3) نظام ترقيم الإصدارات (Semantic Versioning)

الصيغة: **`vMAJOR.MINOR.PATCH`**، مثل `v1.2.3`.

| الجزء | متى يزيد | مثال |
|-------|----------|------|
| **PATCH** (الأخير) | إصلاح خطأ بدون ميزة جديدة | `v1.0.0` ← `v1.0.1` |
| **MINOR** (الأوسط) | إضافة ميزة جديدة متوافقة مع ما سبق | `v1.0.1` ← `v1.1.0` |
| **MAJOR** (الأول) | تغيير جذري، مثل تغيير هيكل قاعدة البيانات بحيث تحتاج البيانات القديمة ترحيلًا | `v1.4.0` ← `v2.0.0` |

**الاقتراح لمشروعك:**
- إصدارات سطح المكتب القديمة تبقى بأرقامها: `v0.1.3` إلى `v0.1.9` (الرقم `0` في البداية يعني مرحلة التجربة والتعلّم).
- تطبيق الويب أول إصدار مستقر له `v1.0.0` لأنه إعادة بناء كاملة وجُرّب فعليًا.

> 💡 الإصدار `0.1.8` غير موجود بين ملفاتك. هذا طبيعي، فلا تخترع له ملفًا.

---

## 4) التنفيذ لأول مرة (مرة واحدة فقط)

### الخطوة 0: التجهيز

- ثبّت **Git** وتأكد أنه يعمل: `git --version` (يفضّل إصدار 2.23 أو أحدث).
- اجمع ملفاتك في مكانين منفصلين على جهازك:
  - مجلد **الويب** (محتوى `colba-main`).
  - مجلد **القديم** (محتوى `1_colba` الذي يحوي `old_versions` و`colaba.0.1.7.py` و`colaba.0.1.9.py`).

> 🚫 **تنبيه خصوصية:** مجلد `name_DB` في الأرشيف القديم يحوي ملفات `.db` فيها بيانات منتجات (تبدو بيانات عمل حقيقية). **لا ترفعها إلى GitHub أبدًا.** سنستثنيها بملف `.gitignore`.

### الخطوة 1: تجهيز فرع `main` (تطبيق الويب)

إذا كان المستودع موجودًا على GitHub وفيه تطبيق الويب أصلًا (على الأغلب كذلك بحكم اسم الأرشيف `colba-main`)، فاستنسخه:

```bash
git clone https://github.com/Jaafar-Daoud-AC/colba.git
cd colba
```

ثم أضف الملفات الجديدة المرفقة (`README.md` و`README.en.md` و`CHANGELOG.md` و`RELEASE_GUIDE.md`) إلى جذر المشروع، وتأكد أن `.gitignore` يحوي هذه الأسطر:

```gitignore
__pycache__/
*.pyc
*.db
.env
venv/
.DS_Store
```

ثم احفظ التغييرات:

```bash
git add .
git commit -m "docs: add README, CHANGELOG and release guide"
git push origin main
```

### الخطوة 2: وسم الإصدار الحالي `v1.0.0`

افتح `CHANGELOG.md` وبدّل `YYYY-MM-DD` بتاريخ اليوم، ثم:

```bash
git add CHANGELOG.md
git commit -m "release: v1.0.0"
git tag -a v1.0.0 -m "COLBA v1.0.0: first web release"
git push origin main
git push origin v1.0.0
```

> الخيار `-a` ينشئ وسمًا **موثّقًا** (Annotated) يحمل رسالة واسمًا وتاريخًا. هذا هو المعتمد للإصدارات.

### الخطوة 3: إنشاء فرع الإصدارات القديمة `legacy/desktop`

هذا الفرع **يبدأ فارغًا** ولا يرث ملفات الويب، ثم نضيف إليه الإصدارات القديمة **بالترتيب من الأقدم إلى الأحدث**، كل إصدار في Commit مستقل بوسم خاص.

```bash
git switch --orphan legacy/desktop
```

سيصبح المجلد فارغًا من ملفات المشروع (ملفاتك محفوظة في الفرع `main`).

أنشئ `.gitignore` للفرع القديم أولًا:

```bash
printf "__pycache__/\n*.pyc\n*.db\n.env\nI/\nname_DB/\n" > .gitignore
```

الآن أضف كل إصدار. استبدل `PATH_OLD` بمسار مجلد القديم على جهازك، مثل `~/Downloads/1_colba`.

```bash
# --- v0.1.3 ---
cp PATH_OLD/old_versions/colaba.0.1.3.py colaba.py
git add .gitignore colaba.py
git commit -m "release: desktop v0.1.3"
git tag -a v0.1.3 -m "Desktop v0.1.3 (Tkinter + SQLite)"

# --- v0.1.4 ---
cp PATH_OLD/old_versions/colaba.0.1.4.py colaba.py
git add colaba.py
git commit -m "release: desktop v0.1.4"
git tag -a v0.1.4 -m "Desktop v0.1.4"

# --- v0.1.5 ---
cp PATH_OLD/old_versions/colaba.0.1.5.py colaba.py
git add colaba.py
git commit -m "release: desktop v0.1.5"
git tag -a v0.1.5 -m "Desktop v0.1.5"

# --- v0.1.6 ---
cp PATH_OLD/old_versions/colaba.0.1.6.py colaba.py
git add colaba.py
git commit -m "release: desktop v0.1.6"
git tag -a v0.1.6 -m "Desktop v0.1.6"

# --- v0.1.7 (يضيف matplotlib) ---
cp PATH_OLD/colaba.0.1.7.py colaba.py
cp PATH_OLD/requirements.txt requirements.txt
git add colaba.py requirements.txt
git commit -m "release: desktop v0.1.7"
git tag -a v0.1.7 -m "Desktop v0.1.7 (helper functions + matplotlib charts)"

# --- v0.1.9 ---
cp PATH_OLD/colaba.0.1.9.py colaba.py
git add colaba.py
git commit -m "release: desktop v0.1.9"
git tag -a v0.1.9 -m "Desktop v0.1.9 (multiple databases)"
```

> 📝 **حول الملف `db.py`:** النسخ من `0.1.3` إلى `0.1.6` تستورد وحدة `db` (`from db import Database`) غير موجودة في الأرشيف الذي أرسلتَه. هذا طبيعي في الإصدارات التجريبية، لكن اذكره في وصف الإصدار حتى لا يظن الزائر أن الملف معطوب.

أضف ملف `README.md` قصيرًا للفرع القديم يشرح أنه أرشيف:

```bash
cat > README.md <<'EOF'
# COLBA: Desktop versions (archive)

Historical desktop versions (Tkinter + SQLite) of COLBA, kept for reference.
The current version is the web app on the `main` branch:
https://github.com/Jaafar-Daoud-AC/colba

Each version is available as a tag: v0.1.3 ... v0.1.9
EOF
git add README.md
git commit -m "docs: add archive README"
```

ثم ارفع الفرع والوسوم:

```bash
git push -u origin legacy/desktop
git push origin --tags
```

أخيرًا ارجع إلى الفرع الرئيسي:

```bash
git switch main
```

### الخطوة 4: إنشاء صفحات Releases على GitHub

افعل هذا لكل وسم من واجهة GitHub:

1. افتح المستودع ← **Releases** ← **Draft a new release**.
2. من **Choose a tag** اختر الوسم (مثل `v1.0.0`).
3. اكتب **عنوانًا** (مثل: `COLBA v1.0.0: Web release`).
4. اكتب وصفًا (استعن بالقالب في القسم 7).
5. للإصدارات القديمة `v0.1.x`: فعّل **Set as a pre-release** (ولا تفعّل Latest).
6. للإصدار `v1.0.0`: فعّل **Set as the latest release**.
7. اضغط **Publish release**.

GitHub يضيف تلقائيًا ملفي **Source code (zip / tar.gz)** لكل إصدار، فيستطيع أي شخص تنزيل نسخة الإصدار كما كانت بالضبط.

**بديل بالأوامر** (إن ثبّتّ [GitHub CLI](https://cli.github.com)):

```bash
gh release create v1.0.0 --title "COLBA v1.0.0: Web release" --notes-file notes.md --latest
gh release create v0.1.9 --title "Desktop v0.1.9" --notes "Multiple databases support" --prerelease --latest=false
```

بعدها ستتحول شارة `release` في الـ README تلقائيًا لتعرض رقم آخر إصدار.

---

## 5) نشر إصدار جديد مستقبلًا (الروتين الثابت)

افترض أنك أضفت ميزة تصدير PDF وتريد نشر `v1.1.0`.

### أ) اعمل على فرع خاص بالميزة، وليس على `main` مباشرة

```bash
git switch main
git pull
git switch -c feature/pdf-export
# ... عدّل الكود واختبره ...
git add .
git commit -m "feat: add PDF export for reports"
git push -u origin feature/pdf-export
```

ثم افتح **Pull Request** على GitHub وادمجه في `main` (حتى لو كنت وحدك، فهذا يعطيك سجلًا مرتبًا).

### ب) قائمة التحقق قبل الإصدار ✅

- [ ] جرّبت التطبيق محليًا وعمل بدون أخطاء.
- [ ] إن عدّلتَ ملفات الواجهة (`app.js` أو `index.html` أو `styles.css`) فقد **رفعتَ رقم `CACHE_NAME` في `frontend/sw.js`** (مثل `colba-cache-v4` ← `colba-cache-v5`)، وإلا قد يرى المستخدمون النسخة القديمة من الكاش. وهذه ملاحظة كتبتَها بنفسك في الملف.
- [ ] إن غيّرتَ هيكل قاعدة البيانات فقد فكرتَ في كيفية ترحيل البيانات الموجودة (وهذا يعني غالبًا رفع رقم MAJOR).
- [ ] لا توجد أسرار في الكود (`DATABASE_URL`، كلمات مرور، ملفات `.env` أو `.db`).
- [ ] حدّثتَ `CHANGELOG.md`.

### ج) حدّث `CHANGELOG.md`

انقل ما تحت `[غير منشور]` إلى قسم جديد:

```markdown
## [1.1.0] - 2026-11-15

### أُضيف
- تصدير التقارير بصيغة PDF.

### أُصلح
- مشكلة ... في ...
```

وحدّث الروابط في آخر الملف:

```markdown
[غير منشور]: https://github.com/Jaafar-Daoud-AC/colba/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/Jaafar-Daoud-AC/colba/compare/v1.0.0...v1.1.0
```

### د) ضع الوسم وانشر

```bash
git switch main
git pull
git add CHANGELOG.md
git commit -m "release: v1.1.0"
git tag -a v1.1.0 -m "COLBA v1.1.0: PDF export"
git push origin main
git push origin v1.1.0
```

ثم أنشئ صفحة **Release** من GitHub كما في الخطوة 4، وفعّل **Latest**.

### هـ) النشر على Render

Render ينشر تلقائيًا عند كل `push` إلى `main`. تأكد من ضبط **Branch = main** في إعدادات الخدمة (Settings ← Build & Deploy)، فلا تؤثر الفروع الأخرى على التطبيق المنشور.

---

## 6) الإصلاح العاجل (Hotfix)

اكتشفت خطأً في النسخة المنشورة وتريد إصلاحه بسرعة؟

```bash
git switch main
git pull
git switch -c fix/stocktake-bug
# ... أصلح الخطأ ...
git commit -am "fix: correct stocktake calculation"
git switch main
git merge fix/stocktake-bug
# حدّث CHANGELOG ثم:
git commit -am "release: v1.0.1"
git tag -a v1.0.1 -m "Fix stocktake calculation"
git push origin main
git push origin v1.0.1
```

---

## 7) قالب وصف الإصدار (Release Notes)

```markdown
## ما الجديد
- ميزة ...
- تحسين ...

## الإصلاحات
- إصلاح ...

## ملاحظات
- أي تنبيه مهم (مثل: يتطلب تحديث قاعدة البيانات).

**السجل الكامل:** https://github.com/Jaafar-Daoud-AC/colba/compare/v1.0.0...v1.1.0
```

---

## 8) صياغة رسائل الـ Commit

استخدم بادئة تدل على نوع التغيير ليبقى السجل مقروءًا:

| البادئة | الاستخدام | مثال |
|---------|-----------|------|
| `feat:` | ميزة جديدة | `feat: add cash count screen` |
| `fix:` | إصلاح خطأ | `fix: wrong total in daily stats` |
| `docs:` | توثيق فقط | `docs: update README` |
| `refactor:` | إعادة تنظيم بدون تغيير السلوك | `refactor: split invoice logic` |
| `chore:` | أمور جانبية | `chore: update requirements` |
| `release:` | نقطة إصدار | `release: v1.1.0` |

---

## 9) مواقف شائعة وحلولها

**العودة لرؤية إصدار قديم:**
```bash
git checkout v0.1.7        # عرض الملفات كما كانت في ذلك الإصدار
git switch main            # الرجوع إلى الحاضر
```
أو نزّل **Source code (zip)** من صفحة الإصدار مباشرة.

**وضعتُ وسمًا بالخطأ (قبل نشره على GitHub):**
```bash
git tag -d v1.0.0
```

**وضعتُ وسمًا بالخطأ وقد رفعتُه:**
```bash
git tag -d v1.0.0
git push origin :refs/tags/v1.0.0
```
ثم احذف صفحة الـ Release من GitHub إن وُجدت، وأعد وسم الـ Commit الصحيح.

**رفعتُ كلمة مرور أو ملف `.db` بالخطأ:**
- غيّر كلمة مرور قاعدة البيانات فورًا من لوحة Supabase، لأن حذف الملف لاحقًا **لا يمحو** القيمة من سجل Git.
- ثم أزل الملف من المستودع وأضفه إلى `.gitignore`.

**أريد معرفة ما تغيّر بين إصدارين:**
```bash
git diff v1.0.0 v1.1.0 --stat
```
أو افتح على GitHub: `https://github.com/Jaafar-Daoud-AC/colba/compare/v1.0.0...v1.1.0`

---

## 10) ملخص سريع

| أريد أن ... | أفعل |
|-------------|------|
| إضافة ميزة | فرع `feature/...` ← PR ← دمج في `main` |
| نشر إصدار | تحديث CHANGELOG ← Commit ← `git tag -a vX.Y.Z` ← push ← Release على GitHub |
| حفظ إصدار قديم | فرع `legacy/...` + وسم لكل إصدار |
| إصلاح عاجل | فرع `fix/...` ← دمج ← رقم PATCH جديد |
| حماية الأسرار | `.gitignore` + متغيرات البيئة، ولا ترفع `.env` أو `*.db` أبدًا |

**المبادئ الثلاثة:** فرع `main` نظيف دائمًا · رقم الإصدار في الوسم وليس في اسم الملف · كل إصدار له سجل في `CHANGELOG.md` وصفحة Release.

</div>
