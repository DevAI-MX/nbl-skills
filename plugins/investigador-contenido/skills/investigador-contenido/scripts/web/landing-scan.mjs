// Escanea landings de la competencia como las vería alguien que llega desde un anuncio en el celular.
// Navegador headless propio (perfil temporal, sin sesión, no toca el navegador personal). NO llena ni envía formularios.
//
// Por página guarda en <salida>/<slug>/: data.json (título, URL final, encabezados, botones, formularios y campos,
// videos, contador, siguiente paso, redirecciones y tecnología), page.html, shot.png (celular, página completa) y
// desktop.png (primera pantalla en escritorio). Además abre UNA vez las páginas de gracias del mismo dominio y una de pago.
//
// USO: node landing-scan.mjs <lista.json: [{ "url": "..." }]> <carpeta_salida> [concurrencia=3]   (FORCE=1 rehace)
import fs from 'node:fs';
import path from 'node:path';
import { cargarPlaywright, opcionesDeLanzamiento, perfilTemporal } from './navegador-local.mjs';
import { paginasParaSeguir, redirecciones, siguientePaso, slugDe, tecnologia } from './landing-lib.mjs';

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const UA_CELULAR = 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Mobile/15E148 Safari/604.1 Instagram 360.0.0.0';

// Corre dentro de la página.
function leerPagina() {
  const vis = (el) => { const r = el.getBoundingClientRect(); const s = getComputedStyle(el); return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none'; };
  const txt = (el) => (el.innerText || el.value || el.getAttribute('aria-label') || '').replace(/\s+/g, ' ').trim();
  const y = (el) => Math.round(el.getBoundingClientRect().top + scrollY);
  const encabezados = [...document.querySelectorAll('h1,h2,h3')].filter(vis).map((e) => ({ tag: e.tagName, texto: txt(e).slice(0, 300), y: y(e) }));
  const botones = [...document.querySelectorAll('a,button,input[type=submit],[role=button]')].filter(vis)
    .map((e) => ({ texto: txt(e).slice(0, 140), href: e.href || e.getAttribute('href') || null, y: y(e) })).filter((b) => b.texto || b.href).slice(0, 150);
  const formularios = [...document.querySelectorAll('form')].map((f) => ({
    action: f.getAttribute('action'), method: f.getAttribute('method'), y: y(f),
    campos: [...f.querySelectorAll('input,select,textarea')].filter((i) => i.type !== 'hidden')
      .map((i) => ({ tipo: i.type || i.tagName.toLowerCase(), nombre: i.name || i.id || '', placeholder: i.placeholder || '', requerido: i.required })),
    ocultos: [...f.querySelectorAll('input[type=hidden]')].map((i) => i.name).slice(0, 30),
  }));
  const medios = [...document.querySelectorAll('iframe,video')].map((e) => ({ tag: e.tagName, src: e.src || e.currentSrc || '', y: y(e) }));
  const cuerpo = document.body.innerText || '';
  const contador = /\b\d{1,2}\s*[:]\s*\d{2}\s*[:]\s*\d{2}\b|d[ií]as\s+horas\s+min|DIAS?\s*HORAS?|days\s+hours\s+min/i.test(cuerpo);
  return { encabezados, botones, formularios, medios, contador, texto: cuerpo.slice(0, 60000), alto: document.body.scrollHeight };
}

async function bajarHastaElFinal(page) {
  let alto = 0;
  for (let i = 0; i < 40; i++) {
    const nuevo = await page.evaluate(() => { window.scrollBy(0, 900); return document.body.scrollHeight; }).catch(() => 0);
    await sleep(350);
    const visto = await page.evaluate(() => window.scrollY + window.innerHeight).catch(() => 0);
    if (visto >= nuevo - 5 && nuevo === alto) break;
    alto = nuevo;
  }
  await page.evaluate(() => window.scrollTo(0, 0)).catch(() => {});
  await sleep(1200);
}

async function capturaEscritorio(browser, url, archivo) {
  const ctx = await browser.newContext({ viewport: { width: 1366, height: 900 } });
  try {
    const p = await ctx.newPage();
    await p.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await sleep(3500);
    await p.screenshot({ path: archivo });
  } finally {
    await ctx.close();
  }
}

async function escanear(ctx, browser, item, salida, seguir = true) {
  const { url } = item;
  const slug = slugDe(url);
  const dir = path.join(salida, slug);
  if (fs.existsSync(path.join(dir, 'data.json')) && !process.env.FORCE) return { url, slug, skip: true };
  fs.mkdirSync(dir, { recursive: true });
  const page = await ctx.newPage();
  const res = { url, slug, escaneado: new Date().toISOString(), meta: item };
  try {
    const r = await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 45000 });
    res.status = r ? r.status() : null;
    await page.waitForLoadState('networkidle', { timeout: 15000 }).catch(() => {});
    await sleep(3000);
    await bajarHastaElFinal(page);
    Object.assign(res, { url_final: page.url(), titulo: await page.title().catch(() => '') }, await page.evaluate(leerPagina));
    const html = await page.content();
    fs.writeFileSync(path.join(dir, 'page.html'), html);
    const scripts = await page.evaluate(() => [...document.scripts].map((s) => s.src).filter(Boolean)).catch(() => []);
    Object.assign(res, { tecnologia: tecnologia(html + '\n' + scripts.join('\n')), siguiente_paso: siguientePaso(html), redirecciones: redirecciones(html) });
    await page.screenshot({ path: path.join(dir, 'shot.png'), fullPage: true, timeout: 60000 }).catch((e) => { res.error_captura = e.message; });
    if (seguir) {
      res.paginas_gracias = [];
      for (const g of paginasParaSeguir(res.siguiente_paso, new URL(res.url_final || url).hostname)) {
        const sub = await escanear(ctx, browser, { url: g, origen: url }, salida, false).catch((e) => ({ url: g, error: e.message }));
        res.paginas_gracias.push({ url: g, slug: sub.slug, error: sub.error || null });
      }
    }
  } catch (e) {
    res.error = e.message;
  }
  fs.writeFileSync(path.join(dir, 'data.json'), JSON.stringify(res, null, 1));
  await capturaEscritorio(browser, url, path.join(dir, 'desktop.png')).catch(() => {});
  await page.close().catch(() => {});
  return { url, slug, error: res.error || null };
}

async function main() {
  const [rutaLista, salida, concurrencia = '3'] = process.argv.slice(2);
  if (!rutaLista || !salida) { console.error('uso: node landing-scan.mjs <lista.json> <salida> [concurrencia]'); process.exit(1); }
  const lista = JSON.parse(fs.readFileSync(rutaLista, 'utf8'));
  fs.mkdirSync(salida, { recursive: true });
  const { chromium } = await cargarPlaywright();
  const ctx = await chromium.launchPersistentContext(perfilTemporal('landing-scan-'), opcionesDeLanzamiento(process.env, {
    viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true, userAgent: UA_CELULAR, locale: 'es-MX',
  }));
  const browser = await chromium.launch(opcionesDeLanzamiento()); // aparte, para la captura de escritorio
  let siguiente = 0; const hechos = [];
  const trabajador = async () => {
    while (siguiente < lista.length) {
      const item = lista[siguiente++];
      const r = await escanear(ctx, browser, item, salida).catch((e) => ({ url: item.url, error: e.message }));
      hechos.push(r);
      console.log(`${hechos.length}/${lista.length} ${r.error ? 'ERROR ' + r.error.slice(0, 80) : (r.skip ? 'ya estaba' : 'ok')}  ${item.url}`);
    }
  };
  await Promise.all(Array.from({ length: parseInt(concurrencia, 10) }, trabajador));
  fs.writeFileSync(path.join(salida, '_resumen.json'), JSON.stringify(hechos, null, 1));
  await ctx.close();
  await browser.close();
}

main().then(() => process.exit(0), (e) => { console.error(e.message); process.exit(1); });
