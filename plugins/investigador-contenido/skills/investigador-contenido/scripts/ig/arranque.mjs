// ¿Este módulo es el que se corrió con node? Compara rutas reales: comparar el texto de la URL con process.argv[1]
// falla en silencio con espacios, acentos o enlaces simbólicos en la ruta.
import fs from 'node:fs';
import { fileURLToPath } from 'node:url';

function rutaReal(ruta) {
  try {
    return fs.realpathSync(ruta);
  } catch {
    return null;
  }
}

export function esPrincipal(urlDelModulo, rutaEjecutada = process.argv[1]) {
  if (!rutaEjecutada) return false;
  const modulo = rutaReal(fileURLToPath(urlDelModulo));
  return modulo !== null && modulo === rutaReal(rutaEjecutada);
}
