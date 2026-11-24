// Pruebas de bajar_referencia.mjs (sin red). Correr: node --test "scripts/tests/*.test.mjs"
import { test } from 'node:test';
import assert from 'node:assert/strict';
import {
  shortcodeDe, pkDeCodigo, buscarNodos, nodoDesdeHtml, metaDeNodo, revisarRespuestaApi,
  ErrorDeReferencia, AlertaDeSesion, argumentos, rutaDeSalida, revisarDescarga, resumenLote, rutaNavegador,
} from '../bajar_referencia.mjs';

const lamina = (n) => ({ media_type: 1, original_width: 1080, original_height: 1350,
  image_versions2: { candidates: [{ url: `https://cdn.ejemplo/${n}.jpg` }, { url: 'chica.jpg' }] } });
const nodo = {
  code: 'AbC_1-x', user: { username: 'cuenta_ejemplo' }, caption: { text: 'Comenta GUIA' },
  taken_at: Date.UTC(2026, 0, 1) / 1000, like_count: 10, comment_count: 5, carousel_media: [lamina(1), lamina(2), lamina(3)],
};

test('shortcode desde p, reel y con usuario en la ruta', () => {
  assert.equal(shortcodeDe('https://www.instagram.com/p/AbC_1-x/?img_index=1'), 'AbC_1-x');
  assert.equal(shortcodeDe('https://instagram.com/reel/XYZ/'), 'XYZ');
  assert.equal(shortcodeDe('https://www.instagram.com/cuenta.ejemplo/p/QWE/'), 'QWE');
  assert.throws(() => shortcodeDe('https://ejemplo.com/p/x'), ErrorDeReferencia);
});

test('pk desde el shortcode en base 64 de Instagram', () => {
  assert.equal(pkDeCodigo('B'), '1');
  assert.equal(pkDeCodigo('BA'), '64');
  assert.equal(pkDeCodigo('_'), '63');
  assert.throws(() => pkDeCodigo('a*b'), ErrorDeReferencia);
});

test('buscarNodos solo devuelve nodos del código con medios', () => {
  const arbol = { a: [{ code: 'AbC_1-x' }, { b: nodo }], c: { code: 'otro', image_versions2: {} } };
  assert.deepEqual(buscarNodos(arbol, 'AbC_1-x'), [nodo]);
});

test('nodoDesdeHtml elige el nodo con más láminas y salta JSON roto', () => {
  const corto = { ...nodo, carousel_media: [lamina(1)] };
  const html = `<script type="application/json">{roto AbC_1-x</script>
    <script type="application/json" data-x="1">${JSON.stringify({ x: [corto, nodo] })}</script>`;
  assert.equal(nodoDesdeHtml(html, 'AbC_1-x').carousel_media.length, 3);
  assert.throws(() => nodoDesdeHtml('<html></html>', 'AbC_1-x'), /payload_no_encontrado/);
});

test('metaDeNodo arma cuenta, caption y la imagen completa de cada lámina', () => {
  const meta = metaDeNodo(nodo, 'https://www.instagram.com/p/AbC_1-x/');
  assert.equal(meta.total_laminas, 3);
  assert.equal(meta.autor, 'cuenta_ejemplo');
  assert.equal(meta.caption, 'Comenta GUIA');
  assert.equal(meta.laminas[1].imagen, 'https://cdn.ejemplo/2.jpg');
  assert.equal(meta.fecha, '2026-01-01T00:00:00.000Z');
});

test('un post de una sola imagen cuenta como una lámina', () => {
  const solo = { code: 'Z', image_versions2: { candidates: [{ url: 'u' }] }, caption: 'texto' };
  const meta = metaDeNodo(solo, 'u');
  assert.equal(meta.total_laminas, 1);
  assert.equal(meta.caption, 'texto');
});

test('revisarRespuestaApi: alerta de sesión, sin post y post correcto', () => {
  assert.throws(() => revisarRespuestaApi(401, '{}'), AlertaDeSesion);
  assert.throws(() => revisarRespuestaApi(400, '{"message":"checkpoint_required"}'), AlertaDeSesion);
  assert.throws(() => revisarRespuestaApi(404, 'no json'), ErrorDeReferencia);
  assert.equal(revisarRespuestaApi(200, JSON.stringify({ items: [nodo] })).code, 'AbC_1-x');
});

test('argumentos: varios enlaces, --out, --cdp y --perfil', () => {
  const a = argumentos(['https://www.instagram.com/p/A/', 'https://www.instagram.com/p/B/', '--out', 'refs', '--perfil', 'perfil-ig']);
  assert.deepEqual(a.urls, ['https://www.instagram.com/p/A/', 'https://www.instagram.com/p/B/']);
  assert.ok(a.out.endsWith('refs'));
  assert.ok(a.perfil.endsWith('perfil-ig'));
  assert.equal(a.cdp, undefined);
  assert.throws(() => argumentos(['--out', 'x']), ErrorDeReferencia);
  assert.throws(() => argumentos(['https://www.instagram.com/p/A/', '--cdp', 'http://127.0.0.1:9333', '--perfil', 'p']), ErrorDeReferencia);
});

test('con un enlace guarda en --out; con varios, una carpeta por shortcode', () => {
  assert.equal(rutaDeSalida('/r', 'ABC', false), '/r');
  assert.equal(rutaDeSalida('/r', 'ABC', true), '/r/ABC');
});

test('una descarga sin ninguna lámina es error (pasa con carruseles vacíos)', () => {
  assert.throws(() => revisarDescarga({ total_laminas: 3, laminas: [{}, {}, {}] }), /ninguna lámina/);
  assert.doesNotThrow(() => revisarDescarga({ total_laminas: 2, laminas: [{ archivo: 'x' }, { error: 'e' }] }));
});

test('resumen del lote: hechos y fallidos', () => {
  const r = resumenLote([{ url: 'u1', meta: { shortcode: 'A', autor: 'c', total_laminas: 3 } }, { url: 'u2', error: 'falló' }]);
  assert.deepEqual(r, { done: [{ shortcode: 'A', author: 'c', slides: 3 }], failed: [{ url: 'u2', error: 'falló' }] });
});

test('el navegador sale de BRAVE_PATH o BROWSER_PATH', () => {
  assert.equal(rutaNavegador({ BRAVE_PATH: '/b', BROWSER_PATH: '/c' }), '/b');
  assert.equal(rutaNavegador({ BROWSER_PATH: '/c' }), '/c');
  assert.equal(rutaNavegador({}), undefined);
});
