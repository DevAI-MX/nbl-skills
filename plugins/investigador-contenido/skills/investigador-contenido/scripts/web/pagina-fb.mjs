// Funciones puras: id de anunciante de una página pública de Facebook a partir de su HTML.
const PATRONES = [/fb:\/\/page\/(\d+)/g, /"pageID":"(\d+)"/g, /"page_id":"(\d+)"/g, /"userID":"(\d+)"/g, /"delegate_page":\{"id":"(\d+)"/g];

export function idsDePagina(html) {
  const ids = new Set();
  for (const re of PATRONES) for (const m of html.matchAll(re)) ids.add(m[1]);
  return [...ids];
}

export function tituloDe(html) {
  return ((html.match(/<title>([^<]*)<\/title>/) || [])[1] || '').slice(0, 120);
}
