// Lector público de carruseles, SIN sesión: baja todas las láminas y el caption leyendo el JSON incrustado en el HTML.
// Es la vía de respaldo (o la principal cuando no hay navegador de investigación con sesión). La principal con sesión es
// ig/fichas-por-codigo.mjs + guiones/medios.py bajar. Ojo: a veces no baja nada (post privado, restringido por edad,
// carrusel que llega vacío o Instagram cambió el HTML); ese post sale en "failed" y hay que probar la otra vía.
//
// USO: node carrusel-publico.mjs "<url>" ["<url2>" ...] [--out <carpeta>]   (por omisión ./carruseles)
// Salida: <carpeta>/<codigo>/slide-NN.jpg + meta.json, y <carpeta>/_batch.json con { done, failed }.
import fs from 'node:fs';
import path from 'node:path';
import { cargarPlaywright, opcionesDeLanzamiento, perfilTemporal } from './navegador-local.mjs';
import { bloquesJson, estadoDeDescarga, laminasDe, metaDe, nodoDelPost, shortcodeDe } from './carrusel-lib.mjs';

async function bajarLaminas(page, meta, laminas) {
  for (const l of laminas) {
    const registro = { slide: l.lamina, tipo: l.tipo, w: l.w, h: l.h, alt: l.alt, file: null };
    if (l.url) {
      const archivo = path.join(meta.dir, `slide-${String(l.lamina).padStart(2, '0')}.jpg`);
      try {
        fs.writeFileSync(archivo, await (await page.request.get(l.url, { timeout: 30000 })).body());
        registro.file = archivo;
      } catch (e) {
        registro.error = e.message;
      }
    }
    meta.slides.push(registro);
  }
}

async function leerPost(page, url, raiz) {
  const codigo = shortcodeDe(url);
  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 45000 });
  await page.waitForTimeout(5000);
  const nodo = nodoDelPost(bloquesJson(await page.content()), codigo);
  if (!nodo) throw new Error('el HTML no trae el post (privado, restringido por edad, vacío o Instagram cambió el HTML)');
  const meta = metaDe(nodo, url, path.join(raiz, codigo));
  fs.mkdirSync(meta.dir, { recursive: true });
  await bajarLaminas(page, meta, laminasDe(nodo));
  fs.writeFileSync(path.join(meta.dir, 'meta.json'), JSON.stringify(meta, null, 2));
  const estado = estadoDeDescarga(meta);
  if (!estado.ok) throw new Error(`no se bajó ninguna de sus ${meta.total_slides} láminas`);
  return { ...meta, ...estado };
}

async function main() {
  const args = process.argv.slice(2);
  const urls = args.filter((a) => a.startsWith('http'));
  const raiz = args.includes('--out') ? args[args.indexOf('--out') + 1] : path.join(process.cwd(), 'carruseles');
  if (!urls.length) { console.error('uso: node carrusel-publico.mjs "<url>" ["<url2>" ...] [--out <carpeta>]'); process.exit(1); }
  fs.mkdirSync(raiz, { recursive: true });
  const { chromium } = await cargarPlaywright();
  const ctx = await chromium.launchPersistentContext(perfilTemporal('carrusel-publico-'),
    opcionesDeLanzamiento(process.env, { viewport: { width: 1280, height: 1100 } }));
  const page = ctx.pages()[0] || await ctx.newPage();
  const done = [], failed = [];
  for (const url of urls) {
    try {
      const m = await leerPost(page, url, raiz);
      done.push({ shortcode: m.shortcode, author: m.author, slides: m.total_slides, bajadas: m.bajadas, faltan: m.faltan });
      console.log(`OK    ${m.shortcode}  ${m.bajadas} de ${m.total_slides} láminas  @${m.author}`);
    } catch (e) {
      failed.push({ url, error: e.message });
      console.log(`FALLO ${url}  -> ${e.message}`);
    }
  }
  fs.writeFileSync(path.join(raiz, '_batch.json'), JSON.stringify({ done, failed }, null, 2));
  console.log(`\n${done.length} ok / ${failed.length} fallidos`);
  await ctx.close();
}

main().then(() => process.exit(0), (e) => { console.error(e.message); process.exit(1); });
