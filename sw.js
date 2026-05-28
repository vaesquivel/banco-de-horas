const CACHE = 'bdh-v6';
const URLS  = ['./', './index.html', './manifest.json', './icon.svg'];

self.addEventListener('install', ev => {
  ev.waitUntil(
    caches.open(CACHE)
      .then(c => c.addAll(URLS))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', ev => {
  ev.waitUntil(
    caches.keys()
      .then(keys => Promise.all(
        keys.filter(k => k !== CACHE).map(k => caches.delete(k))
      ))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', ev => {
  if (ev.request.method !== 'GET') return;
  // Network first para o index.html — sempre pega versão mais recente
  if (ev.request.url.endsWith('index.html') || ev.request.url.endsWith('/')) {
    ev.respondWith(
      fetch(ev.request)
        .then(res => {
          const clone = res.clone();
          caches.open(CACHE).then(c => c.put(ev.request, clone));
          return res;
        })
        .catch(() => caches.match(ev.request))
    );
    return;
  }
  // Cache first para os demais arquivos
  ev.respondWith(
    caches.match(ev.request).then(cached => cached || fetch(ev.request))
  );
});
