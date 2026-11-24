#!/usr/bin/env python3
"""QA medible del archivo final: resolucion, codec sin HDR colado, loudness, pico real y pausas.

Uso:
  python3 qa_master.py final.mp4 [--lufs -16] [--pico -1.5] [--pausa-max 0.25] [--resolucion 1080x1920]

Marca personal y cliente organico: --lufs -16. Promos, anuncios y videos con kit de marca: --lufs -14.
Imprime una tabla PASA/FALLA y sale con codigo 1 si algo falla. Necesita ffmpeg y ffprobe en el PATH.
"""
import argparse
import json
import re
import shutil
import subprocess
import sys

TOLERANCIA_LU = 0.5            # margen de medicion alrededor del objetivo de loudness
SILENCIO_DB = -40              # silencedetect: una pausa es audio bajo -40 dB...
TRANSFERENCIAS_HDR = {"arib-std-b67", "smpte2084"}


class ErrorDeQA(Exception):
    """No se pudo medir el archivo."""


def _herramienta(nombre):
    ruta = shutil.which(nombre)
    if ruta is None:
        raise ErrorDeQA(f"hace falta {nombre} en el PATH")
    return ruta


def _correr(cmd):
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise ErrorDeQA(f"fallo {' '.join(cmd[:3])}...: {proc.stderr.strip()[-300:]}")
    return proc


# ---------------------------------------------------------------- interpretar salidas

def leer_loudnorm(stderr):
    """(LUFS integrados, pico real dBTP) del bloque JSON que imprime loudnorm=print_format=json."""
    try:
        datos = json.loads(stderr[stderr.rindex("{"):stderr.rindex("}") + 1])
        return float(datos["input_i"]), float(datos["input_tp"])
    except (ValueError, KeyError) as e:
        raise ErrorDeQA(f"no se encontro la medicion de loudnorm: {e}")


def leer_silencios(stderr):
    """Duraciones de cada silencio que reporta silencedetect."""
    return [float(x) for x in re.findall(r"silence_duration:\s*([\d.]+)", stderr)]


def leer_stream(salida_csv):
    """(ancho, alto, codec, transferencia) de la linea csv de ffprobe."""
    campos = salida_csv.strip().split(",")
    if len(campos) < 3:
        raise ErrorDeQA(f"ffprobe no devolvio el stream de video: {salida_csv!r}")
    codec, ancho, alto = campos[0], int(campos[1]), int(campos[2])
    transferencia = campos[3] if len(campos) > 3 else ""
    return ancho, alto, codec, transferencia


# ---------------------------------------------------------------- mediciones

def medir_video(ruta):
    proc = _correr([_herramienta("ffprobe"), "-v", "error", "-select_streams", "v:0", "-show_entries",
                    "stream=codec_name,width,height,color_transfer", "-of", "csv=p=0", ruta])
    return leer_stream(proc.stdout)


def medir_loudness(ruta):
    proc = _correr([_herramienta("ffmpeg"), "-nostdin", "-hide_banner", "-i", ruta, "-af",
                    "loudnorm=print_format=json", "-f", "null", "-"])
    return leer_loudnorm(proc.stderr)


def medir_pausas(ruta, pausa_max):
    proc = _correr([_herramienta("ffmpeg"), "-nostdin", "-hide_banner", "-i", ruta, "-af",
                    f"silencedetect=noise={SILENCIO_DB}dB:d={pausa_max}", "-f", "null", "-"])
    return leer_silencios(proc.stderr)


# ---------------------------------------------------------------- juicio

def juzgar(video, loudness, silencios, objetivos):
    ancho, alto, codec, transferencia = video
    lufs, pico = loudness
    esperada = objetivos["resolucion"]
    return [
        ("Resolucion", f"{ancho}x{alto}", f"{ancho}x{alto}" == esperada),
        ("Codec sin HDR colado", f"{codec} {transferencia or '-'}",
         codec == "h264" and transferencia not in TRANSFERENCIAS_HDR),
        ("Loudness integrado", f"{lufs:.1f} LUFS (objetivo {objetivos['lufs']})",
         abs(lufs - objetivos["lufs"]) <= TOLERANCIA_LU),
        ("Pico real", f"{pico:.1f} dBTP (maximo {objetivos['pico']})", pico <= objetivos["pico"]),
        ("Pausas", f"{len(silencios)} de mas de {objetivos['pausa_max']} s" +
         (f" (la mayor {max(silencios):.2f} s)" if silencios else ""), not silencios),
    ]


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("video")
    p.add_argument("--lufs", type=float, default=-16.0)
    p.add_argument("--pico", type=float, default=-1.5)
    p.add_argument("--pausa-max", type=float, default=0.25)
    p.add_argument("--resolucion", default="1080x1920")
    a = p.parse_args(argv)
    objetivos = {"lufs": a.lufs, "pico": a.pico, "pausa_max": a.pausa_max, "resolucion": a.resolucion}
    filas = juzgar(medir_video(a.video), medir_loudness(a.video), medir_pausas(a.video, a.pausa_max), objetivos)
    print("| Check | Medido | Resultado |\n|---|---|---|")
    for nombre, medido, pasa in filas:
        print(f"| {nombre} | {medido} | {'PASA' if pasa else 'FALLA'} |")
    return 0 if all(pasa for _, _, pasa in filas) else 1


if __name__ == "__main__":
    sys.exit(main())
