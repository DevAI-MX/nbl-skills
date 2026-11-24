import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'fs';
import { mediosDeBusqueda, esRespuestaDeBusqueda } from '../serp-respuesta.mjs';

const respuesta = JSON.parse(fs.readFileSync(new URL('./fixtures/top_serp_graphql.json', import.meta.url), 'utf8'));

test('reconoce la respuesta GraphQL de la búsqueda por palabra clave', () => {
  assert.equal(esRespuestaDeBusqueda(respuesta), true);
  assert.equal(esRespuestaDeBusqueda({ data: { xdt_viewer: {} } }), false);
  assert.equal(esRespuestaDeBusqueda(null), false);
});

test('saca los reels de las unidades de cuadrícula e ignora encabezados, cuentas y piezas sin código', () => {
  const medios = mediosDeBusqueda(respuesta, 'marca personal');
  assert.deepEqual(medios.map(m => m.code), ['DVq-bkuAEPw', 'DB6r209othX']);
});

test('cada reel trae dueño, fecha, likes, comentarios, caption y la búsqueda que lo encontró', () => {
  const [primero] = mediosDeBusqueda(respuesta, 'marca personal');
  assert.equal(primero.user, 'cuenta_ejemplo_uno');
  assert.equal(primero.taken_at, 1773076187); // vault:inventado
  assert.equal(primero.likes, 15808);
  assert.equal(primero.comments, 154);
  assert.equal(primero.media_type, 2);
  assert.match(primero.caption, /5 tipos de contenido/);
  assert.deepEqual(primero.queries, ['marca personal']);
});

test('las vistas quedan en null cuando Instagram no las manda, nunca en cero', () => {
  const [primero] = mediosDeBusqueda(respuesta, 'marca personal');
  assert.equal(primero.plays, null);
});

test('una respuesta sin cuadrícula devuelve lista vacía', () => {
  assert.deepEqual(mediosDeBusqueda({ data: { xdt_fbsearch__top_serp_graphql: { edges: [] } } }, 'x'), []);
  assert.deepEqual(mediosDeBusqueda({}, 'x'), []);
});
