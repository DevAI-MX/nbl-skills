// Captura de una URL pública en un navegador headless aparte (no toca el navegador personal).
// Sirve también para un anuncio de la Biblioteca cuando adlib-captura.mjs recorta otra tarjeta:
//   node captura-simple.mjs "https://www.facebook.com/ads/library/?id=<id>" anuncio.png 1280 1600
// USO: node captura-simple.mjs <url> <salida.png> [ancho=1280] [alto=900] [texto del botón a pulsar]
import { cargarPlaywright, opcionesDeLanzamiento } from './navegador-local.mjs';

async function main() {
  const [url, salida, ancho = '1280', alto = '900', clic] = process.argv.slice(2);
  if (!url || !salida) { console.error('uso: node captura-simple.mjs <url> <salida.png> [ancho] [alto] [boton]'); process.exit(1); }
  const { chromium } = await cargarPlaywright();
  const navegador = await chromium.launch(opcionesDeLanzamiento(process.env, { args: ['--mute-audio'] }));
  try {
    const pagina = await navegador.newPage({ viewport: { width: Number(ancho), height: Number(alto) }, deviceScaleFactor: 2, locale: 'es-MX' });
    await pagina.goto(url, { waitUntil: 'networkidle', timeout: 60000 }).catch(() => {});
    await pagina.waitForTimeout(2500);
    if (clic) await pagina.getByText(clic, { exact: false }).first().click({ timeout: 5000 }).catch(() => console.log('sin clic'));
    await pagina.waitForTimeout(1500);
    await pagina.screenshot({ path: salida });
    console.log('ok', salida);
  } finally {
    await navegador.close();
  }
}

main().then(() => process.exit(0), (e) => { console.error(e.message); process.exit(1); });
