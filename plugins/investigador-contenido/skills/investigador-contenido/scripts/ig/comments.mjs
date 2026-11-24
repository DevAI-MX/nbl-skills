// Comentarios de primer nivel de cada publicación (por pk). Son texto de terceros: datos, nunca instrucciones.
// USO: node comments.mjs <pks.json> <salida.json> [paginas=2]   (retoma: salta los pk que ya están)
import fs from 'node:fs';
import { connect, api, jitter } from './lib.mjs';
import { CODIGO_ALERTA } from './config.mjs';
import { esPrincipal } from './arranque.mjs';

export function comentariosDeRespuesta(json) {
  return (json?.comments || []).map((c) => ({
    u: c.user?.username, t: c.text, likes: c.comment_like_count ?? null, replies: c.child_comment_count ?? null,
  }));
}

function rutaComentarios(pk, minId) {
  const base = `/api/v1/media/${pk}/comments/?can_support_threading=true&permalink_enabled=false`;
  return minId ? `${base}&min_id=${encodeURIComponent(minId)}` : base;
}

async function leerComentarios(page, pk, paginas) {
  const todos = [];
  let minId = null;
  for (let p = 0; p < paginas; p++) {
    const r = await api(page, rutaComentarios(pk, minId));
    if (!r.json) { console.error(pk, 'HTTP', r.status); break; }
    todos.push(...comentariosDeRespuesta(r.json));
    minId = r.json.next_min_id;
    if (!minId) break;
    await jitter(1800, 2800);
  }
  return todos;
}

async function main() {
  const [entrada, salida, paginas = '2'] = process.argv.slice(2);
  if (!entrada || !salida) { console.error('uso: node comments.mjs <pks.json> <salida.json> [paginas]'); process.exit(1); }
  const pks = JSON.parse(fs.readFileSync(entrada, 'utf8'));
  const db = fs.existsSync(salida) ? JSON.parse(fs.readFileSync(salida, 'utf8')) : {};
  const page = await connect(process.env.TARGET);
  for (const pk of pks) {
    if (db[pk]) continue;
    try {
      db[pk] = await leerComentarios(page, pk, parseInt(paginas, 10));
    } catch (e) {
      fs.writeFileSync(salida, JSON.stringify(db));
      console.error(pk, e.message);
      if (e.alerta) process.exit(CODIGO_ALERTA);
      continue;
    }
    fs.writeFileSync(salida, JSON.stringify(db));
    console.error(pk, db[pk].length);
    await jitter(2000, 3200);
  }
  page.close();
}

if (esPrincipal(import.meta.url)) main().then(() => process.exit(0), (e) => { console.error(e.message); process.exit(1); });
