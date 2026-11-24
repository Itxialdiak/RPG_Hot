// Construye la versión web instalable (PWA) en la carpeta web/:
// la misma app de un solo archivo, más manifiesto, service worker para jugar sin conexión,
// iconos y los PDF para imprimir. Lista para publicar, por ejemplo, en GitHub Pages.
import { readFileSync, writeFileSync, copyFileSync, existsSync, mkdirSync, readdirSync, rmSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const raiz = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const web = resolve(raiz, 'web');
mkdirSync(web, { recursive: true });

const pdfs = { carnaval: 'doble-llave-carnaval-para-imprimir.pdf', fantasia: 'doble-llave-bosque-para-imprimir.pdf', cotidiana: 'doble-llave-cotidiana-para-imprimir.pdf' };
const hay = Object.fromEntries(Object.entries(pdfs).filter(([, f]) => existsSync(resolve(raiz, 'salida', f))));
for (const f of Object.values(hay)) copyFileSync(resolve(raiz, 'salida', f), resolve(web, f));

// La música (herramientas/musica.mjs la deja en musica/salida/). No se sube al repositorio:
// el flujo de GitHub Pages la prepara antes de publicar.
const musica = resolve(raiz, 'musica/salida'), musicaWeb = resolve(web, 'musica');
let pistas = 0;
if (existsSync(resolve(musica, 'disponibles.json'))) {
  rmSync(musicaWeb, { recursive: true, force: true });
  mkdirSync(musicaWeb, { recursive: true });
  for (const f of readdirSync(musica).filter(f => f.endsWith('.ogg') || f === 'disponibles.json')) { copyFileSync(resolve(musica, f), resolve(musicaWeb, f)); if (f.endsWith('.ogg')) pistas++; }
}

let html = readFileSync(resolve(raiz, 'doble-llave.html'), 'utf8');
html = html.replace('<link rel="icon" href="data:,">',
  '<link rel="icon" href="icono-192.png">\n<link rel="apple-touch-icon" href="icono-180.png">\n<link rel="manifest" href="manifest.webmanifest">\n<meta name="mobile-web-app-capable" content="yes">\n<meta name="apple-mobile-web-app-title" content="Doble Llave">');
html = html.replace('<script>\n\'use strict\';', '<script>window.DL_PDFS = ' + JSON.stringify(hay) + ';</script>\n<script>\n\'use strict\';');
html = html.replace('</body>', '<script>if(\'serviceWorker\' in navigator && !window.Capacitor && (location.protocol === \'https:\' || location.hostname === \'localhost\')) navigator.serviceWorker.register(\'sw.js\').catch(() => {});</script>\n</body>');
writeFileSync(resolve(web, 'index.html'), html);

writeFileSync(resolve(web, 'manifest.webmanifest'), JSON.stringify({
  name: 'Doble Llave', short_name: 'Doble Llave', lang: 'es',
  description: 'Juegos de rol para dos, para encender una noche poco a poco.',
  start_url: './', scope: './', display: 'standalone', orientation: 'portrait',
  background_color: '#140610', theme_color: '#1a0811',
  icons: [
    { src: 'icono-192.png', sizes: '192x192', type: 'image/png' },
    { src: 'icono-512.png', sizes: '512x512', type: 'image/png' },
    { src: 'icono-adaptable-512.png', sizes: '512x512', type: 'image/png', purpose: 'maskable' }
  ]
}, null, 2));

const archivos = ['./', 'index.html', 'manifest.webmanifest', 'icono-180.png', 'icono-192.png', 'icono-512.png', 'icono-adaptable-512.png', ...Object.values(hay)];
const version = createHash('sha256').update(html).digest('hex').slice(0, 10);
writeFileSync(resolve(web, 'sw.js'), `// Doble Llave: funciona sin conexión. Versión ${version}
const CACHE = 'doble-llave-${version}';
const ARCHIVOS = ${JSON.stringify(archivos)};
self.addEventListener('install', e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(ARCHIVOS)).then(() => self.skipWaiting())); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  // la música va siempre por la red: pesa mucho y el navegador la pide a trozos (Range)
  if (new URL(e.request.url).pathname.includes('/musica/')) return;
  e.respondWith(caches.match(e.request, { ignoreSearch: true }).then(r => r || fetch(e.request)));
});
`);
console.log('web/ lista: index.html, manifiesto, service worker, iconos' + (Object.keys(hay).length ? ', PDF' : '') + (pistas ? ' y ' + pistas + ' pistas de música' : ' (sin música)'));
