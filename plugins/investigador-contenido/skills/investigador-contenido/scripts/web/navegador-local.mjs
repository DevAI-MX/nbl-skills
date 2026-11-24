// Lo común para los scripts que usan Playwright: cargarlo desde donde corres y lanzar un navegador headless aparte.
//   NAVEGADOR   ruta del ejecutable de Chrome, Chromium o Brave (opcional: sin ella usa el Chromium de Playwright)
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { createRequire } from 'node:module';

export class FaltaPlaywright extends Error {}

/** Playwright se busca junto al script y, si no está, en la carpeta donde corres (npm i playwright ahí). */
export async function cargarPlaywright(cwd = process.cwd()) {
  try {
    return await import('playwright');
  } catch {
    try {
      return createRequire(path.join(cwd, 'cargar.js'))('playwright');
    } catch {
      throw new FaltaPlaywright('Falta Playwright: corre "npm i playwright" en la carpeta desde donde lanzas el script.');
    }
  }
}

export function opcionesDeLanzamiento(env = process.env, extra = {}) {
  return { headless: true, ...(env.NAVEGADOR ? { executablePath: env.NAVEGADOR } : {}), ...extra };
}

/** Perfil nuevo y vacío en la carpeta temporal del sistema: sin sesión y sin tocar el navegador personal. */
export function perfilTemporal(prefijo) {
  return fs.mkdtempSync(path.join(os.tmpdir(), prefijo));
}

export const UA_ESCRITORIO = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36';
