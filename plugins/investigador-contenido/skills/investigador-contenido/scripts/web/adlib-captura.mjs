// Captura cómo se ve cada anuncio en la Biblioteca de Meta (sin sesión, headless con perfil temporal).
// Recorta la tarjeta que contiene "Identificador de la biblioteca"; si no la encuentra, guarda la pantalla.
// Si la página mezcla un anuncio de terceros y sale otra tarjeta, usa captura-simple.mjs con 1280 x 1600.
// USO: node adlib-captura.mjs <ids.json: [{"id":"<ad_archive_id>","archivo":"ruta.png"}]>
import fs from 'node:fs';
import { cargarPlaywright, opcionesDeLanzamiento, perfilTemporal, UA_ESCRITORIO } from './navegador-local.mjs';

const BOTONES_COOKIES = ['Rechazar cookies opcionales', 'Decline optional cookies'];

async function rechazarCookiesOpcionales(page) {
  for (const t of BOTONES_COOKIES) {
    const b = page.getByRole('button', { name: t });
    if (await b.count()) { await b.first().click().catch(() => {}); await page.waitForTimeout(800); return; }
  }
}

// Corre dentro de la página: caja de la tarjeta del anuncio.
function cajaDeTarjeta() {
  const el = [...document.querySelectorAll('span,div')].find((e) => /Identificador de la biblioteca|Library ID/.test(e.textContent || '') && e.children.length === 0);
  for (let n = el, i = 0; n && i < 12; n = n.parentElement, i++) {
    const r = n.getBoundingClientRect();
    if (r.height > 500 && r.width > 280 && r.width < 700) return { x: r.left + scrollX, y: r.top + scrollY, w: r.width, h: r.height };
  }
  return null;
}

async function main() {
  const [rutaLista] = process.argv.slice(2);
  if (!rutaLista) { console.error('uso: node adlib-captura.mjs <ids.json>'); process.exit(1); }
  const lista = JSON.parse(fs.readFileSync(rutaLista, 'utf8'));
  const { chromium } = await cargarPlaywright();
  const ctx = await chromium.launchPersistentContext(perfilTemporal('adlib-cap-'),
    opcionesDeLanzamiento(process.env, { viewport: { width: 1280, height: 1400 }, locale: 'es-MX', userAgent: UA_ESCRITORIO }));
  const page = await ctx.newPage();
  for (const x of lista) {
    try {
      await page.goto(`https://www.facebook.com/ads/library/?id=${encodeURIComponent(x.id)}`, { waitUntil: 'domcontentloaded', timeout: 45000 });
      await page.waitForTimeout(7000);
      await rechazarCookiesOpcionales(page);
      const caja = await page.evaluate(cajaDeTarjeta);
      if (caja) {
        await page.screenshot({ path: x.archivo, fullPage: true, clip: { x: Math.max(0, caja.x - 8), y: Math.max(0, caja.y - 8),
          width: Math.min(caja.w + 16, 1280), height: Math.min(caja.h + 16, 3000) } });
      } else {
        await page.screenshot({ path: x.archivo });
      }
      console.log(caja ? 'ok   ' : 'pant.', x.id, x.archivo);
    } catch (e) {
      console.log('ERROR', x.id, e.message.slice(0, 100));
    }
  }
  await ctx.close();
}

main().then(() => process.exit(0), (e) => { console.error(e.message); process.exit(1); });
