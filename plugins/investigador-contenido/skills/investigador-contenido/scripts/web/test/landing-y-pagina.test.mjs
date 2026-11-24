import { test } from 'node:test';
import assert from 'node:assert/strict';
import { paginasParaSeguir, redirecciones, siguientePaso, slugDe, tecnologia } from '../landing-lib.mjs';
import { idsDePagina, tituloDe } from '../pagina-fb.mjs';
import { opcionesDeLanzamiento, perfilTemporal } from '../navegador-local.mjs';
import fs from 'node:fs';
import os from 'node:os';

const html = `<html><head><script src="https://connect.facebook.net/en_US/fbevents.js"></script></head>
<body><form data-redirect_url="https://clase.example.com/gracias-registro"></form>
<a href="https://chat.whatsapp.com/AbC123xyz">grupo</a>
<a href="https://clase.example.com/gracias-registro">gracias</a>
<a href="https://pay.hotmart.com/X123?off=1&amp;b=2">comprar</a>
<script>var cfg = {"thank_you_url": "https://clase.example.com/confirmado"};</script></body></html>`;

test('slug estable y corto para la carpeta de cada landing', () => {
  assert.equal(slugDe('https://clase.example.com/registro?a=1'), 'clase_example_com_registro_a_1');
  assert.ok(slugDe('https://x.example.com/' + 'a'.repeat(200)).length <= 90);
});

test('siguiente paso del embudo: grupo, gracias y pago, sin repetir', () => {
  const s = siguientePaso(html);
  assert.ok(s.includes('chat.whatsapp.com/AbC123xyz'));
  assert.ok(s.includes('https://clase.example.com/gracias-registro'));
  assert.ok(s.includes('pay.hotmart.com/X123?off=1&b=2'));
  assert.equal(new Set(s).size, s.length);
});

test('redirecciones configuradas en el código', () => {
  const r = redirecciones(html);
  assert.ok(r.includes('redirect_url = https://clase.example.com/gracias-registro'));
  assert.ok(r.includes('thank_you_url = https://clase.example.com/confirmado'));
});

test('huella tecnológica', () => {
  assert.deepEqual(tecnologia(html), ['Meta Pixel', 'Hotmart']);
});

test('abre como máximo 2 páginas de gracias del mismo dominio y 1 de pago', () => {
  const sig = ['https://clase.example.com/gracias-1', 'https://clase.example.com/gracias-2', 'https://clase.example.com/gracias-3',
    'https://otro.example.com/gracias', 'pay.hotmart.com/X1'];
  assert.deepEqual(paginasParaSeguir(sig, 'clase.example.com'),
    ['https://clase.example.com/gracias-1', 'https://clase.example.com/gracias-2', 'https://pay.hotmart.com/X1']);
  assert.deepEqual(paginasParaSeguir([], 'x'), []);
});

test('id de anunciante de una página pública de Facebook', () => {
  const pagina = '<title>Taller Ejemplo | Facebook</title> fb://page/111 "pageID":"222" "pageID":"222" "delegate_page":{"id":"333"';
  assert.deepEqual(idsDePagina(pagina), ['111', '222', '333']);
  assert.equal(tituloDe(pagina), 'Taller Ejemplo | Facebook');
  assert.deepEqual(idsDePagina('<html>'), []);
});

test('el navegador se elige por NAVEGADOR y el perfil es temporal y nuevo', () => {
  assert.deepEqual(opcionesDeLanzamiento({}), { headless: true });
  assert.deepEqual(opcionesDeLanzamiento({ NAVEGADOR: '/ruta/chrome' }, { locale: 'es-MX' }),
    { headless: true, executablePath: '/ruta/chrome', locale: 'es-MX' });
  const dir = perfilTemporal('prueba-');
  assert.ok(dir.startsWith(os.tmpdir()));
  assert.deepEqual(fs.readdirSync(dir), []);
  fs.rmdirSync(dir);
});
