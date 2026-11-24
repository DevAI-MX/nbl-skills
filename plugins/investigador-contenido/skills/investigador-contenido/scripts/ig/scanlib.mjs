// Escaneo de un perfil en el navegador de investigación: /reels/ (reels con vistas) o el feed (carruseles).
// Escucha las respuestas GraphQL mientras baja la cuadrícula y guarda <ESCANEOS_DIR>/<handle>[.feed].json.
import fs from 'node:fs';
import path from 'node:path';
import { sleep, jitter, AlertaDeSesion, cuerpoComoJson } from './lib.mjs';
import { armarEscaneo, codigoDeEnlace, encadenadosDeRespuesta, esDelPerfil, fusionar, perfilDeRespuesta,
  publicacionesDeRespuesta } from './escaneo-respuesta.mjs';

const VUELTAS_QUIETAS_PARA_PARAR = 3;

// Corre dentro de la página: devuelve cabecera, avisos y enlaces de la cuadrícula.
const LEER_DOM = `(() => {
  const h = document.querySelector('header'); const htext = h ? h.innerText : '';
  const titles = h ? [...h.querySelectorAll('[title]')].map(x => x.getAttribute('title')) : [];
  const body = (document.body.innerText||'').slice(0,1500);
  const notfound = /Lo sentimos, esta p|Sorry, this page isn|no est\\u00e1 disponible|isn.t available/i.test(body);
  const checkpoint = /challenge|checkpoint/i.test(location.href) || /Confirma que eres t|Tu cuenta ha sido suspendida|We suspended/i.test(body.slice(0,500));
  const login = /accounts\\/login/.test(location.href);
  const privado = /Esta cuenta es privada|This account is private/i.test(body);
  const reels = [...document.querySelectorAll('a[href*="/reel/"], a[href*="/p/"]')]
    .map(a => ({ href: a.getAttribute('href'), text: (a.innerText||'').trim().replace(/\\n+/g,' | ') }));
  return { url: location.href, htext, titles, notfound, checkpoint, login, privado, reels };
})()`;

function escucharRespuestas(page, handle, estado) {
  const pendientes = new Set();
  page.on('Network.responseReceived', (p) => {
    const u = p.response?.url || '';
    if (/graphql|api\/v1/.test(u) && /(json|javascript)/.test(p.response.mimeType || '')) pendientes.add(p.requestId);
  });
  page.on('Network.loadingFinished', async (p) => {
    if (!pendientes.delete(p.requestId)) return;
    let cuerpo;
    try {
      const b = await page.send('Network.getResponseBody', { requestId: p.requestId }, 10000);
      cuerpo = b.base64Encoded ? Buffer.from(b.body, 'base64').toString() : b.body;
    } catch { return; } // el cuerpo ya no está: esa tanda se pierde, no se inventa
    const datos = cuerpoComoJson(cuerpo);
    if (!datos) return;
    estado.seguidoresApi = perfilDeRespuesta(datos, handle) ?? estado.seguidoresApi;
    for (const pub of publicacionesDeRespuesta(datos)) estado.porCodigo.set(pub.code, fusionar(estado.porCodigo.get(pub.code), pub));
    const encadenados = encadenadosDeRespuesta(datos);
    if (encadenados.length) estado.encadenados = encadenados;
  });
}

function absorber(dom, handle, visibles) {
  for (const { href, text } of dom.reels) {
    const codigo = codigoDeEnlace(href);
    if (codigo && esDelPerfil(href, handle)) visibles.set(codigo, text);
  }
}

async function bajarCuadricula(page, handle, maxScrolls, objetivos, visibles) {
  let dom = await page.evaluate(LEER_DOM);
  if (dom.login || dom.checkpoint) throw new AlertaDeSesion(`${dom.login ? 'LOGIN' : 'CHECKPOINT'} ${dom.url}`);
  absorber(dom, handle, visibles);
  let quietas = 0;
  for (let i = 0; i < maxScrolls && quietas < VUELTAS_QUIETAS_PARA_PARAR; i++) {
    if (objetivos.size && [...objetivos].every((c) => visibles.has(c))) break;
    const antes = visibles.size;
    await page.wheel(2400);
    await jitter(1500, 2200);
    dom = await page.evaluate(LEER_DOM);
    absorber(dom, handle, visibles);
    quietas = visibles.size === antes ? quietas + 1 : 0;
  }
  return dom;
}

export async function scanReels(page, handle, { maxScrolls = 8, objetivos = new Set(), feed = false, carpeta }) {
  const estado = { porCodigo: new Map(), seguidoresApi: null, encadenados: [] };
  const visibles = new Map();
  await page.send('Network.enable');
  escucharRespuestas(page, handle, estado);
  await page.send('Page.bringToFront').catch(() => {});
  // En headless la cuadrícula de /reels/ no carga sin emulación de foco.
  await page.send('Emulation.setFocusEmulationEnabled', { enabled: true }).catch(() => {});
  try {
    await page.goto(`https://www.instagram.com/${handle}/${feed ? '' : 'reels/'}`, { timeout: 30000 });
    await sleep(3500);
    const dom = await bajarCuadricula(page, handle, maxScrolls, objetivos, visibles);
    const escaneo = armarEscaneo({ handle, feed, dom, visibles, ...estado, fecha: new Date().toISOString() });
    fs.mkdirSync(carpeta, { recursive: true });
    fs.writeFileSync(path.join(carpeta, `${handle}${feed ? '.feed' : ''}.json`), JSON.stringify(escaneo, null, 1));
    return escaneo;
  } finally {
    page.off('Network.responseReceived');
    page.off('Network.loadingFinished');
  }
}
