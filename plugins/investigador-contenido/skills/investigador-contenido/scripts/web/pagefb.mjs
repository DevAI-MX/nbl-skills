// Saca el page_id de páginas públicas de Facebook leyendo su HTML, sin sesión, en el navegador de investigación.
// Sirve para las consultas type=page de adlib.mjs: el autocompletado de la Biblioteca da 404 sin sesión.
// Ojo: las páginas tipo perfil personal pueden no dar el id de anunciante.
//   node pagefb.mjs <urls.json: ["https://www.facebook.com/<pagina>", ...]> <salida.json>
import fs from 'node:fs';
import { urlCdpVerificada } from '../ig/config.mjs';
import { cargarPlaywright } from './navegador-local.mjs';
import { idsDePagina, tituloDe } from './pagina-fb.mjs';

async function main() {
  const [rutaUrls, salida] = process.argv.slice(2);
  if (!rutaUrls || !salida) { console.error('uso: node pagefb.mjs <urls.json> <salida.json>'); process.exit(1); }
  const urls = JSON.parse(fs.readFileSync(rutaUrls, 'utf8'));
  const { chromium } = await cargarPlaywright();
  const browser = await chromium.connectOverCDP(urlCdpVerificada());
  const page = await browser.contexts()[0].newPage();
  const out = {};
  for (const url of urls) {
    try {
      await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 45000 });
      await page.waitForTimeout(3500);
      const html = await page.content();
      out[url] = { titulo: tituloDe(html), ids: idsDePagina(html), final: page.url() };
      console.log(url, '->', out[url].titulo.slice(0, 60), '|', out[url].ids.join(','));
    } catch (e) {
      out[url] = { error: String(e).slice(0, 200) };
      console.log(url, '-> ERROR', String(e).slice(0, 100));
    }
    await page.waitForTimeout(1500);
  }
  fs.writeFileSync(salida, JSON.stringify(out, null, 1));
  await page.close();
}

main().then(() => process.exit(0), (e) => { console.error(e.message); process.exit(1); });
