#!/usr/bin/env python3
"""Recorta una imagen a 4:5 y la deja en 2160x2700 (por ejemplo, una portada que viene de un generador).

Uso:
  python3 recortar_45.py <entrada> <salida.png> [--centro-x 0.5] [--centro-y 0.5]

Respeta la rotación que guarda la foto (EXIF) antes de recortar. Necesita Pillow (pip install pillow).
Las fotos HEIC del iPhone conviértelas antes a JPG o PNG (ver references/verificacion.md).
"""
import argparse
import sys

ANCHO, ALTO = 2160, 2700
PROPORCION = 4 / 5


def caja_45(ancho, alto, centro_x=0.5, centro_y=0.5):
    """La caja (izq, arriba, der, abajo) 4:5 más grande que cabe, centrada en (centro_x, centro_y) de 0 a 1."""
    if not (0 <= centro_x <= 1 and 0 <= centro_y <= 1):
        raise ValueError("el centro va de 0 a 1")
    if ancho / alto > PROPORCION:
        nuevo = round(alto * PROPORCION)
        izq = round((ancho - nuevo) * centro_x)
        return izq, 0, izq + nuevo, alto
    nuevo = round(ancho / PROPORCION)
    arriba = round((alto - nuevo) * centro_y)
    return 0, arriba, ancho, arriba + nuevo


def recortar(entrada, salida, centro_x, centro_y):
    from PIL import Image, ImageOps
    with Image.open(entrada) as original:
        imagen = ImageOps.exif_transpose(original)
        recorte = imagen.crop(caja_45(*imagen.size, centro_x, centro_y))
        recorte.resize((ANCHO, ALTO), Image.LANCZOS).save(salida)


def main(argv=None):
    p = argparse.ArgumentParser(description="Recorta una imagen a 4:5 en 2160x2700.")
    p.add_argument("entrada")
    p.add_argument("salida")
    p.add_argument("--centro-x", type=float, default=0.5, help="0 = izquierda, 1 = derecha")
    p.add_argument("--centro-y", type=float, default=0.5, help="0 = arriba, 1 = abajo")
    args = p.parse_args(argv)
    try:
        recortar(args.entrada, args.salida, args.centro_x, args.centro_y)
    except ImportError:
        print("ERROR: falta Pillow (pip install pillow)", file=sys.stderr)
        return 1
    except (OSError, ValueError) as e:
        print(f"ERROR: no pude recortar {args.entrada}: {e}", file=sys.stderr)
        return 1
    print(f"OK: {args.salida} en {ANCHO}x{ALTO}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
