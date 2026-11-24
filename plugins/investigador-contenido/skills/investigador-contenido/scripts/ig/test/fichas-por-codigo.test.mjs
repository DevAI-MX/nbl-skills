import { test } from 'node:test';
import assert from 'node:assert/strict';
import { pkDeCodigo } from '../fichas-por-codigo.mjs';

test('convierte el código de la URL en el pk real (reel público con fecha conocida)', () => {
  // pk confirmado: la API devolvió este reel con este código y su fecha sale del pk
  const pk = pkDeCodigo('DGt1qzqOeAq');
  assert.equal(pk, '3579753316981792810');
  const fecha = new Date(Number(BigInt(pk) >> 23n) + 1314220021721);
  assert.equal(fecha.toISOString().slice(0, 10), '2025-03-02');
});

test('los caracteres - y _ cuentan como 62 y 63', () => {
  assert.equal(pkDeCodigo('-'), '62');
  assert.equal(pkDeCodigo('_'), '63');
  assert.equal(pkDeCodigo('BA'), '64');
});
