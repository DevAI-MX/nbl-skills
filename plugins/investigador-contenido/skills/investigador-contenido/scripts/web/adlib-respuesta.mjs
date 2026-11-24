// Funciones puras para la Biblioteca de anuncios de Meta: armar la URL de búsqueda y leer los resultados.

/** URL de búsqueda ordenada por impresiones totales (de mayor a menor): el rank es la posición. */
export function urlDe(c) {
  const p = new URLSearchParams({
    active_status: c.status || 'active', ad_type: 'all', country: c.country || 'ALL',
    is_targeted_country: 'false', media_type: 'all',
  });
  if (c.type === 'page') {
    p.set('search_type', 'page');
    p.set('view_all_page_id', c.page_id);
  } else {
    p.set('q', c.type === 'phrase' ? `"${c.q}"` : c.q);
    p.set('search_type', c.type === 'phrase' ? 'keyword_exact_phrase' : 'keyword_unordered');
  }
  p.set('sort_data[mode]', 'total_impressions');
  p.set('sort_data[direction]', 'desc');
  return 'https://www.facebook.com/ads/library/?' + p.toString();
}

function nodosDeConexion(conexion) {
  return (conexion?.edges || []).flatMap((e) => e.node?.collated_results || []);
}

/** Anuncios de una respuesta GraphQL de búsqueda (primera línea del cuerpo); si no es de búsqueda, null. */
export function resultadosDeGraphql(texto) {
  if (!texto.includes('search_results_connection')) return null;
  try {
    const c = JSON.parse(texto.split('\n')[0])?.data?.ad_library_main?.search_results_connection;
    return c ? { nodos: nodosDeConexion(c), fin: c.page_info || null } : null;
  } catch {
    return null;
  }
}

function finDelObjeto(texto, inicio) {
  let profundidad = 0, enCadena = false, escape = false;
  for (let j = inicio; j < texto.length; j++) {
    const ch = texto[j];
    if (enCadena) {
      if (escape) escape = false;
      else if (ch === '\\') escape = true;
      else if (ch === '"') enCadena = false;
    } else if (ch === '"') enCadena = true;
    else if (ch === '{') profundidad++;
    else if (ch === '}' && --profundidad === 0) return j;
  }
  return -1;
}

const MARCA = '"search_results_connection":{';

/** Con pocos resultados Meta manda la primera tanda incrustada en el HTML y no por GraphQL: se lee de ahí. */
export function resultadosIncrustados(html) {
  const nodos = [];
  let fin = null;
  for (let k = html.indexOf(MARCA); k >= 0;) {
    const inicio = html.indexOf('{', k);
    const cierre = finDelObjeto(html, inicio);
    if (cierre < 0) break;
    try {
      const c = JSON.parse(html.slice(inicio, cierre + 1));
      nodos.push(...nodosDeConexion(c));
      fin = fin || c.page_info || null;
    } catch { /* bloque roto: se salta */ }
    k = html.indexOf(MARCA, cierre);
  }
  return { nodos, fin };
}

/** Un anuncio por ad_archive_id, numerado en el orden en que Meta los muestra. */
export function numerarSinRepetidos(nodos) {
  const vistos = new Set();
  return nodos.filter((n) => !vistos.has(n.ad_archive_id) && vistos.add(n.ad_archive_id))
    .map((n, i) => ({ rank: i + 1, ...n }));
}

export function pideSesionOBloquea(textoPagina) {
  return /Inicia sesión para continuar|Log in to continue|You.re Temporarily Blocked|Bloqueado temporalmente/i.test(textoPagina);
}

export function totalDeTexto(textoPagina) {
  return (textoPagina.match(/~?[\d.,]+\s*(?:resultados|results)/) || [])[0] || null;
}

/** Alcance en la UE (solo existe para anuncios entregados en la UE) desde las respuestas GraphQL o el texto del panel. */
export function alcanceUe(respuestas, textoPanel = '') {
  for (const r of respuestas) {
    const m = r.match(/"eu_total_reach":(\d+)/);
    if (!m) continue;
    const desglose = r.match(/"age_country_gender_reach_breakdown":(\[.*?\])\s*,\s*"/);
    return { eu_total_reach: Number(m[1]), desglose: desglose ? desglose[1].slice(0, 4000) : null };
  }
  const t = textoPanel.match(/Alcance(?: total)?[^\d]{0,40}([\d.,]+)/i);
  return { eu_total_reach: t ? Number(t[1].replace(/[.,]/g, '')) : null, desglose: null };
}
