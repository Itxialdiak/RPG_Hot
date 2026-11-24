// Exporta los datos del juego (los mismos que usa la app) a JSON, para generar los PDF.
const fs = require('fs'), vm = require('vm');
const code = fs.readFileSync(__dirname + '/datos.js', 'utf8');
const ctx = {console, Math, Date, JSON, String, Object, Array, setTimeout, clearTimeout,
  window: {}, document: {addEventListener(){}, getElementById(){return null}, querySelector(){return null}},
  navigator: {}, localStorage: {getItem(){return null}, setItem(){}, removeItem(){}}};
ctx.globalThis = ctx;
vm.createContext(ctx);
vm.runInContext(code, ctx);
fs.writeFileSync(__dirname + '/datos.json', JSON.stringify(ctx.__DATA, null, 1));
console.log('ok', Object.keys(ctx.__DATA));
