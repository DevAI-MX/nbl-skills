// Escanea la pestaña /reels/ de UNA cuenta; con códigos objetivo deja de bajar cuando los encuentra todos.
// USO: node reelscan.mjs <handle> [maxScrolls=6] [codigo1,codigo2]
//   Córrelo desde la carpeta de la corrida: los escaneos van a ./escaneos o a ESCANEOS_DIR relativa a ella.
import { connect } from './lib.mjs';
import { scanReels } from './scanlib.mjs';
import { carpetaEscaneos, CODIGO_ALERTA } from './config.mjs';

async function main() {
  const [handle, scrolls = '6', codigos = ''] = process.argv.slice(2);
  if (!handle) { console.error('uso: node reelscan.mjs <handle> [maxScrolls] [codigos,coma]'); process.exit(1); }
  const objetivos = new Set(codigos.split(',').filter(Boolean));
  const page = await connect(process.env.TARGET);
  try {
    const r = await scanReels(page, handle, { maxScrolls: parseInt(scrolls, 10), objetivos, carpeta: carpetaEscaneos(process.env, process.cwd()) });
    console.log(JSON.stringify({ handle, followers: r.followers, label: r.followers_label, items: r.items.length,
      encontrados: [...objetivos].filter((c) => r.items.some((i) => i.code === c)) }));
  } catch (e) {
    console.error(e.message);
    process.exit(e.alerta ? CODIGO_ALERTA : 1);
  } finally {
    page.close();
  }
}

main().then(() => process.exit(0));
