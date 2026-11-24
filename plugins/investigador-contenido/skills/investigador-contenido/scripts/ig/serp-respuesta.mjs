// Lectura de la respuesta GraphQL del buscador de Instagram (PolarisKeywordSearchExplorePageRelayQuery).
// Desde oct-2026 los reels llegan en data.xdt_fbsearch__top_serp_graphql.edges[].node.items[], sin vistas.

const UNIDAD_CUADRICULA = 'XDTTopSerpMediaGridUnit';

function conexionDeBusqueda(respuesta) {
  return respuesta?.data?.xdt_fbsearch__top_serp_graphql;
}

export function esRespuestaDeBusqueda(respuesta) {
  return Boolean(conexionDeBusqueda(respuesta));
}

function miniatura(item) {
  return item.image_versions2?.candidates?.[0]?.url
    ?? item.carousel_media?.[0]?.image_versions2?.candidates?.[0]?.url
    ?? null;
}

function registroDeMedio(item, consulta) {
  return {
    code: item.code, pk: item.pk, media_type: item.media_type,
    user: item.user?.username, user_pk: item.user?.pk, verified: item.user?.is_verified,
    plays: item.view_count ?? null, likes: item.like_count ?? null, comments: item.comment_count ?? null,
    taken_at: item.taken_at, caption: item.caption?.text || '', thumb: miniatura(item),
    queries: [consulta],
  };
}

export function mediosDeBusqueda(respuesta, consulta) {
  const aristas = conexionDeBusqueda(respuesta)?.edges ?? [];
  return aristas
    .filter(arista => arista.node?.__typename === UNIDAD_CUADRICULA)
    .flatMap(arista => arista.node.items ?? [])
    .filter(item => item?.code)
    .map(item => registroDeMedio(item, consulta));
}
