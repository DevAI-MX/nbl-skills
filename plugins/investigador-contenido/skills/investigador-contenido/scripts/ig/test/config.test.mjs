import { test } from 'node:test';
import assert from 'node:assert/strict';
import path from 'node:path';
import { urlCdp, carpetaEscaneos, carpetaDeLaCorrida, elegirPestana, ErrorDeConfiguracion } from '../config.mjs';
import { esAlertaDeSesion, cuerpoComoJson } from '../lib.mjs';

test('el puerto del navegador de investigación es obligatorio y no puede ser el personal', () => {
  assert.equal(urlCdp({ CDP_PUERTO: '9400' }), 'http://127.0.0.1:9400');
  assert.throws(() => urlCdp({}), ErrorDeConfiguracion);
  assert.throws(() => urlCdp({ CDP_PUERTO: 'abc' }), ErrorDeConfiguracion);
  assert.throws(() => urlCdp({ CDP_PUERTO: '9400', CDP_PUERTO_PERSONAL: '9400' }), /personal/);
});

test('la carpeta de escaneos se resuelve contra la carpeta de la corrida, igual que en pasos.py', () => {
  assert.equal(carpetaEscaneos({}, '/datos/corrida'), path.resolve('/datos/corrida/escaneos'));
  assert.equal(carpetaEscaneos({ ESCANEOS_DIR: '../comunes' }, '/datos/corrida'), path.resolve('/datos/comunes'));
  assert.equal(carpetaEscaneos({ ESCANEOS_DIR: '/fija' }, '/datos/corrida'), '/fija');
});

test('batchscan toma como carpeta de la corrida la de su lista', () => {
  assert.equal(carpetaDeLaCorrida('/datos/corrida/cuentas_a.json'), path.resolve('/datos/corrida'));
  assert.equal(carpetaDeLaCorrida('cuentas_a.json', '/donde/corro'), path.resolve('/donde/corro'));
});

test('elige la pestaña pedida o la primera de Instagram', () => {
  const pestanas = [{ id: 'a', type: 'page', url: 'about:blank' }, { id: 'b', type: 'page', url: 'https://www.instagram.com/' }];
  assert.equal(elegirPestana(pestanas).id, 'b');
  assert.equal(elegirPestana(pestanas, 'a').id, 'a');
  assert.throws(() => elegirPestana(pestanas, 'z'), /No existe/);
  assert.throws(() => elegirPestana([]), /PUT/);
});

test('reconoce cuándo Instagram pide sesión o frena la actividad', () => {
  assert.equal(esAlertaDeSesion({ status: 401 }), true);
  assert.equal(esAlertaDeSesion({ status: 400, mensaje: 'feedback_required' }), true);
  assert.equal(esAlertaDeSesion({ status: 200, url: 'https://www.instagram.com/accounts/login/' }), true);
  assert.equal(esAlertaDeSesion({ status: 200, mensaje: '', url: 'https://www.instagram.com/api/v1/media/1/info/' }), false);
});

test('lee JSON con o sin el prefijo for (;;);', () => {
  assert.deepEqual(cuerpoComoJson('for (;;);{"a":1}'), { a: 1 });
  assert.deepEqual(cuerpoComoJson('{"a":2}'), { a: 2 });
  assert.equal(cuerpoComoJson('<html>'), null);
});
