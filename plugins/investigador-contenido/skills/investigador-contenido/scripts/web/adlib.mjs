// Biblioteca de anuncios de Meta, sin iniciar sesión, desde el navegador de investigación (CDP_PUERTO).
// Lee la respuesta GraphQL que la propia página pide (search_results_connection) mientras baja la lista.
//
//   node adlib.mjs <consultas.json> <carpeta_salida> [max_por_consulta=60]
//
// consultas.json: [{ "id": "kw_clase_gratis", "q": "clase gratis", "type": "keyword"|"phrase"|"page",
//                    "page_id": "<id>" (solo type=page), "country": "ALL"|"MX"|"BR", "status": "active"|"all" }]
// Salida: <carpeta>/<id>.json con { consulta, url, total_texto, anuncios: [...], fin }; cada anuncio lleva "rank"
// (orden por impresiones totales, de mayor a menor). Retoma: salta las consultas ya guardadas (FORCE=1 las rehace).
// NUNCA en paralelo con otra corrida en el mismo navegador. Código 3 = Facebook pide sesión o bloquea: detente.
// Para esperar a que termine, corre en serie; no esperes con pgrep -f adlib.mjs (el comando se encuentra a sí mismo).
import fs from 'node:fs';
import path from 'node:path';
import { urlCdpVerificada, CODIGO_ALERTA } from '../ig/config.mjs';
import { cargarPlaywright } from './navegador-local.mjs';
import { numerarSinRepetidos, pideSesionOBloquea, resultadosDeGraphql, resultadosIncrustados, totalDeTexto, urlDe } from './adlib-respuesta.mjs';

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const VUELTAS_MAX = 40;
const VUELTAS_QUIETAS = 4;

async function bajarLista(page, estado, max) {
  let quietas = 0, previo = -1;
  for (let i = 0; i < VUELTAS_MAX && estado.lote.length < max; i++) {
    await page.mouse.wheel(0, 3000);
    await sleep(2500 + Math.random() * 1500);
    quietas = estado.lote.length === previo ? quietas + 1 : 0;
    previo = estado.lote.length;
    if (estado.fin?.has_next_page === false || quietas >= VUELTAS_QUIETAS) break;
  }
}

async function correrConsulta(page, c, estado, max, carpeta) {
  estado.lote = []; estado.fin = null;
  const url = urlDe(c);
  console.log(`> ${c.id}: ${url}`);
  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 45000 });
  await sleep(7000);
  await bajarLista(page, estado, max);
  const incrustados = resultadosIncrustados(await page.content());
  const texto = (await page.locator('body').innerText().catch(() => '')) || '';
  if (pideSesionOBloquea(texto)) {
    await page.screenshot({ path: path.join(carpeta, `${c.id}_ALERTA.png`) }).catch(() => {});
    return { alerta: true };
  }
  const anuncios = numerarSinRepetidos([...incrustados.nodos, ...estado.lote]);
  const datos = { consulta: c, url, total_texto: totalDeTexto(texto), anuncios, fin: estado.fin || incrustados.fin };
  fs.writeFileSync(path.join(carpeta, `${c.id}.json`), JSON.stringify(datos, null, 1));
  console.log(`  ${anuncios.length} anuncios (${datos.total_texto || 'sin total'})`);
  return { alerta: false };
}

async function main() {
  const [rutaConsultas, carpeta, maxArg] = process.argv.slice(2);
  if (!rutaConsultas || !carpeta) { console.error('uso: node adlib.mjs <consultas.json> <carpeta_salida> [max]'); process.exit(1); }
  const max = parseInt(maxArg || '60', 10);
  const consultas = JSON.parse(fs.readFileSync(rutaConsultas, 'utf8'));
  fs.mkdirSync(carpeta, { recursive: true });
  const { chromium } = await cargarPlaywright();
  const browser = await chromium.connectOverCDP(urlCdpVerificada());
  const ctx = browser.contexts()[0];
  const page = await ctx.newPage();
  await (await ctx.newCDPSession(page)).send('Emulation.setFocusEmulationEnabled', { enabled: true });
  const estado = { lote: [], fin: null };
  page.on('response', async (r) => {
    if (!r.url().includes('/api/graphql')) return;
    const res = resultadosDeGraphql(await r.text().catch(() => ''));
    if (res) { estado.lote.push(...res.nodos); estado.fin = res.fin || estado.fin; }
  });
  for (const c of consultas) {
    if (fs.existsSync(path.join(carpeta, `${c.id}.json`)) && !process.env.FORCE) { console.log(`= ${c.id} ya existe, salto`); continue; }
    try {
      if ((await correrConsulta(page, c, estado, max, carpeta)).alerta) {
        console.log('  ALERTA: Facebook pide sesión o bloqueo temporal. Me detengo.');
        process.exit(CODIGO_ALERTA);
      }
    } catch (e) {
      console.log(`  error en ${c.id}: ${e.message}`);
    }
    await sleep(4000 + Math.random() * 4000);
  }
  await page.close();
}

main().then(() => process.exit(0), (e) => { console.error(e.message); process.exit(1); });
