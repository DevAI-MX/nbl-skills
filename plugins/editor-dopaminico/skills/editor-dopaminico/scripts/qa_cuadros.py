#!/usr/bin/env python3
"""QA automatica de los cuadros de un video terminado: negro, pops, tramos muertos y tiempo de lectura.

Uso:
  python3 qa_cuadros.py final.mp4 [--bloques graficos.json] [--cierre 1.0] [--hojas carpeta_qa]

- Negro: tramos de al menos 0.1 s en negro (blackdetect pix_th=0.06). --cierre ignora el negro de los ultimos N s
  cuando el formato cierra a negro (historias, tarjeta).
- Pops: un cuadro que cambia 3 veces mas que sus vecinos (y mas de 2 niveles de gris). Los cortes a proposito tambien
  salen: se confirma cada uno mirando, no hacen fallar.
- Tramos muertos: mas de 1 s sin que se mueva nada (cambio medio < 0.12 niveles de gris por cuadro).
- Lectura (con --bloques): cada bloque de texto de un grafico o titulo visible al menos letras/15 + 1.5 s si es frase,
  o + 0.6 s si son 1-2 palabras. No se aplica al subtitulo palabra a palabra.
- --hojas: deja hoja.jpg (2 cuadros por segundo) y celular.jpg (1 por segundo a 360 px: se lee en un telefono?).
Sale con codigo 1 si hay negro, tramos muertos o textos que no se alcanzan a leer. Necesita ffmpeg, ffprobe y numpy.
"""
import argparse
import json
import math
import re
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np

ANCHO, ALTO = 90, 160              # los cuadros se comparan reducidos y en gris
POP_VECES = 3.0
POP_MINIMO = 2.0
POP_PISO_VECINOS = 0.3
QUIETO = 0.12
MUERTO_MIN = 1.0
NEGRO_DURACION = 0.1
NEGRO_UMBRAL_PIXEL = 0.06
LETRAS_POR_SEGUNDO = 15.0
FIJARSE_FRASE, FIJARSE_PALABRAS = 1.5, 0.6
TOLERANCIA_LECTURA = 0.05


class ErrorDeQA(Exception):
    """No se pudo leer el video."""


def _herramienta(nombre):
    ruta = shutil.which(nombre)
    if ruta is None:
        raise ErrorDeQA(f"hace falta {nombre} en el PATH")
    return ruta


# ---------------------------------------------------------------- analisis puro

def diferencias(cuadros):
    """d[i] = cambio medio entre el cuadro i y el i+1."""
    return np.abs(np.diff(np.asarray(cuadros, dtype=np.float32), axis=0)).mean(axis=(1, 2))


def pops(d, fps):
    salida = []
    for i in range(1, len(d) - 1):
        vecinos = max(d[i - 1], d[i + 1], POP_PISO_VECINOS)
        if d[i] > POP_VECES * vecinos and d[i] > POP_MINIMO:
            salida.append((round((i + 1) / fps, 2), round(float(d[i]), 1)))
    return salida


def tramos_muertos(d, fps):
    salida, inicio = [], None
    for i, quieto in enumerate(list(d < QUIETO) + [False]):
        if quieto and inicio is None:
            inicio = i
        elif not quieto and inicio is not None:
            if (i - inicio) / fps > MUERTO_MIN:
                salida.append((round(inicio / fps, 2), round(i / fps, 2)))
            inicio = None
    return salida


def lectura(bloques):
    """Bloques de texto que no estan en pantalla el tiempo minimo para leerlos."""
    cortos = []
    for b in bloques:
        letras, palabras = len(re.sub(r"\s", "", b["text"])), len(b["text"].split())
        minimo = round(letras / LETRAS_POR_SEGUNDO + (FIJARSE_PALABRAS if palabras <= 2 else FIJARSE_FRASE), 2)
        visto = round(float(b["end"]) - float(b["start"]), 2)
        if visto + TOLERANCIA_LECTURA < minimo:
            cortos.append({"texto": b["text"][:60], "inicio": float(b["start"]), "visto": visto, "minimo": minimo})
    return cortos


def leer_negro(stderr):
    return [(float(a), float(b)) for a, b in re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", stderr)]


def negro_fuera_del_cierre(tramos, duracion, cierre):
    return [(a, b) for a, b in tramos if a < duracion - cierre]


# ---------------------------------------------------------------- lectura del video

def meta(video):
    salida = subprocess.run([_herramienta("ffprobe"), "-v", "error", "-select_streams", "v:0", "-show_entries",
                             "stream=r_frame_rate:format=duration", "-of", "json", video],
                            capture_output=True, text=True)
    if salida.returncode != 0:
        raise ErrorDeQA(f"ffprobe no pudo leer {video}: {salida.stderr.strip()[-200:]}")
    datos = json.loads(salida.stdout)
    num, den = datos["streams"][0]["r_frame_rate"].split("/")
    return float(num) / float(den), float(datos["format"]["duration"])


def leer_cuadros(video):
    proc = subprocess.run([_herramienta("ffmpeg"), "-nostdin", "-v", "error", "-i", video, "-vf",
                           f"scale={ANCHO}:{ALTO},format=gray", "-f", "rawvideo", "-"], capture_output=True)
    if proc.returncode != 0 or not proc.stdout:
        raise ErrorDeQA(f"ffmpeg no pudo sacar los cuadros de {video}")
    return np.frombuffer(proc.stdout, np.uint8).reshape(-1, ALTO, ANCHO)


def detectar_negro(video):
    proc = subprocess.run([_herramienta("ffmpeg"), "-nostdin", "-hide_banner", "-nostats", "-i", video, "-vf",
                           f"blackdetect=d={NEGRO_DURACION}:pix_th={NEGRO_UMBRAL_PIXEL}", "-an", "-f", "null", "-"],
                          capture_output=True, text=True)
    return leer_negro(proc.stderr)


def hojas(video, duracion, carpeta):
    Path(carpeta).mkdir(parents=True, exist_ok=True)
    ffmpeg = _herramienta("ffmpeg")
    for nombre, filtro in (("hoja.jpg", f"fps=2,scale=240:-1,tile=6x{math.ceil(duracion * 2 / 6)}:padding=4"),
                           ("celular.jpg", f"fps=1,scale=360:-1,tile=5x{math.ceil(duracion / 5)}:padding=4")):
        subprocess.run([ffmpeg, "-nostdin", "-v", "error", "-y", "-i", video, "-vf", filtro, "-frames:v", "1",
                        str(Path(carpeta) / nombre)], check=True)


def revisar(video, bloques, cierre):
    fps, duracion = meta(video)
    d = diferencias(leer_cuadros(video))
    return {"fps": fps, "duracion": duracion, "pops": pops(d, fps), "muertos": tramos_muertos(d, fps),
            "negro": negro_fuera_del_cierre(detectar_negro(video), duracion, cierre), "lectura": lectura(bloques)}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("video")
    p.add_argument("--bloques", help="JSON [{text, start, end}] con los textos de graficos y titulos")
    p.add_argument("--cierre", type=float, default=0.0, help="segundos finales con cierre a negro a proposito")
    p.add_argument("--hojas", help="carpeta donde dejar hoja.jpg y celular.jpg")
    a = p.parse_args(argv)
    bloques = json.loads(Path(a.bloques).read_text(encoding="utf-8")) if a.bloques else []
    r = revisar(a.video, bloques, a.cierre)
    if a.hojas:
        hojas(a.video, r["duracion"], a.hojas)
    print(f"Negro ({len(r['negro'])}): {r['negro'] or 'ninguno'}")
    print(f"Tramos muertos de mas de 1 s ({len(r['muertos'])}): {r['muertos'] or 'ninguno'}")
    print(f"Lectura ({len(bloques)} bloques): {r['lectura'] or 'todos con tiempo suficiente'}")
    print(f"Pops a confirmar mirando ({len(r['pops'])}): {r['pops'] or 'ninguno'}"
          " (los cortes a proposito tambien salen)")
    falla = r["negro"] or r["muertos"] or r["lectura"]
    print("QA DE CUADROS: FALLA" if falla else "QA DE CUADROS: PASA")
    return 1 if falla else 0


if __name__ == "__main__":
    sys.exit(main())
