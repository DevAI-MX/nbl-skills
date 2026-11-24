#!/usr/bin/env node
/**
 * render.mjs: renderiza slides HTML a PNG 1080×1350 (×2 retina = 2160×2700).
 *
 * Uso:
 *   node render.mjs --slides <dir> --out <dir> [--preview <archivo.html>] [--scale 2] [--format png|jpeg]
 *
 * - <slides-dir> debe contener slide-01.html, slide-02.html, ...
 * - <out-dir>    recibe slide-01.png, slide-02.png, ...
 * - preview.html (cuadrícula con todas las slides) va en <out-dir> o donde diga --preview
 *
 * - Busca playwright en node_modules de la carpeta donde lo ejecutas.
 * - Si defines BRAVE_PATH o BROWSER_PATH, usa ese navegador (tu Brave o tu Chrome) en vez del Chromium de Playwright.
 * - Espera a que carguen las fuentes antes de cada captura y siempre cierra el navegador.
 */

// Resolve playwright from the project's node_modules (cwd), not the skill directory
import { pathToFileURL } from 'node:url';
import { resolve as resolvePath } from 'node:path';
const playwrightPath = resolvePath(process.cwd(), 'node_modules', 'playwright', 'index.js');
const playwrightMod = await import(pathToFileURL(playwrightPath).href);
const { chromium } = playwrightMod.default ?? playwrightMod;
import { readdir, mkdir, writeFile, stat } from 'node:fs/promises';
import { join, resolve, relative, dirname } from 'node:path';

const SLIDE_W = 1080;
const SLIDE_H = 1350;

function parseArgs(argv) {
  const args = { scale: 2, format: 'png' };
  for (let i = 2; i < argv.length; i++) {
    const k = argv[i];
    const v = argv[i + 1];
    if (k === '--slides') { args.slides = v; i++; }
    else if (k === '--out') { args.out = v; i++; }
    else if (k === '--scale') { args.scale = Number(v); i++; }
    else if (k === '--format') { args.format = v; i++; }
    else if (k === '--preview') { args.preview = v; i++; }
  }
  if (!args.slides || !args.out) {
    console.error('Uso: node render.mjs --slides <dir> --out <dir> [--preview <archivo.html>] [--scale 2] [--format png|jpeg]');
    process.exit(1);
  }
  args.slides = resolve(args.slides);
  args.out = resolve(args.out);
  args.preview = resolve(args.preview || join(args.out, 'preview.html'));
  return args;
}

async function listSlideFiles(dir) {
  const entries = await readdir(dir);
  return entries
    .filter((f) => /^slide-\d+\.html$/i.test(f))
    .sort();
}

async function renderSlide(page, htmlPath, outPath, format) {
  const url = pathToFileURL(htmlPath).href;
  await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 });
  await page.evaluate(() => document.fonts.ready);
  // pequeño settle por si hay lazy paint de imágenes
  await page.waitForTimeout(200);
  await page.screenshot({
    path: outPath,
    type: format === 'jpeg' ? 'jpeg' : 'png',
    quality: format === 'jpeg' ? 92 : undefined,
    fullPage: false,
    clip: { x: 0, y: 0, width: SLIDE_W, height: SLIDE_H },
  });
}

function buildPreviewHtml(pngFiles) {
  const items = pngFiles
    .map(
      (f, i) => `
    <figure>
      <img src="${f}" alt="${f}">
      <figcaption>${i + 1}. ${f}</figcaption>
    </figure>`
    )
    .join('');
  return `<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <title>Preview carrusel</title>
  <style>
    body {
      margin: 0;
      padding: 24px;
      background: #111;
      color: #eee;
      font: 14px -apple-system, system-ui, sans-serif;
    }
    h1 { font-weight: 500; margin: 0 0 16px; }
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
      gap: 16px;
    }
    figure { margin: 0; background: #1a1a1a; border-radius: 8px; overflow: hidden; }
    figure img { width: 100%; display: block; aspect-ratio: 1080/1350; object-fit: contain; background: #000; }
    figcaption { padding: 8px 12px; font-size: 12px; color: #aaa; }
  </style>
</head>
<body>
  <h1>Preview del carrusel: ${pngFiles.length} slides</h1>
  <div class="grid">${items}
  </div>
</body>
</html>`;
}

async function main() {
  const args = parseArgs(process.argv);
  await mkdir(args.out, { recursive: true });

  const slideFiles = await listSlideFiles(args.slides);
  if (slideFiles.length === 0) {
    console.error(`No hay slide-NN.html en ${args.slides}`);
    process.exit(1);
  }
  console.log(`▶ Renderizando ${slideFiles.length} slides desde ${args.slides}`);

  const executablePath = process.env.BRAVE_PATH || process.env.BROWSER_PATH || undefined;
  const browser = await chromium.launch({ headless: true, ...(executablePath ? { executablePath } : {}) });
  let renderedPngs = [];
  try {
    const context = await browser.newContext({
      viewport: { width: SLIDE_W, height: SLIDE_H },
      deviceScaleFactor: args.scale,
    });
    const page = await context.newPage();

    for (const file of slideFiles) {
      const htmlPath = join(args.slides, file);
      const pngName = file.replace(/\.html$/i, args.format === 'jpeg' ? '.jpg' : '.png');
      const outPath = join(args.out, pngName);
      await renderSlide(page, htmlPath, outPath, args.format);
      const s = await stat(outPath);
      console.log(`  ✓ ${pngName} (${(s.size / 1024).toFixed(0)} KB)`);
      renderedPngs.push(pngName);
    }

    await context.close();
  } finally {
    await browser.close();
  }

  const previewPath = args.preview;
  const rutaPngs = relative(dirname(previewPath), args.out);
  const enlaces = renderedPngs.map((f) => (rutaPngs ? `${rutaPngs}/${f}` : f));
  await writeFile(previewPath, buildPreviewHtml(enlaces), 'utf8');
  console.log(`✓ Preview: ${previewPath}`);
  console.log(`✓ Render OK: ${renderedPngs.length} archivos en ${args.out}`);
}

main().catch((err) => {
  console.error('✗ Error en render:', err);
  process.exit(1);
});
