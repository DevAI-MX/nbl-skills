#!/usr/bin/env python3
"""Hoja HTML con las paletas de los competidores lado a lado y la paleta propia al final, más los choques medidos.

  python3 hoja_paletas.py <paletas.json> <salida.html> [--etiquetas etiquetas.json] [--propia propia.json]

paletas.json: {handle: salida de paleta.py}. etiquetas.json (opcional): {handle: {"#HEX": "qué es: fondo, texto, piel..."}},
revisadas a ojo sobre las portadas. propia.json (opcional): {"titulo": "...", "colores": [["#HEX", "nombre"], ...]}.
Choque: un color del competidor a menos de 15 de distancia (ΔE76) de un color propio.
"""
import argparse
import html
import json
import sys

from paleta import delta_e76

MISMA_FAMILIA = 15


def tinta(color):
    r, g, b = (int(color.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4))
    return '#111' if 0.299 * r + 0.587 * g + 0.114 * b > 150 else '#fff'


def muestra(color, parte, etiqueta=''):
    porcentaje = f'<span>{parte}%</span>' if parte is not None else ''
    return (f'<div class="sw"><div class="chip" style="background:{color};color:{tinta(color)}"><b>{color}</b>{porcentaje}</div>'
            f'<div class="lab">{html.escape(etiqueta)}</div></div>')


def tarjeta(handle, datos, etiquetas):
    dominantes = ''.join(muestra(c, p, etiquetas.get(c, '')) for c, p in datos['dominantes'])
    acentos = ''.join(muestra(c, p, 'acento saturado') for c, p in datos.get('acentos', [])) \
        or '<p class="none">Sin acentos saturados (paleta neutra).</p>'
    return (f'<section class="card"><h2>@{html.escape(handle)}</h2><p class="meta">{datos["n_imgs"]} imágenes de diseño · '
            f'píxeles saturados {datos.get("pixeles_saturados_pct", 0)}%</p><h3>Dominantes</h3><div class="row">{dominantes}</div>'
            f'<h3>Acentos</h3><div class="row">{acentos}</div></section>')


def choques(paletas, propia):
    salida = []
    for color, _nombre in propia.get('colores', []):
        cercanos = sorted(((h, c, delta_e76(color, c)) for h, d in paletas.items()
                           for c, _ in d['dominantes'] + d.get('acentos', [])), key=lambda x: x[2])
        salida.append({'color': color, 'cercanos': [x for x in cercanos if x[2] < MISMA_FAMILIA]})
    return salida


ESTILO = """:root{--bg:#f4f3f1;--card:#fff;--ink:#16161a;--mut:#5d5d66;--line:#e2e0dc}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#141416;--card:#1d1d21;--ink:#ececf0;--mut:#a0a0aa;--line:#2e2e34}}
:root[data-theme="dark"]{--bg:#141416;--card:#1d1d21;--ink:#ececf0;--mut:#a0a0aa;--line:#2e2e34}
*{box-sizing:border-box} body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.45 system-ui,sans-serif}
main{max-width:1180px;margin:0 auto;padding:24px 16px 64px} .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,520px),1fr));gap:16px}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:16px} .mine{border:2px solid var(--ink)}
h2{margin:0;font-size:18px} h3{font-size:12px;text-transform:uppercase;letter-spacing:.06em;color:var(--mut);margin:12px 0 6px}
.meta,.lab,.none{color:var(--mut);font-size:12px} .row{display:flex;flex-wrap:wrap;gap:8px} .sw{width:96px}
.chip{height:60px;border-radius:9px;padding:6px;display:flex;flex-direction:column;justify-content:space-between;font-size:12px}
table{width:100%;border-collapse:collapse;font-size:13px} td,th{border-bottom:1px solid var(--line);padding:8px 6px;text-align:left}"""


def pagina(paletas, etiquetas, propia):
    tarjetas = ''.join(tarjeta(h, d, etiquetas.get(h, {})) for h, d in paletas.items())
    mia = ''
    if propia:
        colores = ''.join(muestra(c, None, n) for c, n in propia['colores'])
        filas = ''.join(f"<tr><td>{c['color']}</td><td>{', '.join(f'@{h} {col} (ΔE {d})' for h, col, d in c['cercanos']) or 'ninguno'}</td></tr>"
                        for c in choques(paletas, propia))
        mia = (f'<h1>{html.escape(propia["titulo"])}</h1><div class="grid"><section class="card mine"><div class="row">{colores}</div>'
               f'</section></div><section class="card"><h2>Choques (ΔE76 menor de {MISMA_FAMILIA})</h2>'
               f'<table><tr><th>Color propio</th><th>Competidores con un color de la misma familia</th></tr>{filas}</table></section>')
    return (f'<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>Paletas del nicho</title><style>{ESTILO}</style></head><body><main><h1>Paletas del nicho</h1>'
            f'<div class="grid">{tarjetas}</div>{mia}</main></body></html>')


def leer(ruta):
    if not ruta:
        return {}
    with open(ruta, encoding='utf-8') as archivo:
        return json.load(archivo)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('paletas')
    ap.add_argument('salida')
    ap.add_argument('--etiquetas')
    ap.add_argument('--propia')
    a = ap.parse_args(argv)
    with open(a.salida, 'w', encoding='utf-8') as archivo:
        archivo.write(pagina(leer(a.paletas), leer(a.etiquetas), leer(a.propia)))
    print('ok', a.salida)
    return 0


if __name__ == '__main__':
    sys.exit(main())
