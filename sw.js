const CACHE = 'dbt-offline-v6';
const FILES = [
  './',
  './index.html',
  './diary.html',
  './trud.html',
  './stop.html',
  './pros_cons.html',
  './problem_solving.html',
  './trud.pdf',
  './stop.pdf',
  './pros_cons.pdf',
  './problem_solving.pdf',
  './manifest.json',
  './icon.png',
  './favicon.png'
];

self.addEventListener('install', e => {
  self.skipWaiting();
  e.waitUntil(
    caches.open(CACHE).then(cache => cache.addAll(FILES))
  );
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', e => {
  // Кэшируем только GET-запросы своего домена
  if (e.request.method !== 'GET') return;

  e.respondWith(
    caches.open(CACHE).then(cache => {
      return cache.match(e.request).then(cachedResponse => {
        // Фоновый запрос в сеть для обновления кэша
        const fetchPromise = fetch(e.request)
          .then(networkResponse => {
            // Сохраняем в кэш только успешные ответы
            if (networkResponse && networkResponse.status === 200) {
              cache.put(e.request, networkResponse.clone());
            }
            return networkResponse;
          })
          .catch(() => {
            // Если сети нет вообще и в кэше пусто — отдаём главную как запасной вариант
            if (e.request.mode === 'navigate') {
              return cache.match('./index.html');
            }
          });

        // Если есть в кэше — отдаём мгновенно, иначе ждём сеть
        return cachedResponse || fetchPromise;
      });
    })
  );
});
