// Copia la versión de siempre (un solo archivo HTML) dentro de la app, con su música.
// La web y la APK comparten exactamente el mismo juego: solo cambia el envoltorio.
import { copyFileSync, mkdirSync, existsSync, readdirSync, rmSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const aqui = dirname(fileURLToPath(import.meta.url));
const origen = resolve(aqui, '../../doble-llave.html');
const destino = resolve(aqui, '../www/index.html');

if (!existsSync(origen)) {
  console.error('No encuentro doble-llave.html en la raíz del proyecto.');
  process.exit(1);
}
mkdirSync(dirname(destino), { recursive: true });
copyFileSync(origen, destino);
console.log('Copiado doble-llave.html → www/index.html');

// La música la prepara herramientas/musica.mjs en musica/salida/ (la APK de GitHub Actions lo hace sola).
// Sin ella, la app funciona igual y cada escena sugiere qué poner.
const musica = resolve(aqui, '../../musica/salida');
const musicaDentro = resolve(aqui, '../www/musica');
rmSync(musicaDentro, { recursive: true, force: true });
if (existsSync(resolve(musica, 'disponibles.json'))) {
  mkdirSync(musicaDentro, { recursive: true });
  const archivos = readdirSync(musica).filter(f => f.endsWith('.ogg') || f === 'disponibles.json');
  for (const f of archivos) copyFileSync(resolve(musica, f), resolve(musicaDentro, f));
  console.log(`Música: ${archivos.length - 1} pistas → www/musica/`);
} else {
  console.log('Sin música preparada (node herramientas/musica.mjs): la APK irá sin ella y cada escena dirá qué poner.');
}
