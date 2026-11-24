import { test } from 'node:test';
import assert from 'node:assert/strict';
import { ficha } from '../fichas-por-codigo.mjs';
import { fichaCorta } from '../minfo.mjs';
import { comentariosDeRespuesta } from '../comments.mjs';
import { guardarMedios } from '../serp.mjs';

const carrusel = { code: 'C1', product_type: 'carousel_container', media_type: 8, user: { username: 'u', pk: '5' },
  like_count: 10, comment_count: 2, taken_at: 1, caption: { text: 'cap' }, carousel_media_count: 2,
  carousel_media: [
    { media_type: 1, image_versions2: { candidates: [{ url: 'https://example.invalid/1.jpg' }] } },
    { media_type: 2, image_versions2: { candidates: [{ url: 'https://example.invalid/2.jpg' }] }, video_versions: [{ url: 'https://example.invalid/2.mp4' }] },
  ] };

test('la ficha trae cada lámina con su imagen y, si es video, su video', () => {
  const f = ficha(carrusel);
  assert.deepEqual(f.partes, [
    { media_type: 1, imagen: 'https://example.invalid/1.jpg', video: null },
    { media_type: 2, imagen: 'https://example.invalid/2.jpg', video: 'https://example.invalid/2.mp4' },
  ]);
  assert.equal(f.plays, null);
  assert.equal(f.caption, 'cap');
});

test('un reel suelto es una sola parte', () => {
  const f = ficha({ code: 'R', video_versions: [{ url: 'https://example.invalid/r.mp4' }], media_type: 2, play_count: 7, video_duration: 31.2 });
  assert.equal(f.partes.length, 1);
  assert.equal(f.partes[0].video, 'https://example.invalid/r.mp4');
  assert.equal(f.dur, 31.2);
});

test('la ficha corta guarda láminas, coautores y si los comentarios están desactivados', () => {
  const f = fichaCorta({ ...carrusel, coauthor_producers: [{ username: 'co' }], comments_disabled: true });
  assert.deepEqual([f.slides, f.coauthors, f.comments_disabled, f.thumb], [2, ['co'], true, 'https://example.invalid/1.jpg']);
});

test('comentarios de primer nivel con likes y respuestas', () => {
  const r = comentariosDeRespuesta({ comments: [{ user: { username: 'a' }, text: 'GUIA', comment_like_count: 3, child_comment_count: 0 }] });
  assert.deepEqual(r, [{ u: 'a', t: 'GUIA', likes: 3, replies: 0 }]);
  assert.deepEqual(comentariosDeRespuesta({}), []);
});

test('la misma pieza hallada por dos búsquedas guarda ambas consultas una sola vez', () => {
  const base = { media: {} };
  guardarMedios(base, [{ code: 'X', queries: ['a'] }]);
  guardarMedios(base, [{ code: 'X', queries: ['b'] }, { code: 'X', queries: ['a'] }]);
  assert.deepEqual(base.media.X.queries, ['a', 'b']);
});
