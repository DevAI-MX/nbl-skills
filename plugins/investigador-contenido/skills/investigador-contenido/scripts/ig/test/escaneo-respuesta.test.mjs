import { test } from 'node:test';
import assert from 'node:assert/strict';
import { armarEscaneo, codigoDeEnlace, encadenadosDeRespuesta, esDelPerfil, fusionar, perfilDeRespuesta,
  publicacionesDeRespuesta, seguidoresDeCabecera, vistasVisibles } from '../escaneo-respuesta.mjs';

const nodoReel = { code: 'R1', pk: '11', product_type: 'clips', play_count: 79662, like_count: 900, comment_count: 12,
  caption: { text: 'hola' }, user: { username: 'cuenta' }, image_versions2: { candidates: [{ url: 'https://example.invalid/r1.jpg' }] } };
const nodoCarrusel = { code: 'C1', pk: '12', product_type: 'carousel_container', like_count: 3000, carousel_media_count: 8,
  carousel_media: [{ image_versions2: { candidates: [{ url: 'https://example.invalid/c1.jpg' }] } }] };

test('lee reels de /reels/ (clips_connection nueva y vieja) y carruseles del feed', () => {
  const reels = publicacionesDeRespuesta({ data: { fetch__XDTUserDict: { clips_connection: { edges: [{ node: { media: nodoReel } }] } } } });
  const viejos = publicacionesDeRespuesta({ data: { xdt_api__v1__clips__user__connection_v2: { edges: [{ node: { media: nodoReel } }] } } });
  const feed = publicacionesDeRespuesta({ data: { xdt_api__v1__feed__user_timeline_graphql_connection: { edges: [{ node: nodoCarrusel }] } } });
  assert.equal(reels[0].play_count, 79662);
  assert.equal(reels[0].caption, 'hola');
  assert.equal(reels[0].thumb, 'https://example.invalid/r1.jpg');
  assert.deepEqual(viejos, reels);
  assert.equal(feed[0].type, 'carousel_container');
  assert.equal(feed[0].slides, 8);
  assert.equal(feed[0].play_count, null);
  assert.equal(feed[0].thumb, 'https://example.invalid/c1.jpg');
});

test('ignora nodos sin código y respuestas ajenas', () => {
  assert.deepEqual(publicacionesDeRespuesta({ data: { xdt_api__v1__clips__user__connection_v2: { edges: [{ node: {} }] } } }), []);
  assert.deepEqual(publicacionesDeRespuesta(null), []);
});

test('seguidores solo si la respuesta es del perfil pedido', () => {
  assert.equal(perfilDeRespuesta({ data: { user: { username: 'Cuenta', follower_count: 1200 } } }, 'cuenta'), 1200);
  assert.equal(perfilDeRespuesta({ data: { user: { username: 'otra', follower_count: 5 } } }, 'cuenta'), null);
  assert.equal(perfilDeRespuesta({ data: { user: { username: 'cuenta', edge_followed_by: { count: 7 } } } }, 'cuenta'), 7);
});

test('fusionar no pisa un dato con null', () => {
  assert.deepEqual(fusionar({ caption: 'previo', play_count: 5 }, { caption: null, play_count: 9 }), { caption: 'previo', play_count: 9 });
  assert.deepEqual(fusionar(undefined, { a: 1 }), { a: 1 });
});

test('sugeridos del perfil para descubrir cuentas', () => {
  assert.deepEqual(encadenadosDeRespuesta({ data: { xdt_api__v1__discover__chaining: { users: [{ username: 'a' }, { username: 'b' }] } } }), ['a', 'b']);
  assert.deepEqual(encadenadosDeRespuesta({}), []);
});

test('seguidores exactos del atributo title y la línea visible', () => {
  const r = seguidoresDeCabecera(['', '27.312', '15'], 'cuenta\n312 publicaciones\n27,3 mil seguidores\n');
  assert.deepEqual(r, { followers: 27312, label: '27,3 mil seguidores' });
  assert.deepEqual(seguidoresDeCabecera(), { followers: null, label: null });
});

test('código y dueño de cada enlace de la cuadrícula', () => {
  assert.equal(codigoDeEnlace('/cuenta/reel/ABC_-1/'), 'ABC_-1');
  assert.equal(codigoDeEnlace('/p/XYZ/?img_index=1'), 'XYZ');
  assert.equal(codigoDeEnlace('/explore/'), null);
  assert.equal(esDelPerfil('/cuenta/reel/A/', 'Cuenta'), true);
  assert.equal(esDelPerfil('/otra/reel/A/', 'cuenta'), false);
  assert.equal(esDelPerfil('/reel/A/', 'cuenta'), true);
});

test('contador visible en español, portugués e inglés', () => {
  assert.equal(vistasVisibles('79,6 mil'), 79600);
  assert.equal(vistasVisibles('1,2 M'), 1200000);
  assert.equal(vistasVisibles('2 M'), 2000000);
  assert.equal(vistasVisibles('1,5 mi'), 1500000);
  assert.equal(vistasVisibles('12.5K'), 12500);
  assert.equal(vistasVisibles('9585'), 9585);
  assert.equal(vistasVisibles('1.234'), 1234);
  assert.equal(vistasVisibles('1.234,5 mil'), 1234500);
  assert.equal(vistasVisibles(''), null);
  assert.equal(vistasVisibles('Fijado'), null);
});

test('el escaneo guarda payload y contador visible; en feed no inventa vistas', () => {
  const dom = { titles: ['1.000'], htext: '1 mil seguidores', notfound: false, privado: false };
  const porCodigo = new Map([['R1', { code: 'R1', play_count: 50 }]]);
  const reels = armarEscaneo({ handle: 'c', feed: false, dom, visibles: new Map([['R1', '45 mil'], ['R2', '3 M']]),
    porCodigo, seguidoresApi: 999, encadenados: [], fecha: 'f' });
  assert.equal(reels.followers, 1000);
  assert.equal(reels.mode, 'reels');
  assert.deepEqual(reels.items.map((i) => [i.code, i.play_count ?? null, i.vistas_visibles]), [['R1', 50, 45000], ['R2', null, 3000000]]);
  const feed = armarEscaneo({ handle: 'c', feed: true, dom: { ...dom, titles: [] }, visibles: new Map([['C1', '']]),
    porCodigo: new Map(), seguidoresApi: 999, encadenados: [], fecha: 'f' });
  assert.equal(feed.followers, 999);
  assert.equal(feed.items[0].vistas_visibles, null);
});
