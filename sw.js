const CACHE = 'dbt-offline-v1';
const FILES = [
  './',
  './index.html',
  './trud.html',
  './stop.html',
  './pros_cons.html',
  './trud.pdf',
  './stop.pdf',
  './pros_cons.pdf'
];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES)));
});

self.addEventListener('fetch', e => {
  e.respondWith(
    caches.match(e.request).then(res => res || fetch(e.request))
  );
});
