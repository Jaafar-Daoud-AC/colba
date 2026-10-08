// خدمة عاملة بسيطة: تخزين الواجهة الثابتة مؤقتًا كي يفتح التطبيق حتى بدون اتصال
// ملاحظة مهمة: يجب رفع رقم CACHE_NAME في كل مرة تُعدَّل فيها app.js/index.html/
// styles.css حتى تُجبر كل الأجهزة (خصوصًا أندرويد/PWA المثبَّت) على تحميل
// النسخة الجديدة تلقائيًا بدل الاستمرار في عرض نسخة قديمة من الكاش المحلي.
const CACHE_NAME = "colba-cache-v4";
const STATIC_ASSETS = [
  "/",
  "/styles.css",
  "/app.js",
  "/manifest.json",
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(STATIC_ASSETS))
  );
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (event) => {
  const url = new URL(event.request.url);

  // لا نخزّن طلبات الـ API مؤقتًا؛ نريدها محدثة دائمًا من قاعدة البيانات
  if (url.pathname.startsWith("/api/")) {
    return;
  }

  // استراتيجية "الشبكة أولًا" لملفات الواجهة (HTML/CSS/JS): نحاول جلب أحدث
  // نسخة من السيرفر أولًا، ولا نلجأ للكاش إلا إذا فشل الاتصال (بدون إنترنت).
  // هذا يمنع مشكلة بقاء المستخدم عالقًا على نسخة قديمة من التطبيق حتى لو لم
  // يمسح الكاش يدويًا، لأن أي تحديث جديد يصل فورًا طالما هناك اتصال بالشبكة.
  event.respondWith(
    fetch(event.request)
      .then((response) => {
        const clone = response.clone();
        caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
        return response;
      })
      .catch(() => caches.match(event.request))
  );
});
