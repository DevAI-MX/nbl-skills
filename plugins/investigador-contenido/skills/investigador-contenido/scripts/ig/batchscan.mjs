// Escanea en lote la pestaña /reels/ (o el feed) de varias cuentas.
// USO: node batchscan.mjs <handles.json> [scrolls=8] [feed]
//   Los escaneos van a <carpeta de la lista>/escaneos o a ESCANEOS_DIR (relativa a esa carpeta), igual que pasos.py.
//   Salta las cuentas ya escaneadas; FORCE=1 las vuelve a escanear. TARGET fija la pestaña. Código 3 = login o checkpoint.
//   Tras unas 25 cuentas la conexión puede morir (CDP timeout: Network.enable): reinicia el navegador y sigue.
import fs from 'node:fs';
import path from 'node:path';
import { connect, jitter } from './lib.mjs';
import { scanReels } from './scanlib.mjs';
import { carpetaDeLaCorrida, carpetaEscaneos, CODIGO_ALERTA } from './config.mjs';

function resumen(h, r) {
  const top = r.items.filter((x) => x.play_count).sort((a, b) => b.play_count - a.play_count)[0];
  const marcas = `${r.notFound ? ' NOTFOUND' : ''}${r.privado ? ' PRIVADA' : ''}`;
  return `@${h}: ${r.followers} seg | ${r.items.length} items | top ${top ? `${top.code} ${top.visible}` : '-'}${marcas}`;
}

async function main() {
  const [lista, scrolls = '8', modo = ''] = process.argv.slice(2);
  if (!lista) { console.error('uso: node batchscan.mjs <handles.json> [scrolls=8] [feed]'); process.exit(1); }
  const handles = JSON.parse(fs.readFileSync(lista, 'utf8'));
  const feed = modo === 'feed';
  const carpeta = carpetaEscaneos(process.env, carpetaDeLaCorrida(lista));
  const page = await connect(process.env.TARGET);
  for (const h of handles) {
    if (fs.existsSync(path.join(carpeta, `${h}${feed ? '.feed' : ''}.json`)) && !process.env.FORCE) continue;
    try {
      console.error(resumen(h, await scanReels(page, h, { maxScrolls: parseInt(scrolls, 10), feed, carpeta })));
    } catch (e) {
      console.error(`@${h}: ERR ${e.message}`);
      if (e.alerta) { page.close(); process.exit(CODIGO_ALERTA); }
    }
    await jitter(2500, 4500);
  }
  page.close();
}

main().then(() => process.exit(0), (e) => { console.error(e.message); process.exit(1); });
