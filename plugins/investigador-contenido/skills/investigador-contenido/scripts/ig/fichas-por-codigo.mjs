// Ficha completa por código de publicación (el de la URL /reel/<codigo>/ o /p/<codigo>/), con la sesión del navegador
// de investigación: caption, vistas, likes, fecha, duración y las URLs del video y de la imagen de cada lámina.
// Es el método vigente para bajar las láminas de un carrusel: la lectura del JSON del HTML sin sesión dejó de servir.
// USO: node fichas-por-codigo.mjs <codigos.json> <salida.json>   (retoma: salta los que ya tienen ficha)
import fs from 'node:fs';
import { connect, api, jitter } from './lib.mjs';
import { CODIGO_ALERTA } from './config.mjs';
import { esPrincipal } from './arranque.mjs';

const ALFABETO = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_';

/** El código es el pk en base 64 con este alfabeto; se usa BigInt porque el pk no cabe en un Number. */
export function pkDeCodigo(codigo) {
  return [...codigo].reduce((pk, letra) => pk * 64n + BigInt(ALFABETO.indexOf(letra)), 0n).toString();
}

const mejorImagen = (m) => m.image_versions2?.candidates?.[0]?.url || null;
const mejorVideo = (m) => m.video_versions?.[0]?.url || null;

export function ficha(it) {
  const partes = it.carousel_media || [it];
  return {
    code: it.code, type: it.product_type, media_type: it.media_type,
    user: it.user?.username, user_pk: it.user?.pk, coauthors: (it.coauthor_producers || []).map((x) => x.username),
    plays: it.play_count ?? null, ig_plays: it.ig_play_count ?? null, views: it.view_count ?? null,
    likes: it.like_count, comments: it.comment_count, taken_at: it.taken_at, dur: it.video_duration ?? null,
    caption: it.caption?.text || '',
    partes: partes.map((m) => ({ media_type: m.media_type, imagen: mejorImagen(m), video: mejorVideo(m) })),
  };
}

async function main() {
  const [entrada, salida] = process.argv.slice(2);
  if (!entrada || !salida) { console.error('uso: node fichas-por-codigo.mjs <codigos.json> <salida.json>'); process.exit(1); }
  const codigos = JSON.parse(fs.readFileSync(entrada, 'utf8'));
  const db = fs.existsSync(salida) ? JSON.parse(fs.readFileSync(salida, 'utf8')) : {};
  const page = await connect(process.env.TARGET);
  for (const codigo of codigos) {
    if (db[codigo] && !db[codigo].error) continue;
    try {
      const r = await api(page, `/api/v1/media/${pkDeCodigo(codigo)}/info/`);
      const it = r.json?.items?.[0];
      db[codigo] = it ? ficha(it) : { error: r.status };
      if (!it) console.error(codigo, 'HTTP', r.status);
    } catch (e) {
      if (e.alerta) { fs.writeFileSync(salida, JSON.stringify(db, null, 1)); console.error(e.message); process.exit(CODIGO_ALERTA); }
      db[codigo] = { error: e.message };
    }
    fs.writeFileSync(salida, JSON.stringify(db, null, 1));
    await jitter(1800, 3000);
  }
  page.close();
}

if (esPrincipal(import.meta.url)) main().then(() => process.exit(0), (e) => { console.error(e.message); process.exit(1); });
