import { test } from 'node:test';
import assert from 'node:assert/strict';
import { bloquesJson, laminasDe, metaDe, nodoDelPost, shortcodeDe } from '../carrusel-lib.mjs';

const nodo = (extra) => ({ code: 'ABC_1', user: { username: 'cuenta_ejemplo' }, caption: { text: 'Comenta GUIA' },
  taken_at: 1780000000, like_count: 10, comment_count: 2, ...extra }); // vault:inventado
const lamina = (n, video = false) => ({ media_type: video ? 2 : 1, original_width: 1080, original_height: 1350,
  accessibility_caption: `lámina ${n}`, image_versions2: { candidates: [{ url: `https://example.invalid/${n}.jpg` }] },
  ...(video ? { video_versions: [{ url: `https://example.invalid/${n}.mp4` }] } : {}) });

test('código del post en /p/, /reel/ y /tv/; otra URL es error', () => {
  assert.equal(shortcodeDe('https://www.instagram.com/p/ABC_1/?img_index=2'), 'ABC_1');
  assert.equal(shortcodeDe('https://www.instagram.com/cuenta/reel/R-9/'), 'R-9');
  assert.equal(shortcodeDe('https://www.instagram.com/tv/T1/'), 'T1');
  assert.throws(() => shortcodeDe('https://www.instagram.com/cuenta/'), /no es un post/);
});

test('saca los bloques JSON incrustados del HTML', () => {
  const html = '<script type="application/json" data-x="1">{"a":1}</script><script>no</script><script type="application/json">{"b":2}</script>';
  assert.deepEqual(bloquesJson(html), ['{"a":1}', '{"b":2}']);
});

test('elige el nodo del post con más láminas e ignora bloques rotos o ajenos', () => {
  const corto = nodo({ carousel_media: [lamina(1)] });
  const completo = nodo({ carousel_media: [lamina(1), lamina(2), lamina(3)] });
  const bloques = ['{roto', JSON.stringify({ otro: { code: 'XYZ', image_versions2: {} } }),
    JSON.stringify({ a: [corto, { b: completo }] })];
  assert.equal(nodoDelPost(bloques, 'ABC_1').carousel_media.length, 3);
  assert.equal(nodoDelPost(bloques, 'NADA'), null);
});

test('cada lámina con su tipo, medidas, texto alternativo y la URL a tamaño completo', () => {
  const r = laminasDe(nodo({ carousel_media: [lamina(1), lamina(2, true)] }));
  assert.deepEqual(r.map((l) => [l.lamina, l.tipo, l.url, l.alt]), [
    [1, 'imagen', 'https://example.invalid/1.jpg', 'lámina 1'], [2, 'video', 'https://example.invalid/2.jpg', 'lámina 2']]);
  assert.equal(laminasDe(nodo({ image_versions2: { candidates: [{ url: 'https://example.invalid/u.jpg' }] } })).length, 1);
});

test('meta del post: autor, caption, fecha, cifras y total de láminas', () => {
  const m = metaDe(nodo({ carousel_media: [lamina(1), lamina(2)] }), 'https://www.instagram.com/p/ABC_1/', '/salida/ABC_1');
  assert.equal(m.author, 'cuenta_ejemplo');
  assert.equal(m.caption, 'Comenta GUIA');
  assert.equal(m.total_slides, 2);
  assert.equal(m.taken_at, new Date(1780000000 * 1000).toISOString()); // vault:inventado
  assert.equal(m.dir, '/salida/ABC_1');
});

test('un carrusel sin ninguna lámina bajada cuenta como fallo, no como hecho', async () => {
  const { estadoDeDescarga } = await import('../carrusel-lib.mjs');
  const meta = (archivos) => ({ total_slides: 3, slides: archivos.map((file, i) => ({ slide: i + 1, file })) });
  assert.deepEqual(estadoDeDescarga(meta(['a.jpg', 'b.jpg', 'c.jpg'])), { ok: true, bajadas: 3, faltan: 0 });
  assert.deepEqual(estadoDeDescarga(meta(['a.jpg', null, 'c.jpg'])), { ok: true, bajadas: 2, faltan: 1 });
  assert.deepEqual(estadoDeDescarga(meta([null, null, null])), { ok: false, bajadas: 0, faltan: 3 });
});
