/**
 * Cliente CDP crudo (sin Playwright) que le habla a UNA página ya abierta por su websocket de página.
 *
 * Existe porque connectOverCDP() a nivel de navegador a veces se queda colgado en el attach aunque el
 * navegador responda a /json; conectar directo al webSocketDebuggerUrl de una página funciona al instante.
 * Reimplementa lo mínimo: navegar, evaluar, escuchar respuestas de red y hacer scroll con eventos de verdad.
 * Nunca abre ni cierra pestañas por su cuenta. Usa el WebSocket global de Node (22 o más reciente).
 */
const TIEMPO_COMANDO_MS = 30000;
const TIEMPO_RUEDA_MS = 6000;

export class CdpPage {
  constructor(wsUrl, { tiempoRuedaMs = TIEMPO_RUEDA_MS } = {}) {
    this.wsUrl = wsUrl;
    this.tiempoRuedaMs = tiempoRuedaMs;
    this.ws = null;
    this.nextId = 1;
    this.pending = new Map();
    this.listeners = new Map();
  }

  async connect() {
    this.ws = new WebSocket(this.wsUrl);
    await new Promise((resolve, reject) => {
      this.ws.addEventListener('open', resolve, { once: true });
      this.ws.addEventListener('error', () => reject(new Error(`no pude abrir el websocket ${this.wsUrl}`)), { once: true });
    });
    this.ws.addEventListener('message', (ev) => this.recibir(JSON.parse(String(ev.data))));
  }

  recibir(msg) {
    if (msg.id && this.pending.has(msg.id)) {
      const { resolve, reject, temporizador } = this.pending.get(msg.id);
      clearTimeout(temporizador);
      this.pending.delete(msg.id);
      if (msg.error) reject(new Error(msg.error.message || JSON.stringify(msg.error)));
      else resolve(msg.result);
      return;
    }
    for (const cb of this.listeners.get(msg.method) || []) cb(msg.params);
  }

  send(method, params = {}, timeoutMs = TIEMPO_COMANDO_MS) {
    const id = this.nextId++;
    return new Promise((resolve, reject) => {
      const temporizador = setTimeout(() => {
        this.pending.delete(id);
        reject(new Error(`CDP timeout: ${method}`));
      }, timeoutMs);
      this.pending.set(id, { resolve, reject, temporizador });
      this.ws.send(JSON.stringify({ id, method, params }));
    });
  }

  on(event, cb) {
    if (!this.listeners.has(event)) this.listeners.set(event, []);
    this.listeners.get(event).push(cb);
  }

  off(event) {
    this.listeners.delete(event);
  }

  async goto(url, { timeout = 25000 } = {}) {
    await this.send('Page.enable');
    const cargada = new Promise((resolve) => this.on('Page.loadEventFired', () => { this.off('Page.loadEventFired'); resolve(); }));
    await this.send('Page.navigate', { url });
    let temporizador;
    const limite = new Promise((resolve) => { temporizador = setTimeout(resolve, timeout); });
    await Promise.race([cargada, limite]); // la carga es de mejor esfuerzo: Instagram nunca queda "quieto"
    clearTimeout(temporizador);
  }

  async evaluate(expression, { awaitPromise = false } = {}) {
    const res = await this.send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise });
    if (res.exceptionDetails) {
      throw new Error(res.exceptionDetails.exception?.description || JSON.stringify(res.exceptionDetails));
    }
    return res.result?.value;
  }

  /**
   * Instagram solo carga más cuadrícula con eventos de entrada confiables (isTrusted): un scroll por
   * Runtime.evaluate no trae contenido nuevo. Input.dispatchMouseEvent sí, pero en pestañas de fondo a
   * veces se cuelga; con un tiempo corto y, si falla, un scroll por script para al menos no perder posición.
   */
  async wheel(deltaY = 2200, x = 640, y = 400) {
    try {
      await this.send('Input.dispatchMouseEvent', { type: 'mouseWheel', x, y, deltaX: 0, deltaY }, this.tiempoRuedaMs);
    } catch {
      await this.evaluate(`window.scrollBy(0, ${Number(deltaY)})`).catch(() => {});
    }
  }

  close() {
    if (this.ws) this.ws.close();
  }
}
