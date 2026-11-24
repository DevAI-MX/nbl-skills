// Configuración compartida por todos los recolectores. Todo sale de variables de entorno: nada fijo de una máquina.
//   CDP_PUERTO            puerto del navegador de investigación (obligatorio)
//   CDP_PUERTO_PERSONAL   puerto del navegador personal (opcional): si coincide, se niega a conectar
//   PERFIL_INVESTIGACION  perfil con que research-browser.sh lanzó el navegador (por omisión ~/.perfil-investigacion):
//                         SIEMPRE se verifica que el proceso del puerto use ese perfil; si no, no se conecta
//   ESCANEOS_DIR          carpeta de escaneos por cuenta; relativa a la carpeta de la corrida (por omisión <corrida>/escaneos)
//   TARGET                id de la pestaña CDP a usar (uno por proceso en paralelo)
import { execFileSync } from 'node:child_process';
import os from 'node:os';
import path from 'node:path';

export class ErrorDeConfiguracion extends Error {}

export function urlCdp(env = process.env) {
  const puerto = env.CDP_PUERTO || '';
  if (!/^\d{2,5}$/.test(puerto)) {
    throw new ErrorDeConfiguracion('Falta CDP_PUERTO: el puerto del navegador de investigación (research-browser.sh).');
  }
  if (env.CDP_PUERTO_PERSONAL && env.CDP_PUERTO_PERSONAL === puerto) {
    throw new ErrorDeConfiguracion('CDP_PUERTO es el de tu navegador personal: la investigación corre solo en el aislado.');
  }
  return `http://127.0.0.1:${puerto}`;
}

const PERFIL_POR_OMISION = '.perfil-investigacion'; // el mismo que usa research-browser.sh

export function perfilEsperado(env) {
  const perfil = env.PERFIL_INVESTIGACION || path.join('~', PERFIL_POR_OMISION);
  return path.resolve(perfil.replace(/^~(?=$|\/)/, os.homedir()));
}

/** Perfil (--user-data-dir) del proceso que escucha en ese puerto de depuración, o null si no hay ninguno. */
export function perfilDelPuerto(listaDeProcesos, puerto) {
  const marca = new RegExp(`--remote-debugging-port=${puerto}(?!\\d)`);
  const linea = listaDeProcesos.split('\n').find((l) => marca.test(l));
  const perfil = linea && linea.match(/--user-data-dir=(.+?)(?= --|$)/);
  return perfil ? perfil[1].trim() : null;
}

const leerProcesos = () => execFileSync('ps', ['-axww', '-o', 'command'], { encoding: 'utf8' });

/**
 * La URL del navegador de investigación, solo si el proceso de ese puerto fue lanzado con el perfil de investigación.
 * Así nunca se conecta al navegador personal aunque no se haya definido CDP_PUERTO_PERSONAL.
 */
export function urlCdpVerificada(env = process.env, procesos = leerProcesos) {
  const url = urlCdp(env);
  let lista;
  try {
    lista = procesos();
  } catch (e) {
    throw new ErrorDeConfiguracion(`No pude verificar qué navegador escucha en el puerto ${env.CDP_PUERTO}: ${e.message}`);
  }
  const perfil = perfilDelPuerto(lista, env.CDP_PUERTO);
  if (!perfil || path.resolve(perfil) !== perfilEsperado(env)) {
    throw new ErrorDeConfiguracion(`El puerto ${env.CDP_PUERTO} no es el navegador de investigación (perfil ${perfil || 'ninguno'}, `
      + `se esperaba ${perfilEsperado(env)}). Arráncalo con research-browser.sh start.`);
  }
  return url;
}

/** La carpeta de la corrida es la de la lista de cuentas: ahí mismo trabaja pasos.py. */
export function carpetaDeLaCorrida(rutaLista, cwd = process.cwd()) {
  return path.dirname(path.resolve(cwd, rutaLista));
}

/** Misma regla que pasos.py: ESCANEOS_DIR absoluta tal cual; relativa o ausente, contra la carpeta de la corrida. */
export function carpetaEscaneos(env, carpetaCorrida) {
  return path.resolve(carpetaCorrida, env.ESCANEOS_DIR || 'escaneos');
}

/** La pestaña pedida por id o, si no se pide, la primera de instagram.com. */
export function elegirPestana(pestanas, idPedido) {
  const elegida = idPedido
    ? pestanas.find((p) => p.id === idPedido)
    : pestanas.find((p) => p.type === 'page' && /instagram\.com/.test(p.url || ''));
  if (!elegida) {
    throw new ErrorDeConfiguracion(idPedido
      ? `No existe la pestaña ${idPedido} en el navegador de investigación.`
      : 'No hay pestaña de instagram.com abierta: créala con PUT /json/new?https://www.instagram.com/');
  }
  return elegida;
}

export const CODIGO_ALERTA = 3;
