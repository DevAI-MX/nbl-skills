// Ficha de cada publicación por su pk (el número, no el código): caption completo, comentarios, vistas, dueño,
// láminas, duración, coautores y si los comentarios están desactivados.
// USO: node minfo.mjs <pks.json> <salida.json>   (retoma: salta los pk que ya están)
import fs from 'node:fs';
import { connect, api, jitter } from './lib.mjs';
import { CODIGO_ALERTA } from './config.mjs';
import { esPrincipal } from './arranque.mjs';

export function fichaCorta(it) {
  return {
    code: it.code, type: it.product_type, user: it.user?.username, plays: it.play_count ?? null, ig_plays: it.ig_play_count ?? null,
    likes: it.like_count, comments: it.comment_count, taken_at: it.taken_at, caption: it.caption?.text || '',
    slides: it.carousel_media_count ?? null, dur: it.video_duration ?? null, coauthors: (it.coauthor_producers || []).map((x) => x.username),
    thumb: it.image_versions2?.candidates?.[0]?.url || it.carousel_media?.[0]?.image_versions2?.candidates?.[0]?.url || null,
    comments_disabled: it.comments_disabled ?? null,
  };
}

async function main() {
  const [entrada, salida] = process.argv.slice(2);
  if (!entrada || !salida) { console.error('uso: node minfo.mjs <pks.json> <salida.json>'); process.exit(1); }
  const pks = JSON.parse(fs.readFileSync(entrada, 'utf8'));
  const db = fs.existsSync(salida) ? JSON.parse(fs.readFileSync(salida, 'utf8')) : {};
  const page = await connect(process.env.TARGET);
  for (const pk of pks) {
    if (db[pk]) continue;
    try {
      const r = await api(page, `/api/v1/media/${pk}/info/`);
      const it = r.json?.items?.[0];
      db[pk] = it ? fichaCorta(it) : { error: r.status };
      if (!it) console.error(pk, 'HTTP', r.status);
    } catch (e) {
      if (e.alerta) { fs.writeFileSync(salida, JSON.stringify(db)); console.error(e.message); process.exit(CODIGO_ALERTA); }
      db[pk] = { error: e.message };
    }
    fs.writeFileSync(salida, JSON.stringify(db));
    await jitter(1800, 3000);
  }
  page.close();
}

if (esPrincipal(import.meta.url)) main().then(() => process.exit(0), (e) => { console.error(e.message); process.exit(1); });
