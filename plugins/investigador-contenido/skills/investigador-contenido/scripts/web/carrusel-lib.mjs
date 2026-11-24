// Funciones puras del lector público de carruseles: el HTML del post trae un <script type="application/json"> con el
// nodo de la publicación (carousel_media con la imagen a tamaño completo de cada lámina y el caption).

export function shortcodeDe(url) {
  const m = (url || '').match(/\/(?:p|reel|tv)\/([A-Za-z0-9_-]+)/);
  if (!m) throw new Error(`la URL no es un post de Instagram: ${url}`);
  return m[1];
}

export function bloquesJson(html) {
  return [...html.matchAll(/<script type="application\/json"[^>]*>(.*?)<\/script>/gs)].map((m) => m[1]);
}

function buscar(objeto, codigo, hallados) {
  if (Array.isArray(objeto)) {
    for (const v of objeto) buscar(v, codigo, hallados);
  } else if (objeto && typeof objeto === 'object') {
    if (objeto.code === codigo && (objeto.carousel_media || objeto.image_versions2 || objeto.video_versions)) hallados.push(objeto);
    for (const v of Object.values(objeto)) buscar(v, codigo, hallados);
  }
  return hallados;
}

/** El nodo del post (el que trae más láminas) o null si el HTML no lo trae. */
export function nodoDelPost(bloques, codigo) {
  for (const bloque of bloques.filter((b) => b.includes(codigo))) {
    let datos;
    try { datos = JSON.parse(bloque); } catch { continue; }
    const hallados = buscar(datos, codigo, []);
    if (hallados.length) return hallados.sort((a, z) => (z.carousel_media?.length || 0) - (a.carousel_media?.length || 0))[0];
  }
  return null;
}

export function laminasDe(nodo) {
  return (nodo.carousel_media || [nodo]).map((it, i) => ({
    lamina: i + 1, tipo: it.media_type === 2 || it.video_versions ? 'video' : 'imagen',
    w: it.original_width ?? null, h: it.original_height ?? null, alt: it.accessibility_caption || '',
    url: it.image_versions2?.candidates?.[0]?.url || null,
  }));
}

export function metaDe(nodo, url, carpeta) {
  return {
    url, shortcode: nodo.code, author: nodo.user?.username || nodo.owner?.username || '',
    caption: (typeof nodo.caption === 'object' ? nodo.caption?.text : nodo.caption) || '',
    taken_at: nodo.taken_at ? new Date(nodo.taken_at * 1000).toISOString() : null,
    likes: nodo.like_count ?? null, comments: nodo.comment_count ?? null,
    total_slides: (nodo.carousel_media || [nodo]).length, dir: carpeta, slides: [],
  };
}

/** Cuántas láminas se bajaron de verdad. Sin ninguna, el carrusel es un fallo (pasa: a veces no baja nada). */
export function estadoDeDescarga(meta) {
  const bajadas = meta.slides.filter((s) => s.file).length;
  return { ok: bajadas > 0, bajadas, faltan: meta.total_slides - bajadas };
}
