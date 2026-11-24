#!/usr/bin/env python3
"""Auditoría unificada de una cuenta: reels de /reels/ y publicaciones del feed unidos por código, sin repetir.

  python3 auditoria.py <carpeta> <handle> <salida.md> [--top 50]

Lee <escaneos>/<handle>.json (batchscan.mjs) y <handle>.feed.json (batchscan.mjs ... feed); los escaneos se buscan como
en pasos.py (ESCANEOS_DIR absoluta o relativa a la carpeta, o <carpeta>/escaneos). Escribe las tres vistas (ranking
maestro por comentarios, solo carruseles, solo reels), los reels por vistas y por vistas entre comentarios, y cuántos
reels salieron solo en /reels/. El tema de cada pieza lo pones tú después de ver portadas y captions.
"""
import argparse
import json
import os
import sys

TIPOS = {'clips': 'Reel', 'carousel_container': 'Carrusel'}


def pieza(item, previa=None):
    unida = dict(previa or {})
    for clave, valor in item.items():
        if valor is not None:
            unida[clave] = valor
    return unida


def normalizar(item):
    codigo = item['code']
    tipo = TIPOS.get(item.get('type'), 'Imagen o video')
    enlace = f'https://www.instagram.com/reel/{codigo}/' if tipo == 'Reel' else f'https://www.instagram.com/p/{codigo}/'
    vistas = item.get('play_count') or item.get('vistas_visibles')
    comentarios = item.get('comment_count') or 0
    return {'code': codigo, 'tipo': tipo, 'comentarios': comentarios, 'likes': item.get('like_count') or 0,
            'vistas': vistas, 'ratio': round(vistas / comentarios, 1) if vistas and comentarios else None,
            'taken_at': item.get('taken_at'), 'caption': item.get('caption') or '', 'enlace': enlace}


def unir(escaneo_reels, escaneo_feed):
    """Piezas únicas por código y cuántos reels aparecieron solo en /reels/ (el feed esconde reels)."""
    por_codigo = {}
    for item in escaneo_feed.get('items', []) + escaneo_reels.get('items', []):
        por_codigo[item['code']] = pieza(item, por_codigo.get(item['code']))
    del_feed = {i['code'] for i in escaneo_feed.get('items', [])}
    solo_en_reels = sum(1 for i in escaneo_reels.get('items', []) if i['code'] not in del_feed)
    return [normalizar(i) for i in por_codigo.values()], solo_en_reels


def top(items, campo, n):
    con_dato = [i for i in items if i.get(campo)]
    return sorted(con_dato, key=lambda i: -i[campo])[:n]


def celda(texto):
    return (texto or '').replace('|', '/').replace('\n', ' ').strip()[:120]


def vistas_texto(item):
    return f"{item['vistas']:,}" if item['vistas'] else 'sin dato'


def tabla(items):
    filas = ['| # | Tipo | Comentarios | Likes | Vistas | Enlace | Caption |', '|---|---|---|---|---|---|---|']
    filas += [f"| {n} | {i['tipo']} | {i['comentarios']:,} | {i['likes']:,} | {vistas_texto(i)} | [abrir]({i['enlace']}) | "
              f"{celda(i['caption'])} |" for n, i in enumerate(items, 1)]
    return '\n'.join(filas)


def documento(handle, seguidores, items, solo_en_reels, n):
    reels = [i for i in items if i['tipo'] == 'Reel']
    cuenta = {t: sum(1 for i in items if i['tipo'] == t) for t in ('Reel', 'Carrusel', 'Imagen o video')}
    return '\n'.join([
        f'# Auditoría unificada de @{handle}', '',
        f"{seguidores:,} seguidores (los de hoy). {len(items)} publicaciones únicas: {cuenta['Reel']} reels, "
        f"{cuenta['Carrusel']} carruseles y {cuenta['Imagen o video']} imágenes o videos. "
        f'{solo_en_reels} reels salieron solo en la pestaña /reels/ y no en el feed.', '',
        f'## Ranking maestro por comentarios (top {n})', '', tabla(top(items, 'comentarios', n)), '',
        '## Solo carruseles', '', tabla(top([i for i in items if i['tipo'] == 'Carrusel'], 'comentarios', n)), '',
        '## Solo reels', '', tabla(top(reels, 'comentarios', n)), '',
        f'## Reels por vistas (top {n})', '', tabla(top(reels, 'vistas', n)), '',
        '## Reels por vistas entre comentarios', '', tabla(top(reels, 'ratio', n)), ''])


def leer(ruta):
    with open(ruta, encoding='utf-8') as archivo:
        return json.load(archivo)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('carpeta')
    ap.add_argument('handle')
    ap.add_argument('salida')
    ap.add_argument('--top', type=int, default=50)
    a = ap.parse_args(argv)
    escaneos = os.path.abspath(os.path.join(a.carpeta, os.environ.get('ESCANEOS_DIR') or 'escaneos'))
    reels = leer(os.path.join(escaneos, f'{a.handle}.json'))
    feed = leer(os.path.join(escaneos, f'{a.handle}.feed.json'))
    items, solo_en_reels = unir(reels, feed)
    seguidores = reels.get('followers') or feed.get('followers') or 0
    with open(a.salida, 'w', encoding='utf-8') as archivo:
        archivo.write(documento(a.handle, seguidores, items, solo_en_reels, a.top))
    print(f'ok {a.salida}: {len(items)} piezas, {solo_en_reels} solo en /reels/')
    return 0


if __name__ == '__main__':
    sys.exit(main())
