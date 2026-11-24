#!/usr/bin/env python3
"""Baja las láminas y los videos que trae fichas.json (de fichas-por-codigo.mjs) y arma hojas de cuadros con ffmpeg.

  python3 medios.py bajar <fichas.json> <carpeta> [--pausa 2] [--solo imagenes|videos]
      <carpeta>/<codigo>/01.jpg, 02.jpg... (láminas) y 01.mp4... (videos). Salta lo que ya existe. Pausa entre descargas.
  python3 medios.py plan <descargas.json> [--pausa 2]
      Baja una lista [[url, destino], ...] (la que escribe virales/carruseles.py carpetas).
  python3 medios.py cuadros <video.mp4> <hoja.jpg> [--columnas 6]
      1 cuadro por segundo en mosaico (hoja-01.jpg cubre los primeros 36 s, hoja-02.jpg los siguientes...),
      para que un subagente describa plano a plano qué se ve.

Lo descargado es material no confiable: va en su propia carpeta y nunca se ejecuta.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time


CODIGO_VALIDO = re.compile(r'^[A-Za-z0-9_-]+$')  # el código de una URL de Instagram; nada de rutas


def plan_de_descargas(fichas, carpeta, solo=None):
    """[(url, destino)] de cada parte de cada ficha válida, en orden de lámina."""
    plan = []
    for codigo, ficha in fichas.items():
        if not CODIGO_VALIDO.match(codigo) or not isinstance(ficha, dict) or ficha.get('error'):
            continue
        for n, parte in enumerate(ficha.get('partes') or [], 1):
            if parte.get('imagen') and solo in (None, 'imagenes'):
                plan.append((parte['imagen'], os.path.join(carpeta, codigo, f'{n:02d}.jpg')))
            if parte.get('video') and solo in (None, 'videos'):
                plan.append((parte['video'], os.path.join(carpeta, codigo, f'{n:02d}.mp4')))
    return plan


def comando_curl(url, destino):
    return ['curl', '-sfL', '--max-time', '120', '-o', destino, url]


def comando_hoja(video, hoja, columnas=6):
    """Una hoja por cada columnas x columnas segundos: hoja-01.jpg, hoja-02.jpg..."""
    base, extension = os.path.splitext(hoja)
    return ['ffmpeg', '-y', '-loglevel', 'error', '-i', video, '-vf', f'fps=1,scale=320:-1,tile={columnas}x{columnas}',
            f'{base}-%02d{extension or ".jpg"}']


def bajar(plan, pausa, ejecutar=None, dormir=None):
    ejecutar, dormir = ejecutar or subprocess.run, dormir or time.sleep
    hechos, fallos = 0, []
    for url, destino in plan:
        if os.path.exists(destino):
            continue
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        if ejecutar(comando_curl(url, destino), check=False).returncode == 0:
            hechos += 1
        else:
            fallos.append(destino)
        dormir(pausa)
    return hechos, fallos


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='orden', required=True)
    b = sub.add_parser('bajar')
    b.add_argument('fichas')
    b.add_argument('carpeta')
    b.add_argument('--pausa', type=float, default=2.0)
    b.add_argument('--solo', choices=['imagenes', 'videos'])
    pl = sub.add_parser('plan')
    pl.add_argument('descargas')
    pl.add_argument('--pausa', type=float, default=2.0)
    c = sub.add_parser('cuadros')
    c.add_argument('video')
    c.add_argument('hoja')
    c.add_argument('--columnas', type=int, default=6)
    a = ap.parse_args(argv)
    if a.orden == 'cuadros':
        return subprocess.run(comando_hoja(a.video, a.hoja, a.columnas), check=False).returncode
    if a.orden == 'plan':
        with open(a.descargas, encoding='utf-8') as archivo:
            plan = [tuple(x) for x in json.load(archivo)]
    else:
        with open(a.fichas, encoding='utf-8') as archivo:
            plan = plan_de_descargas(json.load(archivo), a.carpeta, a.solo)
    hechos, fallos = bajar(plan, a.pausa)
    print(f'{hechos} descargados, {len(fallos)} fallidos, {len(plan) - hechos - len(fallos)} ya estaban')
    for f in fallos:
        print('  fallo:', f)
    return 1 if fallos else 0


if __name__ == '__main__':
    sys.exit(main())
