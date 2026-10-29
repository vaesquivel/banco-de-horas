const CACHE = 'bdh-v25';
const URLS  = ['./', './index.html', './manifest.json', './icon.svg', './icon-180.png', './icon-512.png'];

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

/* ── PUSH: notificações com o app fechado ── */
self.addEventListener('push', ev => {
  let d = {};
  try { d = ev.data ? ev.data.json() : {}; } catch (e) {}
  const n = (d && (d.data || d.notification)) || {};
  ev.waitUntil(self.registration.showNotification(n.title || 'Banco de Horas', {
    body: n.body || '',
    icon: './icon-180.png',
    badge: './icon-180.png',
    tag: n.tag || 'bdh-aviso'
  }));
});
self.addEventListener('notificationclick', ev => {
  ev.notification.close();
  ev.waitUntil(clients.matchAll({ type: 'window', includeUncontrolled: true }).then(list => {
    for (const c of list) { if ('focus' in c) return c.focus(); }
    return clients.openWindow('./');
  }));
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
