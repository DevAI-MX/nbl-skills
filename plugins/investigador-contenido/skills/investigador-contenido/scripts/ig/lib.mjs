// Conexión al navegador de investigación aislado y llamadas a la API web de Instagram con la sesión de esa pestaña.
import { CdpPage } from './cdp-lite.mjs';
import { urlCdpVerificada, elegirPestana } from './config.mjs';

const ID_APP_WEB_INSTAGRAM = '936619743392459'; // el que manda la propia web de Instagram en sus peticiones

export class AlertaDeSesion extends Error {
  constructor(detalle) {
    super('ALERTA_SESION: ' + detalle);
    this.alerta = true;
  }
}

export async function connect(idPestana, env = process.env) {
  const pestanas = await (await fetch(`${urlCdpVerificada(env)}/json`)).json();
  const page = new CdpPage(elegirPestana(pestanas, idPestana).webSocketDebuggerUrl);
  await page.connect();
  return page;
}

/** Instagram pide iniciar sesión, un checkpoint o frena la actividad: hay que parar, no reintentar en bucle. */
export function esAlertaDeSesion({ status, mensaje = '', url = '' }) {
  return status === 401
    || /login_required|checkpoint_required|challenge_required|feedback_required/.test(mensaje)
    || /accounts\/login|challenge/.test(url);
}

export function cuerpoComoJson(texto) {
  try {
    return JSON.parse(texto.startsWith('for (;;);') ? texto.slice(9) : texto);
  } catch {
    return null;
  }
}

function expresionFetch(ruta, metodo, cuerpo) {
  const cabeceraFormulario = cuerpo ? "'content-type':'application/x-www-form-urlencoded'," : '';
  const cuerpoFetch = cuerpo ? `body:${JSON.stringify(cuerpo)},` : '';
  return `(async()=>{try{
    const csrf = (document.cookie.match(/csrftoken=([^;]+)/)||[])[1]||'';
    const r = await fetch(${JSON.stringify(ruta)}, {method:${JSON.stringify(metodo)}, credentials:'include',
      headers:{'x-ig-app-id':'${ID_APP_WEB_INSTAGRAM}','x-requested-with':'XMLHttpRequest','x-csrftoken':csrf, ${cabeceraFormulario}},
      ${cuerpoFetch}});
    return {status:r.status, url:r.url, txt: await r.text()};
  }catch(e){return {status:-1, txt:String(e.message||e)}}})()`;
}

export async function api(page, ruta, { method = 'GET', body = null } = {}) {
  const res = await page.evaluate(expresionFetch(ruta, method, body), { awaitPromise: true });
  const json = cuerpoComoJson(res.txt || '');
  if (esAlertaDeSesion({ status: res.status, mensaje: json?.message || '', url: res.url || '' })) {
    throw new AlertaDeSesion(`${res.status} ${json?.message || ''} ${res.url || ''}`);
  }
  return { status: res.status, json, raw: json ? null : (res.txt || '').slice(0, 300) };
}

export const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
export const jitter = (a, b) => sleep(a + Math.random() * (b - a));
