import { test } from 'node:test';
import assert from 'node:assert/strict';
import os from 'node:os';
import path from 'node:path';
import { perfilDelPuerto, perfilEsperado, urlCdpVerificada, ErrorDeConfiguracion } from '../config.mjs';

const PROCESOS = [
  '/Applications/Navegador.app/Contents/MacOS/Navegador --user-data-dir=/home/x/.perfil investigacion --remote-debugging-port=9400 --headless=new about:blank',
  '/Applications/Navegador.app/Contents/MacOS/Navegador --type=renderer --user-data-dir=/home/x/.perfil investigacion',
  '/Applications/Personal.app/Contents/MacOS/Personal --remote-debugging-port=9500',
  'ps -axo command',
].join('\n');

test('lee el perfil del proceso que escucha en el puerto, aunque tenga espacios', () => {
  assert.equal(perfilDelPuerto(PROCESOS, '9400'), '/home/x/.perfil investigacion');
  assert.equal(perfilDelPuerto(PROCESOS, '9500'), null);
  assert.equal(perfilDelPuerto(PROCESOS, '9600'), null);
  assert.equal(perfilDelPuerto('x --remote-debugging-port=94000 --user-data-dir=/otro', '9400'), null);
});

test('el perfil esperado es PERFIL_INVESTIGACION o el que usa research-browser.sh por omisión', () => {
  assert.equal(perfilEsperado({ PERFIL_INVESTIGACION: '~/mi perfil' }), path.join(os.homedir(), 'mi perfil'));
  assert.equal(perfilEsperado({}), path.join(os.homedir(), '.perfil-investigacion'));
});

test('conecta solo al navegador lanzado con el perfil de investigación', () => {
  const env = { CDP_PUERTO: '9400', PERFIL_INVESTIGACION: '/home/x/.perfil investigacion' };
  assert.equal(urlCdpVerificada(env, () => PROCESOS), 'http://127.0.0.1:9400');
});

test('se niega sin puerto personal definido si el puerto es de otro navegador o de ninguno', () => {
  const env = { PERFIL_INVESTIGACION: '/home/x/.perfil investigacion' };
  assert.throws(() => urlCdpVerificada({ ...env, CDP_PUERTO: '9500' }, () => PROCESOS), /no es el navegador de investigación/);
  assert.throws(() => urlCdpVerificada({ ...env, CDP_PUERTO: '9600' }, () => PROCESOS), /no es el navegador de investigación/);
  assert.throws(() => urlCdpVerificada({ CDP_PUERTO: '9400', PERFIL_INVESTIGACION: '/otro' }, () => PROCESOS), ErrorDeConfiguracion);
});

test('si no puede leer los procesos, no conecta', () => {
  const env = { CDP_PUERTO: '9400', PERFIL_INVESTIGACION: '/home/x/.perfil investigacion' };
  assert.throws(() => urlCdpVerificada(env, () => { throw new Error('sin ps'); }), /No pude verificar/);
});
