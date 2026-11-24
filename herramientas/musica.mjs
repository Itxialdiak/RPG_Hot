// Descarga y prepara la música de la app: Kevin MacLeod (incompetech.com), licencia CC BY 4.0.
//
//   node herramientas/musica.mjs                   deja las pistas en musica/salida/
//   node herramientas/musica.mjs --destino web/musica --destino app-android/www/musica
//
// Cada pista se baja una sola vez de incompetech.com, se iguala el volumen y se comprime a
// Opus (40 kb/s, unos 300 KB por minuto). musica/salida/ hace de caché: lo que ya está no se
// vuelve a bajar. Al final escribe musica/salida/disponibles.json, que es lo que lee la app:
// si una pista no se pudo bajar, la app simplemente no la usa.
// Necesita ffmpeg. Con MUSICA_ORIGEN=/carpeta usa MP3 ya descargados (mismo nombre de archivo).
import { readFileSync, writeFileSync, existsSync, mkdirSync, copyFileSync, rmSync, statSync, readdirSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { dirname, resolve, basename } from 'node:path';
import { fileURLToPath } from 'node:url';
import { tmpdir } from 'node:os';

const raiz = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const cat = JSON.parse(readFileSync(resolve(raiz, 'musica/catalogo.json'), 'utf8'));
const salida = resolve(raiz, 'musica/salida');
const tmp = resolve(tmpdir(), 'doble-llave-musica');
mkdirSync(salida, { recursive: true });
mkdirSync(tmp, { recursive: true });

const destinos = [];
for (let k = 2; k < process.argv.length; k++) if (process.argv[k] === '--destino' && process.argv[k + 1]) destinos.push(resolve(raiz, process.argv[++k]));
const origen = process.env.MUSICA_ORIGEN ? resolve(process.env.MUSICA_ORIGEN) : null;

try { execFileSync('ffmpeg', ['-version'], { stdio: 'ignore' }); }
catch { console.error('Falta ffmpeg: instaladlo (en Ubuntu, sudo apt-get install ffmpeg) y repetid.'); process.exit(1); }

const espera = ms => new Promise(r => setTimeout(r, ms));
async function descargar(url, destino) {
  let ultimo;
  for (let intento = 1; intento <= 3; intento++) {
    try {
      const r = await fetch(url, { headers: { 'User-Agent': 'DobleLlave/1.0 (juego personal; descarga la musica una sola vez para llevarla dentro de la app, con creditos)' }, redirect: 'follow' });
      if (!r.ok) throw new Error('HTTP ' + r.status);
      const b = Buffer.from(await r.arrayBuffer());
      if (b.length < 100_000) throw new Error('archivo demasiado pequeño (' + b.length + ' bytes)');
      writeFileSync(destino, b);
      return;
    } catch (e) { ultimo = e; await espera(1500 * intento); }
  }
  throw ultimo;
}
function duracion(f) {
  const s = execFileSync('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of', 'default=nw=1:nk=1', f]).toString().trim();
  return Math.round(parseFloat(s) || 0);
}

const ok = [], dur = {}, fallos = [];
let bajadas = 0;
for (const [id, p] of Object.entries(cat.pistas)) {
  const ogg = resolve(salida, id + '.ogg');
  if (existsSync(ogg) && statSync(ogg).size > 20_000) { ok.push(id); dur[id] = duracion(ogg); continue; }
  const mp3 = resolve(tmp, id + '.mp3');
  try {
    if (origen) copyFileSync(resolve(origen, decodeURIComponent(basename(new URL(p.url).pathname))), mp3);
    else { if (bajadas++) await espera(700); await descargar(p.url, mp3); }
    execFileSync('ffmpeg', ['-hide_banner', '-loglevel', 'error', '-y', '-i', mp3, '-vn',
      '-af', 'loudnorm=I=-18:TP=-1.5:LRA=11', '-ar', '48000', '-ac', '2',
      '-c:a', 'libopus', '-b:a', '40k', '-vbr', 'on', '-application', 'audio',
      '-map_metadata', '-1', '-metadata', 'title=' + p.t, '-metadata', 'artist=' + p.a,
      '-metadata', 'comment=' + cat.licencia.corto + ', incompetech.com', ogg]);
    ok.push(id); dur[id] = duracion(ogg);
    console.log('  ✓ ' + p.t);
  } catch (e) {
    fallos.push(p.t + ': ' + (e.message || e));
    try { rmSync(ogg, { force: true }); } catch {}
  } finally {
    try { rmSync(mp3, { force: true }); } catch {}
  }
}

const orden = Object.keys(cat.pistas).filter(id => ok.includes(id));
writeFileSync(resolve(salida, 'disponibles.json'), JSON.stringify({ pistas: orden, dur, licencia: cat.licencia.corto, generado: new Date().toISOString() }));
const peso = orden.reduce((t, id) => t + statSync(resolve(salida, id + '.ogg')).size, 0);
console.log(`Música: ${orden.length} de ${Object.keys(cat.pistas).length} pistas listas, ${(peso / 1048576).toFixed(1)} MB.`);
if (fallos.length) console.log('No se pudieron preparar (la app las saltará):\n  ' + fallos.join('\n  '));

for (const d of destinos) {
  rmSync(d, { recursive: true, force: true });
  mkdirSync(d, { recursive: true });
  for (const f of readdirSync(salida)) if (f.endsWith('.ogg') || f === 'disponibles.json') copyFileSync(resolve(salida, f), resolve(d, f));
  console.log('Copiada a ' + d);
}
