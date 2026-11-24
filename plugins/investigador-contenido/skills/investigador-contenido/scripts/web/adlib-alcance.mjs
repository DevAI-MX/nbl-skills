// Alcance en la UE (panel "Transparencia de la UE") de anuncios de la Biblioteca de Meta, sin sesión.
// Solo existe para anuncios entregados en la Unión Europea; fuera de la UE no hay alcance público.
// USO: node adlib-alcance.mjs <ids.json: ["<ad_archive_id>", ...]> <salida.json>   (retoma; FORCE=1 rehace)
import fs from 'node:fs';
import { cargarPlaywright, opcionesDeLanzamiento, perfilTemporal, UA_ESCRITORIO } from './navegador-local.mjs';
import { alcanceUe } from './adlib-respuesta.mjs';

async function abrirPanelUe(page) {
  const detalles = page.getByText(/Ver detalles del anuncio|See ad details/).first();
  if (await detalles.count()) { await detalles.click().catch(() => {}); await page.waitForTimeout(5000); }
  const ue = page.getByText(/Transparencia de la UE|European Union transparency/).last();
  if (await ue.count()) { await ue.click().catch(() => {}); await page.waitForTimeout(3000); }
  return page.locator('[role=dialog]').last().innerText().catch(() => '');
}

async function main() {
  const [rutaIds, salida] = process.argv.slice(2);
  if (!rutaIds || !salida) { console.error('uso: node adlib-alcance.mjs <ids.json> <salida.json>'); process.exit(1); }
  const ids = JSON.parse(fs.readFileSync(rutaIds, 'utf8'));
  const res = fs.existsSync(salida) ? JSON.parse(fs.readFileSync(salida, 'utf8')) : {};
  const { chromium } = await cargarPlaywright();
  const ctx = await chromium.launchPersistentContext(perfilTemporal('adlib-alc-'),
    opcionesDeLanzamiento(process.env, { viewport: { width: 1280, height: 1400 }, locale: 'es-ES', userAgent: UA_ESCRITORIO }));
  const page = await ctx.newPage();
  let respuestas = [];
  page.on('response', async (r) => {
    if (!r.url().includes('/api/graphql')) return;
    const t = await r.text().catch(() => '');
    if (/eu_total_reach|age_country_gender_reach|transparency/i.test(t)) respuestas.push(t.split('\n')[0]);
  });
  for (const id of ids) {
    if (res[id] && !process.env.FORCE) continue;
    respuestas = [];
    try {
      await page.goto(`https://www.facebook.com/ads/library/?id=${encodeURIComponent(id)}`, { waitUntil: 'domcontentloaded', timeout: 45000 });
      await page.waitForTimeout(6000);
      const panel = await abrirPanelUe(page);
      res[id] = { ...alcanceUe(respuestas, panel), texto: panel.slice(0, 2500) };
      console.log(id, res[id].eu_total_reach);
    } catch (e) {
      res[id] = { error: e.message.slice(0, 120) };
      console.log(id, 'ERROR');
    }
    fs.writeFileSync(salida, JSON.stringify(res, null, 1));
  }
  await ctx.close();
}

main().then(() => process.exit(0), (e) => { console.error(e.message); process.exit(1); });
