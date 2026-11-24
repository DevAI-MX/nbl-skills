#!/usr/bin/env python3
"""Look de television vieja para historias narradas (la receta aprobada, sin parpadeo y sin oscurecer de mas).

Uso:
  python3 tv_vieja.py entrada.mp4 salida.mp4 [--ancho 1080 --alto 1920]

Genera la textura de lineas de barrido (cada 4 px: 2 filas blancas y 2 a 196/255) y aplica la cadena de ffmpeg:
desaturado y calido, desenfoque leve, bordes de color corridos +-3 px, grano temporal, multiplicar por las lineas,
curvatura suave de pantalla y vineta suave. El audio se copia tal cual. Necesita ffmpeg en el PATH.
"""
import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

PERIODO_LINEAS = 4
FILAS_OSCURAS = 2
GRIS_LINEA = 196
CADENA = ("[0:v]fps=30,eq=saturation=0.8:contrast=1.04:brightness=0.045,"
          "colorbalance=rs=0.03:bs=-0.04:rh=0.02,gblur=sigma=0.7,rgbashift=rh=-3:bh=3,noise=alls=16:allf=t+u[v];"
          "[v][1:v]blend=all_mode=multiply:shortest=1[s];"
          "[s]lenscorrection=k1=0.05:k2=0.02,vignette=angle=PI/6,format=yuv420p[out]")


class ErrorDeLook(Exception):
    """No se pudo aplicar el look."""


def textura_lineas(ancho, alto):
    """Matriz gris alto x ancho: en cada bloque de 4 filas, las 2 primeras a 255 y las 2 siguientes a 196."""
    fila = np.full(PERIODO_LINEAS, 255, np.uint8)
    fila[PERIODO_LINEAS - FILAS_OSCURAS:] = GRIS_LINEA
    columna = np.resize(fila, alto)
    return np.repeat(columna[:, None], ancho, axis=1)


def escribir_pgm(ruta, imagen):
    alto, ancho = imagen.shape
    Path(ruta).write_bytes(f"P5\n{ancho} {alto}\n255\n".encode() + imagen.tobytes())


def comando(ffmpeg, entrada, textura, salida):
    return [ffmpeg, "-nostdin", "-v", "error", "-y", "-i", str(entrada), "-loop", "1", "-i", str(textura),
            "-filter_complex", CADENA, "-map", "[out]", "-map", "0:a?", "-c:v", "libx264", "-crf", "18",
            "-preset", "medium", "-c:a", "copy", "-movflags", "+faststart", str(salida)]


def aplicar(entrada, salida, ancho=1080, alto=1920):
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        raise ErrorDeLook("hace falta ffmpeg en el PATH")
    with tempfile.TemporaryDirectory() as tmp:
        textura = Path(tmp) / "lineas.pgm"
        escribir_pgm(textura, textura_lineas(ancho, alto))
        proc = subprocess.run(comando(ffmpeg, entrada, textura, salida), capture_output=True, text=True)
    if proc.returncode != 0:
        raise ErrorDeLook(f"ffmpeg fallo con {entrada}: {proc.stderr.strip()[-300:]}")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("entrada")
    p.add_argument("salida")
    p.add_argument("--ancho", type=int, default=1080)
    p.add_argument("--alto", type=int, default=1920)
    a = p.parse_args(argv)
    aplicar(a.entrada, a.salida, a.ancho, a.alto)
    print(f"listo: {a.salida}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
