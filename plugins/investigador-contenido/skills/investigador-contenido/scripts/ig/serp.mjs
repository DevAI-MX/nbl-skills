// Búsqueda por palabra clave con el buscador nativo de Instagram, en el navegador de investigación.
// USO: node serp.mjs <consultas.json> <salida.json> [paginas=2]
//   Abre /explore/search/keyword/?q= y lee la respuesta GraphQL; cada página extra es un scroll.
//   El buscador solo lee captions: frases de 3 o más palabras devuelven 0, usa 2 palabras.
//   No trae vistas (plays queda en null): las vistas salen del escaneo de /reels/ (batchscan.mjs).
//   Retoma: las consultas ya hechas en <salida.json> se saltan. Código 3 = sesión vencida o checkpoint.
import fs from 'node:fs';
import { connect, jitter, AlertaDeSesion, cuerpoComoJson } from './lib.mjs';
import { esRespuestaDeBusqueda, mediosDeBusqueda } from './serp-respuesta.mjs';
import { CODIGO_ALERTA } from './config.mjs';
import { esPrincipal } from './arranque.mjs';

const URL_BUSQUEDA = 'https://www.instagram.com/explore/search/keyword/?q=';

function leerBase(ruta) {
  return fs.existsSync(ruta) ? JSON.parse(fs.readFileSync(ruta, 'utf8')) : { done: {}, media: {} };
}

function escucharRespuestasDeBusqueda(pagina, alRecibir) {
  const pendientes = new Set();
  pagina.on('Network.responseReceived', (e) => { if (/\/graphql/.test(e.response?.url || '')) pendientes.add(e.requestId); });
  pagina.on('Network.loadingFinished', async (e) => {
    if (!pendientes.delete(e.requestId)) return;
    try {
      const r = await pagina.send('Network.getResponseBody', { requestId: e.requestId }, 10000);
      const json = cuerpoComoJson(r.base64Encoded ? Buffer.from(r.body, 'base64').toString() : r.body);
      if (esRespuestaDeBusqueda(json)) alRecibir(json);
    } catch { /* el cuerpo ya no está disponible: esa página se pierde, no se inventa */ }
  });
}

async function verificarSesion(pagina) {
  const url = await pagina.evaluate('location.href');
  if (/accounts\/login|challenge|checkpoint/.test(url)) throw new AlertaDeSesion(url);
}

export function guardarMedios(base, medios) {
  for (const m of medios) {
    const previo = base.media[m.code];
    base.media[m.code] = { ...m, queries: [...new Set([...(previo?.queries || []), ...m.queries])] };
  }
}

async function buscar(pagina, consulta, paginas, base) {
  let recibidos = 0;
  pagina.off('Network.responseReceived'); pagina.off('Network.loadingFinished');
  escucharRespuestasDeBusqueda(pagina, (json) => {
    const medios = mediosDeBusqueda(json, consulta);
    guardarMedios(base, medios); recibidos += medios.length;
  });
  await pagina.goto(URL_BUSQUEDA + encodeURIComponent(consulta));
  await jitter(6000, 8000);
  await verificarSesion(pagina);
  for (let p = 1; p < paginas; p++) { await pagina.wheel(2600); await jitter(3500, 5000); }
  return recibidos;
}

async function main() {
  const [rutaConsultas, rutaSalida, paginas = '2'] = process.argv.slice(2);
  if (!rutaConsultas || !rutaSalida) { console.error('uso: node serp.mjs <consultas.json> <salida.json> [paginas]'); process.exit(1); }
  const consultas = JSON.parse(fs.readFileSync(rutaConsultas, 'utf8'));
  const base = leerBase(rutaSalida);
  const pagina = await connect(process.env.TARGET);
  await pagina.send('Emulation.setFocusEmulationEnabled', { enabled: true });
  await pagina.send('Network.enable');
  for (const consulta of consultas) {
    if (base.done[consulta] !== undefined) continue;
    try {
      base.done[consulta] = await buscar(pagina, consulta, parseInt(paginas, 10), base);
    } catch (e) {
      fs.writeFileSync(rutaSalida, JSON.stringify(base));
      if (e.alerta) { console.error(e.message); process.exit(CODIGO_ALERTA); }
      console.error(consulta, 'ERR', e.message);
      continue;
    }
    fs.writeFileSync(rutaSalida, JSON.stringify(base));
    console.error(`${consulta}: ${base.done[consulta]}`);
    await jitter(3000, 5000);
  }
  console.error('total media', Object.keys(base.media).length);
}

if (esPrincipal(import.meta.url)) main().then(() => process.exit(0), (e) => { console.error(e.message); process.exit(1); });
