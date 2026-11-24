import { test } from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const IG = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const SCRIPTS_CON_GUARDA = ['serp.mjs', 'minfo.mjs', 'comments.mjs', 'fichas-por-codigo.mjs'];

function carpetaRara() {
  const base = fs.mkdtempSync(path.join(os.tmpdir(), 'ruta con espacio y acentuación ñ '));
  const enlace = path.join(base, 'enlace a ig');
  fs.symlinkSync(IG, enlace);
  return enlace;
}

for (const script of SCRIPTS_CON_GUARDA) {
  test(`${script} arranca desde una ruta con espacio, acento y enlace simbólico`, () => {
    const r = spawnSync(process.execPath, [path.join(carpetaRara(), script)], { encoding: 'utf8', env: {} });
    assert.equal(r.status, 1, r.stderr);
    assert.match(r.stderr, /uso:/);
  });
}

test('esPrincipal compara rutas reales, no textos', async () => {
  const { esPrincipal } = await import('../arranque.mjs');
  const real = path.join(IG, 'serp.mjs');
  const enlace = path.join(carpetaRara(), 'serp.mjs');
  assert.equal(esPrincipal(new URL(`file://${real}`).href, enlace), true);
  assert.equal(esPrincipal(new URL(`file://${real}`).href, path.join(IG, 'minfo.mjs')), false);
  assert.equal(esPrincipal(new URL(`file://${real}`).href, undefined), false);
});
