#!/usr/bin/env python3
"""Paleta de una cuenta sacada por programa de sus imágenes de DISEÑO de marca (portadas de carruseles, portadas de reels
con texto, destacadas diseñadas, foto de perfil). Elige tú las imágenes: las fotos sin diseño ensucian la paleta.

  python3 paleta.py <handle> <imagen1> [<imagen2> ...]      imprime un JSON

Dominantes: k-means k=6 sobre los píxeles de todas las imágenes. Acentos: píxeles saturados que no son tono de piel,
k=4 (k=2 si son pocos). Los dominantes con tono de piel se listan aparte: son la cara del creador, no color de marca.
Necesita numpy y Pillow.
"""
import colorsys
import json
import sys

import numpy as np

SEMILLA = 7
K_DOMINANTES, K_FINO = 6, 12
LADO_MINIATURA = (160, 200)
PIXELES_POR_IMAGEN = 2500
SATURACION_ACENTO, BRILLO_ACENTO = 0.55, 0.35
MINIMO_PIXELES_ACENTO, MUCHOS_PIXELES_ACENTO = 60, 400
PARTE_MINIMA_ACENTO = 0.004


def kmeans(pixeles, k, vueltas=25, semilla=SEMILLA):
    """k-means con arranque k-means++. Devuelve centros y su proporción, de mayor a menor. Si hay menos colores
    distintos que k, devuelve menos centros (no inventa)."""
    azar = np.random.default_rng(semilla)
    centros = [pixeles[azar.integers(len(pixeles))]]
    for _ in range(1, k):
        distancia = np.min(((pixeles[:, None, :] - np.array(centros)[None]) ** 2).sum(-1), axis=1)
        if distancia.sum() == 0:
            break
        centros.append(pixeles[azar.choice(len(pixeles), p=distancia / distancia.sum())])
    centros = np.array(centros, dtype=float)
    for _ in range(vueltas):
        etiqueta = np.argmin(((pixeles[:, None, :] - centros[None]) ** 2).sum(-1), axis=1)
        nuevos = np.array([pixeles[etiqueta == j].mean(0) if (etiqueta == j).any() else centros[j] for j in range(len(centros))])
        if np.allclose(nuevos, centros, atol=0.5):
            break
        centros = nuevos
    etiqueta = np.argmin(((pixeles[:, None, :] - centros[None]) ** 2).sum(-1), axis=1)
    parte = np.bincount(etiqueta, minlength=len(centros)) / len(pixeles)
    orden = np.argsort(-parte)
    return centros[orden], parte[orden]


def hx(color):
    return '#%02X%02X%02X' % tuple(int(round(v)) for v in color)


def hsv(color):
    return colorsys.rgb_to_hsv(*(np.array(color, dtype=float) / 255))


def es_piel(color):
    tono, saturacion, brillo = hsv(color)
    return 5 <= tono * 360 <= 45 and 0.15 < saturacion < 0.62 and brillo > 0.3


def mascara_de_acentos(pixeles):
    normal = pixeles / 255.0
    maximo, minimo = normal.max(1), normal.min(1)
    saturacion = np.where(maximo > 0, (maximo - minimo) / np.maximum(maximo, 1e-6), 0)
    piel = np.array([es_piel(p) for p in pixeles])
    return (saturacion >= SATURACION_ACENTO) & (maximo >= BRILLO_ACENTO) & ~piel


def acentos(pixeles, mascara):
    if mascara.sum() < MINIMO_PIXELES_ACENTO:
        return []
    k = 4 if mascara.sum() > MUCHOS_PIXELES_ACENTO else 2
    centros, partes = kmeans(pixeles[mascara], k)
    fraccion = mascara.sum() / len(pixeles)
    return [(hx(c), round(float(p * fraccion) * 100, 1)) for c, p in zip(centros, partes) if p * fraccion >= PARTE_MINIMA_ACENTO]


def resumir(handle, pixeles, n_imagenes):
    dominantes, partes = kmeans(pixeles, K_DOMINANTES)
    finos, partes_finas = kmeans(pixeles, K_FINO)
    saturados = [(hx(c), round(float(p) * 100, 1)) for c, p in zip(finos, partes_finas)
                 if hsv(c)[1] >= 0.40 and hsv(c)[2] >= 0.30 and p >= 0.012]
    mascara = mascara_de_acentos(pixeles)
    return {'handle': handle, 'n_imgs': n_imagenes,
            'dominantes': [(hx(c), round(float(p) * 100, 1)) for c, p in zip(dominantes, partes)],
            'saturados_k12': saturados, 'acentos': acentos(pixeles, mascara),
            'pixeles_saturados_pct': round(float(mascara.mean()) * 100, 1),
            'piel': [hx(c) for c in dominantes if es_piel(c)]}


def pixeles_de(ruta, azar):
    from PIL import Image  # solo hace falta al leer imágenes
    imagen = Image.open(ruta).convert('RGB')
    imagen.thumbnail(LADO_MINIATURA)
    datos = np.asarray(imagen).reshape(-1, 3).astype(float)
    return datos[azar.choice(len(datos), PIXELES_POR_IMAGEN, replace=False)] if len(datos) > PIXELES_POR_IMAGEN else datos


def a_lab(color_hex):
    rgb = np.array([int(color_hex.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4)]) / 255
    lineal = np.where(rgb > 0.04045, ((rgb + 0.055) / 1.055) ** 2.4, rgb / 12.92)
    xyz = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]]) @ lineal
    xyz = xyz / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.array([116 * f[1] - 16, 500 * (f[0] - f[1]), 200 * (f[1] - f[2])])


def delta_e76(color_a, color_b):
    """Distancia en Lab: menos de 5 es prácticamente el mismo color; menos de 15, la misma familia a simple vista."""
    return round(float(np.linalg.norm(a_lab(color_a) - a_lab(color_b))), 1)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) < 2:
        sys.exit(__doc__)
    azar = np.random.default_rng(SEMILLA)
    pixeles = np.vstack([pixeles_de(ruta, azar) for ruta in argv[1:]])
    print(json.dumps(resumir(argv[0], pixeles, len(argv) - 1), ensure_ascii=False))
    return 0


if __name__ == '__main__':
    sys.exit(main())
