#!/usr/bin/env node
/**
 * bajar_referencia.mjs: baja todas las láminas de uno o varios carruseles de Instagram, su caption y sus
 * datos, para transcribirlos leyendo las imágenes.
 *
 * Uso:
 *   node bajar_referencia.mjs "<url>" ["<url2>" ...] [--out <carpeta>] [--cdp <url> | --perfil <carpeta>]
 *
 * Dos vías:
 * - Ficha con sesión (--cdp): se conecta a un navegador de investigación aparte donde ya hay una sesión de
 *   Instagram (nunca el navegador personal) y pide /api/v1/media/<pk>/info/. Si Instagram pide sesión o
 *   muestra una alerta, sale con código 3 y no reintenta.
 * - Lector sin sesión (por defecto): lee el JSON que trae el HTML público del post (el nodo cuyo `code` es
 *   el shortcode); carousel_media[] da la cuenta exacta e image_versions2.candidates[0].url la imagen
 *   completa. Con --perfil usa un perfil persistente (por ejemplo de Brave), como el lector original.
 *
 * Con un enlace guarda en --out (por defecto ./referencia); con varios, una carpeta por shortcode y un
 * _batch.json con los que salieron y los que fallaron. Un carrusel del que no baja ninguna lámina cuenta
 * como fallido. BRAVE_PATH o BROWSER_PATH eligen el navegador; si no, usa el Chromium de Playwright.
 * Busca Playwright en node_modules de la carpeta donde lo corres.
 */
import { pathToFileURL } from 'node:url';
import { resolve, join } from 'node:path';
import { mkdir, writeFile } from 'node:fs/promises';

const ALFABETO = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_';
const IG_APP_ID = '936619743392459'; // id público de la app web de Instagram, no es una clave
const ALERTA = /login_required|checkpoint_required|challenge_required|feedback_required/;
const SALIDA_ALERTA = 3;
const USO = 'Uso: node bajar_referencia.mjs "<url>" ["<url2>" ...] [--out <carpeta>] [--cdp <url> | --perfil <carpeta>]';

export class ErrorDeReferencia extends Error {}
export class AlertaDeSesion extends ErrorDeReferencia {}

export function shortcodeDe(url) {
  const encontrado = String(url).match(/instagram\.com\/(?:[\w.]+\/)?(?:p|reel|tv)\/([A-Za-z0-9_-]+)/);
  if (!encontrado) throw new ErrorDeReferencia(`no es el enlace de un post de Instagram: ${url}`);
  return encontrado[1];
}

export function pkDeCodigo(codigo) {
  return [...codigo].reduce((pk, letra) => {
    const valor = ALFABETO.indexOf(letra);
    if (valor < 0) throw new ErrorDeReferencia(`shortcode inválido: ${codigo}`);
    return pk * 64n + BigInt(valor);
  }, 0n).toString();
}

function tieneMedios(nodo) {
  return Boolean(nodo.carousel_media || nodo.image_versions2 || nodo.video_versions);
}

export function buscarNodos(valor, codigo, hallados = []) {
  if (Array.isArray(valor)) valor.forEach((v) => buscarNodos(v, codigo, hallados));
  else if (valor && typeof valor === 'object') {
    if (valor.code === codigo && tieneMedios(valor)) hallados.push(valor);
    Object.values(valor).forEach((v) => buscarNodos(v, codigo, hallados));
  }
  return hallados;
}

function cuantasLaminas(nodo) {
  return nodo.carousel_media?.length || 0;
}

export function nodoDesdeHtml(html, codigo) {
  const bloques = [...html.matchAll(/<script type="application\/json"[^>]*>(.*?)<\/script>/gs)].map((m) => m[1]);
  for (const bloque of bloques.filter((b) => b.includes(codigo))) {
    let datos;
    try { datos = JSON.parse(bloque); } catch { continue; }
    const hallados = buscarNodos(datos, codigo).sort((a, z) => cuantasLaminas(z) - cuantasLaminas(a));
    if (hallados.length) return hallados[0];
  }
  throw new ErrorDeReferencia('payload_no_encontrado: post privado, restringido por edad o Instagram cambió el HTML (prueba la ficha con sesión, --cdp)');
}

export function metaDeNodo(nodo, url) {
  const partes = nodo.carousel_media || [nodo];
  const caption = typeof nodo.caption === 'object' ? nodo.caption?.text : nodo.caption;
  return {
    url,
    shortcode: nodo.code,
    autor: nodo.user?.username || nodo.owner?.username || '',
    caption: caption || '',
    fecha: nodo.taken_at ? new Date(nodo.taken_at * 1000).toISOString() : null,
    likes: nodo.like_count ?? null,
    comentarios: nodo.comment_count ?? null,
    total_laminas: partes.length,
    laminas: partes.map((p, i) => ({
      lamina: i + 1,
      tipo: p.media_type === 2 || p.video_versions ? 'video (se baja la portada)' : 'imagen',
      ancho: p.original_width ?? null,
      alto: p.original_height ?? null,
      alt: p.accessibility_caption || '',
      imagen: p.image_versions2?.candidates?.[0]?.url || null,
    })),
  };
}

export function revisarRespuestaApi(estado, texto) {
  let json = null;
  try { json = JSON.parse(texto); } catch { /* respuesta no JSON: se reporta abajo */ }
  if (estado === 401 || ALERTA.test(json?.message || '')) {
    throw new AlertaDeSesion(`ALERTA_SESION: Instagram respondió ${estado} ${json?.message || ''}`);
  }
  const nodo = json?.items?.[0];
  if (!nodo) throw new ErrorDeReferencia(`la API no devolvió el post (HTTP ${estado})`);
  return nodo;
}

export function argumentos(argv) {
  const valor = (flag) => (argv.includes(flag) ? argv[argv.indexOf(flag) + 1] : undefined);
  const urls = argv.filter((a) => a.startsWith('http') && argv[argv.indexOf(a) - 1] !== '--cdp');
  if (!urls.length) throw new ErrorDeReferencia(USO);
  const cdp = valor('--cdp');
  const perfil = valor('--perfil');
  if (cdp && perfil) throw new ErrorDeReferencia('usa --cdp o --perfil, no los dos');
  return { urls, out: resolve(valor('--out') || 'referencia'), cdp, perfil: perfil && resolve(perfil) };
}

export function rutaDeSalida(out, codigo, varios) {
  return varios ? join(out, codigo) : out;
}

export function revisarDescarga(meta) {
  if (!meta.laminas.some((l) => l.archivo)) {
    throw new ErrorDeReferencia(`no bajó ninguna lámina de ${meta.total_laminas} (pasa con carruseles vacíos o restringidos)`);
  }
}

export function resumenLote(resultados) {
  return {
    done: resultados.filter((r) => r.meta).map((r) => ({ shortcode: r.meta.shortcode, author: r.meta.autor, slides: r.meta.total_laminas })),
    failed: resultados.filter((r) => r.error).map((r) => ({ url: r.url, error: r.error })),
  };
}

export function rutaNavegador(env) {
  return env.BRAVE_PATH || env.BROWSER_PATH || undefined;
}

async function cargarPlaywright() {
  const ruta = resolve(process.cwd(), 'node_modules', 'playwright', 'index.js');
  try {
    const modulo = await import(pathToFileURL(ruta).href);
    return (modulo.default ?? modulo).chromium;
  } catch {
    throw new ErrorDeReferencia('no encuentro Playwright aquí: corre npm install playwright en esta carpeta');
  }
}

async function nodoSinSesion(pagina, url, codigo) {
  await pagina.goto(url, { waitUntil: 'domcontentloaded', timeout: 45000 });
  await pagina.waitForTimeout(5000);
  return nodoDesdeHtml(await pagina.content(), codigo);
}

async function nodoConSesion(pagina, codigo) {
  if (!/instagram\.com/.test(pagina.url())) await pagina.goto('https://www.instagram.com/', { waitUntil: 'domcontentloaded', timeout: 45000 });
  const { estado, texto } = await pagina.evaluate(async ({ ruta, appId }) => {
    const csrf = (document.cookie.match(/csrftoken=([^;]+)/) || [])[1] || '';
    const r = await fetch(ruta, { credentials: 'include', headers: { 'x-ig-app-id': appId, 'x-csrftoken': csrf, 'x-requested-with': 'XMLHttpRequest' } });
    return { estado: r.status, texto: await r.text() };
  }, { ruta: `/api/v1/media/${pkDeCodigo(codigo)}/info/`, appId: IG_APP_ID });
  return revisarRespuestaApi(estado, texto);
}

async function guardar(pagina, meta, carpeta) {
  await mkdir(carpeta, { recursive: true });
  for (const lamina of meta.laminas.filter((l) => l.imagen)) {
    const archivo = join(carpeta, `slide-${String(lamina.lamina).padStart(2, '0')}.jpg`);
    try {
      const respuesta = await pagina.request.get(lamina.imagen, { timeout: 30000 });
      await writeFile(archivo, await respuesta.body());
      lamina.archivo = archivo;
    } catch (e) {
      lamina.error = e.message;
    }
  }
  await writeFile(join(carpeta, 'meta.json'), JSON.stringify(meta, null, 2));
  await writeFile(join(carpeta, 'descripcion-original.txt'), meta.caption);
  revisarDescarga(meta);
}

async function abrir(chromium, { cdp, perfil }) {
  const executablePath = rutaNavegador(process.env);
  const opciones = { headless: true, ...(executablePath ? { executablePath } : {}) };
  if (cdp) {
    const navegador = await chromium.connectOverCDP(cdp);
    const contexto = navegador.contexts()[0] || await navegador.newContext();
    const pagina = await contexto.newPage();
    return { pagina, cerrar: async () => pagina.close() };
  }
  if (perfil) {
    const contexto = await chromium.launchPersistentContext(perfil, { ...opciones, viewport: { width: 1280, height: 1100 } });
    return { pagina: contexto.pages()[0] || await contexto.newPage(), cerrar: async () => contexto.close() };
  }
  const navegador = await chromium.launch(opciones);
  const contexto = await navegador.newContext({ viewport: { width: 1280, height: 1100 } });
  return { pagina: await contexto.newPage(), cerrar: async () => navegador.close() };
}

async function bajarUno(pagina, url, args, varios) {
  const codigo = shortcodeDe(url);
  const nodo = args.cdp ? await nodoConSesion(pagina, codigo) : await nodoSinSesion(pagina, url, codigo);
  const meta = metaDeNodo(nodo, url);
  await guardar(pagina, meta, rutaDeSalida(args.out, codigo, varios));
  return meta;
}

async function main() {
  const args = argumentos(process.argv.slice(2));
  const varios = args.urls.length > 1;
  const { pagina, cerrar } = await abrir(await cargarPlaywright(), args);
  const resultados = [];
  try {
    for (const url of args.urls) {
      try {
        const meta = await bajarUno(pagina, url, args, varios);
        resultados.push({ url, meta });
        console.log(`OK    ${meta.shortcode}: ${meta.total_laminas} láminas de @${meta.autor}`);
      } catch (e) {
        if (e instanceof AlertaDeSesion) throw e;
        resultados.push({ url, error: e.message });
        console.log(`FALLO ${url}: ${e.message}`);
      }
    }
  } finally {
    await cerrar();
  }
  const lote = resumenLote(resultados);
  if (varios) {
    await mkdir(args.out, { recursive: true });
    await writeFile(join(args.out, '_batch.json'), JSON.stringify(lote, null, 2));
  }
  console.log(`${lote.done.length} ok / ${lote.failed.length} fallidos`);
  if (lote.failed.length) process.exitCode = 1;
}

if (import.meta.url === pathToFileURL(process.argv[1] || '').href) {
  main().catch((e) => {
    console.error(`ERROR: ${e.message}`);
    process.exit(e instanceof AlertaDeSesion ? SALIDA_ALERTA : 1);
  });
}
