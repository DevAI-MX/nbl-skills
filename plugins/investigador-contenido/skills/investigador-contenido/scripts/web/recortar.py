#!/usr/bin/env python3
"""Parte cada shot.png (página completa en celular, de landing-scan.mjs) en tramos legibles para que un agente los lea.

  python3 recortar.py <carpeta_de_landing-scan>

Escribe shot_01.jpg, shot_02.jpg... y tramos.txt junto a cada shot.png. Salta las que ya tienen tramos. Necesita Pillow.
"""
import glob
import os
import sys

ALTO_TRAMO = 1800  # px reales; con escala 2 son 900 px de pantalla
MAX_TRAMOS = 18


def tramos(alto_total, alto=ALTO_TRAMO, maximo=MAX_TRAMOS):
    """[(desde, hasta)] en px y si la página quedó recortada por pasar del máximo de tramos."""
    cortes = [(y, min(y + alto, alto_total)) for y in range(0, alto_total, alto)]
    return cortes[:maximo], len(cortes) > maximo


def recortar_carpeta(base, abrir):
    hechas = []
    for shot in sorted(glob.glob(os.path.join(base, '*', 'shot.png'))):
        carpeta = os.path.dirname(shot)
        if os.path.exists(os.path.join(carpeta, 'shot_01.jpg')):
            continue
        imagen = abrir(shot).convert('RGB')
        ancho, alto = imagen.size
        cortes, recortada = tramos(alto)
        for n, (desde, hasta) in enumerate(cortes, 1):
            imagen.crop((0, desde, ancho, hasta)).save(os.path.join(carpeta, f'shot_{n:02d}.jpg'), quality=72)
        with open(os.path.join(carpeta, 'tramos.txt'), 'w', encoding='utf-8') as archivo:
            archivo.write(f"{len(cortes)} tramos de {ALTO_TRAMO}px; alto total {alto}px{'; RECORTADO' if recortada else ''}\n")
        hechas.append((os.path.basename(carpeta), len(cortes), recortada))
    return hechas


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        sys.exit(__doc__)
    from PIL import Image  # solo hace falta al correrlo de verdad
    Image.MAX_IMAGE_PIXELS = None  # las capturas de página completa son enormes y vienen de nuestro propio escaneo
    for nombre, n, recortada in recortar_carpeta(argv[0], Image.open):
        print(nombre, n, 'tramos', '(recortada)' if recortada else '')
    return 0


if __name__ == '__main__':
    sys.exit(main())
