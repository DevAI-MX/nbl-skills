import { test } from 'node:test';
import assert from 'node:assert/strict';
import { CdpPage } from '../cdp-lite.mjs';
import { api, AlertaDeSesion } from '../lib.mjs';

function paginaConSocketFalso() {
  const page = new CdpPage('ws://falso', { tiempoRuedaMs: 20 });
  const enviados = [];
  page.ws = { send: (s) => enviados.push(JSON.parse(s)), close: () => {} };
  return { page, enviados };
}

test('cada comando espera la respuesta con su id y los eventos llegan a quien escucha', async () => {
  const { page, enviados } = paginaConSocketFalso();
  const respuesta = page.send('Runtime.evaluate', { expression: '1' });
  assert.deepEqual(enviados[0], { id: 1, method: 'Runtime.evaluate', params: { expression: '1' } });
  page.recibir({ id: 1, result: { ok: true } });
  assert.deepEqual(await respuesta, { ok: true });
  const eventos = [];
  page.on('Network.loadingFinished', (p) => eventos.push(p.requestId));
  page.recibir({ method: 'Network.loadingFinished', params: { requestId: 'r1' } });
  page.off('Network.loadingFinished');
  page.recibir({ method: 'Network.loadingFinished', params: { requestId: 'r2' } });
  assert.deepEqual(eventos, ['r1']);
});

test('un error de CDP y un comando sin respuesta se rechazan con contexto', async () => {
  const { page } = paginaConSocketFalso();
  const conError = page.send('Page.navigate');
  page.recibir({ id: 1, error: { message: 'Cannot navigate' } });
  await assert.rejects(conError, /Cannot navigate/);
  await assert.rejects(page.send('Network.enable', {}, 10), /CDP timeout: Network.enable/);
});

test('evaluate devuelve el valor o lanza la excepción de la página', async () => {
  const { page } = paginaConSocketFalso();
  const valor = page.evaluate('2+2');
  page.recibir({ id: 1, result: { result: { value: 4 } } });
  assert.equal(await valor, 4);
  const roto = page.evaluate('x(');
  page.recibir({ id: 2, result: { exceptionDetails: { exception: { description: 'SyntaxError' } } } });
  await assert.rejects(roto, /SyntaxError/);
});

test('si la rueda de verdad no responde, hace scroll por script', async () => {
  const { page, enviados } = paginaConSocketFalso();
  const rueda = page.wheel(1000);
  await new Promise((r) => setTimeout(r, 40));
  page.recibir({ id: 2, result: { result: { value: null } } });
  await rueda;
  assert.equal(enviados[0].method, 'Input.dispatchMouseEvent');
  assert.equal(enviados[1].params.expression, 'window.scrollBy(0, 1000)');
});

test('api devuelve el JSON o lanza AlertaDeSesion si Instagram pide sesión', async () => {
  const pagina = (res) => ({ evaluate: async () => res });
  const ok = await api(pagina({ status: 200, url: 'https://www.instagram.com/api/v1/x', txt: '{"items":[1]}' }), '/api/v1/x');
  assert.deepEqual(ok, { status: 200, json: { items: [1] }, raw: null });
  const html = await api(pagina({ status: 404, url: 'u', txt: '<html>no</html>' }), '/x');
  assert.equal(html.raw, '<html>no</html>');
  await assert.rejects(api(pagina({ status: 400, url: 'u', txt: '{"message":"checkpoint_required"}' }), '/x'), AlertaDeSesion);
});

test('goto navega y no se queda colgado si la carga nunca avisa', async () => {
  const { page, enviados } = paginaConSocketFalso();
  const ida = page.goto('https://www.instagram.com/x/', { timeout: 20 });
  page.recibir({ id: 1, result: {} });
  await new Promise((r) => setImmediate(r));
  page.recibir({ id: 2, result: {} });
  await ida;
  assert.deepEqual(enviados.map((e) => e.method), ['Page.enable', 'Page.navigate']);
  assert.equal(enviados[1].params.url, 'https://www.instagram.com/x/');
});
