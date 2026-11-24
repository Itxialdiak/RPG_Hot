// Doble Llave: funciona sin conexión. Versión afba38e05c
const CACHE = 'doble-llave-afba38e05c';
const ARCHIVOS = ["./","index.html","manifest.webmanifest","icono-180.png","icono-192.png","icono-512.png","icono-adaptable-512.png","doble-llave-carnaval-para-imprimir.pdf","doble-llave-bosque-para-imprimir.pdf","doble-llave-cotidiana-para-imprimir.pdf"];
self.addEventListener('install', e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(ARCHIVOS)).then(() => self.skipWaiting())); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  // la música va siempre por la red: pesa mucho y el navegador la pide a trozos (Range)
  if (new URL(e.request.url).pathname.includes('/musica/')) return;
  e.respondWith(caches.match(e.request, { ignoreSearch: true }).then(r => r || fetch(e.request)));
});
