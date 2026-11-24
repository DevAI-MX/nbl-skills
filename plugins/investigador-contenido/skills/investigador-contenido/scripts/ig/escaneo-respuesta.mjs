// Funciones puras para leer un perfil de Instagram: respuestas GraphQL de /reels/ y del feed, cabecera y contadores.
// Sin red ni archivos: las usa scanlib.mjs y se prueban con node --test.

const CONEXIONES = [
  'xdt_api__v1__clips__user__connection_v2', // pestaña /reels/
  'xdt_api__v1__feed__user_timeline_graphql_connection', // feed principal (carruseles)
];

function conexionesDe(respuesta) {
  const datos = respuesta?.data || {};
  return [...CONEXIONES.map((c) => datos[c]), datos.fetch__XDTUserDict?.clips_connection].filter(Boolean);
}

/** Seguidores del perfil pedido si la respuesta trae su usuario; si no, null. */
export function perfilDeRespuesta(respuesta, handle) {
  const u = respuesta?.data?.user || respuesta?.data?.xdt_api__v1__users__web_profile_info?.user;
  if (!u || (u.username || '').toLowerCase() !== handle.toLowerCase()) return null;
  return u.follower_count ?? u.edge_followed_by?.count ?? null;
}

function textoDeCaption(caption) {
  return (typeof caption === 'object' ? caption?.text : caption) || null;
}

function miniatura(n) {
  return n.image_versions2?.candidates?.[0]?.url || n.carousel_media?.[0]?.image_versions2?.candidates?.[0]?.url || null;
}

function publicacion(n) {
  return {
    code: n.code, pk: n.pk, type: n.product_type ?? null,
    play_count: n.play_count ?? null, ig_play_count: n.ig_play_count ?? null,
    like_count: n.like_count ?? null, comment_count: n.comment_count ?? null, taken_at: n.taken_at ?? null,
    caption: textoDeCaption(n.caption), owner: n.user?.username || n.owner?.username || null,
    thumb: miniatura(n), slides: n.carousel_media_count ?? null,
  };
}

/** Publicaciones (reels o del feed) que trae una respuesta, ya normalizadas. */
export function publicacionesDeRespuesta(respuesta) {
  return conexionesDe(respuesta)
    .flatMap((conexion) => conexion.edges || [])
    .map((arista) => arista.node?.media || arista.node)
    .filter((n) => n?.code)
    .map(publicacion);
}

/** Une dos lecturas de la misma publicación sin pisar un dato con un null. */
export function fusionar(previa = {}, nueva) {
  const unida = { ...previa };
  for (const [clave, valor] of Object.entries(nueva)) if (valor !== null && valor !== undefined) unida[clave] = valor;
  return unida;
}

/** Cuentas que Instagram sugiere junto al perfil ("sugeridos"): sirven para descubrir más cuentas. */
export function encadenadosDeRespuesta(respuesta) {
  return (respuesta?.data?.xdt_api__v1__discover__chaining?.users || []).map((u) => u.username);
}

function entero(texto) {
  const m = (texto || '').replace(/[.,\s]/g, '').match(/\d+/);
  return m ? parseInt(m[0], 10) : null;
}

/** Seguidores exactos desde los atributos title de la cabecera (el primero positivo) y la línea visible. */
export function seguidoresDeCabecera(titulos = [], textoCabecera = '') {
  const exactos = titulos.map(entero).filter((n) => n !== null && n > 0);
  const lineas = textoCabecera.split('\n').map((s) => s.trim()).filter(Boolean);
  return { followers: exactos[0] ?? null, label: lineas.find((l) => /seguidores|followers/i.test(l)) || null };
}

/** Código de la publicación en un enlace /reel/<code>/ o /p/<code>/. */
export function codigoDeEnlace(href) {
  const m = (href || '').match(/\/(reel|p)\/([^/?#]+)/);
  return m ? m[2] : null;
}

/** Un enlace /otra_cuenta/reel/... es de otra cuenta (colaboración o sugerido): no cuenta para este perfil. */
export function esDelPerfil(href, handle) {
  const propio = (href || '').match(/^\/([^/]+)\/(reel|p)\//);
  return !propio || propio[1].toLowerCase() === handle.toLowerCase();
}

const MULTIPLICADORES = { mil: 1e3, k: 1e3, m: 1e6, mi: 1e6, mill: 1e6, millones: 1e6, mln: 1e6 };

/** Vistas del contador visible ("79,6 mil", "1,2 M", "12.5K", "9585"). Lo que no se entiende queda en null. */
export function vistasVisibles(texto) {
  const m = (texto || '').match(/(\d[\d.,]*)\s*(millones|mill|mln|mil|mi|m|k)?(?![a-z])/i);
  if (!m) return null;
  const sufijo = (m[2] || '').toLowerCase();
  if (!sufijo) return entero(m[1]);
  const numero = parseFloat(m[1].replace(/\.(?=\d{3}\b)/g, '').replace(',', '.'));
  return Number.isFinite(numero) ? Math.round(numero * MULTIPLICADORES[sufijo]) : null;
}

/** El escaneo que se guarda por cuenta. Las vistas del payload mandan; el contador visible queda al lado. */
export function armarEscaneo({ handle, feed, dom, visibles, porCodigo, seguidoresApi, encadenados, fecha }) {
  const cabecera = seguidoresDeCabecera(dom.titles, dom.htext);
  return {
    handle, scanned_at: fecha, mode: feed ? 'feed' : 'reels', notFound: dom.notfound, privado: dom.privado,
    followers: cabecera.followers ?? seguidoresApi ?? null, followers_label: cabecera.label,
    header_text: (dom.htext || '').slice(0, 600), chained: encadenados,
    items: [...visibles.entries()].map(([code, texto]) => ({
      code, visible: texto, vistas_visibles: feed ? null : vistasVisibles(texto), ...(porCodigo.get(code) || {}),
    })),
  };
}
