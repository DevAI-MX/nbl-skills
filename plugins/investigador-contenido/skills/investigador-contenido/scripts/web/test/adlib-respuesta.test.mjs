import { test } from 'node:test';
import assert from 'node:assert/strict';
import { alcanceUe, numerarSinRepetidos, pideSesionOBloquea, resultadosDeGraphql, resultadosIncrustados, totalDeTexto, urlDe } from '../adlib-respuesta.mjs';

const conexion = (ids, siguiente = true) => ({ edges: [{ node: { collated_results: ids.map((id) => ({ ad_archive_id: id })) } }],
  page_info: { has_next_page: siguiente } });

test('arma la búsqueda por palabra, frase exacta o página, ordenada por impresiones', () => {
  const kw = new URL(urlDe({ q: 'clase gratis', type: 'keyword', country: 'MX' }));
  assert.equal(kw.searchParams.get('q'), 'clase gratis');
  assert.equal(kw.searchParams.get('search_type'), 'keyword_unordered');
  assert.equal(kw.searchParams.get('country'), 'MX');
  assert.equal(kw.searchParams.get('active_status'), 'active');
  assert.equal(kw.searchParams.get('sort_data[mode]'), 'total_impressions');
  const frase = new URL(urlDe({ q: 'clase gratis', type: 'phrase', status: 'all' }));
  assert.equal(frase.searchParams.get('q'), '"clase gratis"');
  assert.equal(frase.searchParams.get('search_type'), 'keyword_exact_phrase');
  assert.equal(frase.searchParams.get('country'), 'ALL');
  const pagina = new URL(urlDe({ type: 'page', page_id: '123' }));
  assert.equal(pagina.searchParams.get('view_all_page_id'), '123');
  assert.equal(pagina.searchParams.get('q'), null);
});

test('lee los anuncios de la respuesta GraphQL (solo la primera línea) e ignora otras respuestas', () => {
  const cuerpo = JSON.stringify({ data: { ad_library_main: { search_results_connection: conexion(['a', 'b'], false) } } }) + '\n{"extra":1}';
  const r = resultadosDeGraphql(cuerpo);
  assert.deepEqual(r.nodos.map((n) => n.ad_archive_id), ['a', 'b']);
  assert.equal(r.fin.has_next_page, false);
  assert.equal(resultadosDeGraphql('{"data":{}}'), null);
  assert.equal(resultadosDeGraphql('search_results_connection roto'), null);
});

test('lee la primera tanda incrustada en el HTML, aun con llaves dentro de cadenas', () => {
  const bloque = JSON.stringify(conexion(['x'])).replace('"x"', '"x","nota":"texto con } y { y \\" comillas"');
  const html = `<script>{"a":1,"search_results_connection":${bloque}}</script><p>"search_results_connection":{"edges":[{"node":{"collated_results":[{"ad_archive_id":"y"}]}}]}</p>`;
  const r = resultadosIncrustados(html);
  assert.deepEqual(r.nodos.map((n) => n.ad_archive_id), ['x', 'y']);
  assert.equal(r.fin.has_next_page, true);
  assert.deepEqual(resultadosIncrustados('<html></html>'), { nodos: [], fin: null });
});

test('un anuncio por id, numerado en el orden de Meta', () => {
  const r = numerarSinRepetidos([{ ad_archive_id: '1' }, { ad_archive_id: '2' }, { ad_archive_id: '1' }]);
  assert.deepEqual(r.map((a) => [a.rank, a.ad_archive_id]), [[1, '1'], [2, '2']]);
});

test('detecta el muro de sesión o el bloqueo y lee el total de resultados', () => {
  assert.equal(pideSesionOBloquea('Inicia sesión para continuar'), true);
  assert.equal(pideSesionOBloquea("You're Temporarily Blocked"), true);
  assert.equal(pideSesionOBloquea('Biblioteca de anuncios'), false);
  assert.equal(totalDeTexto('~1.200 resultados'), '~1.200 resultados');
  assert.equal(totalDeTexto('nada'), null);
});

test('alcance UE desde GraphQL o desde el panel; sin dato queda en null', () => {
  assert.deepEqual(alcanceUe(['{"eu_total_reach":4521,"age_country_gender_reach_breakdown":[{"a":1}], "x":1}']),
    { eu_total_reach: 4521, desglose: '[{"a":1}]' });
  assert.deepEqual(alcanceUe([], 'Alcance total 12.345'), { eu_total_reach: 12345, desglose: null });
  assert.deepEqual(alcanceUe(['{"otra":1}'], 'sin dato'), { eu_total_reach: null, desglose: null });
});
