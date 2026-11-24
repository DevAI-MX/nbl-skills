#!/usr/bin/env python3
"""Triple revision de subtitulos (niveles 1 y 3; el 2 es el validador de tu motor de edicion).

Las cuatro fallas que se buscan, todas vistas en produccion: palabras repetidas, cues duplicados, texto que no
aparece cuando se dice y bloques solapados. Ademas: frases que terminan en conector y subtitulos que entran antes
que la voz.

Uso:
  python3 revisar_subtitulos.py --cues subs.srt|cues.json --transcript whisper.json
                                [--bloques graficos.json] [--cta PALABRA] [--video final.mp4 --y 69]

cues.json / graficos.json: [{"text": "...", "start": s, "end": s}]
whisper.json: salida de Whisper con segments[].words[] (word, start, end) o lista [[palabra, ini, fin], ...]
Sale con codigo 1 si encuentra fallas.
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
import unicodedata
from pathlib import Path

import numpy as np

TOLERANCIA_TOQUE = 0.06      # tocarse en el borde no es solaparse con un grafico
TOLERANCIA_SOLAPE = 0.001
VENTANA_REPETICION = 4.0     # solo cuenta como repeticion si ocurre a menos de 4 s
COMUNES_PARA_REPETIR = 2     # hacen falta dos palabras de contenido en comun
ADELANTO_MAX = 0.05          # un subtitulo no entra mas de 50 ms antes que su palabra
BUSQUEDA_PALABRA = 1.0       # radio para encontrar en la transcripcion la primera palabra del cue
PX_TEXTO_MIN = 125           # pixeles claros en la franja (a 540x960) para decir que hay texto
FRANJA = 0.16                # +-16 % del alto alrededor de la posicion del subtitulo
FUNCION = {"en", "la", "el", "los", "las", "un", "una", "de", "del", "al", "a", "que", "y", "o", "con", "por",
           "para", "su", "tu", "mi", "es", "no", "se", "te", "lo", "le", "tienes", "muy", "mas", "ya", "si"}
CONECTORES = {"de", "del", "la", "el", "los", "las", "un", "una", "unos", "unas", "lo", "al", "a", "en", "con",
              "por", "para", "sin", "sobre", "entre", "hacia", "hasta", "desde", "que", "y", "e", "o", "u", "ni",
              "pero", "como", "cuando", "si", "porque", "su", "sus", "mi", "mis", "tu", "tus"}


class ErrorDeEntrada(Exception):
    """Archivo de cues o transcripcion que no se puede interpretar."""


def norm(t):
    t = unicodedata.normalize("NFD", t.lower())
    return "".join(c for c in t if unicodedata.category(c) != "Mn" and c.isalnum())


# ---------------------------------------------------------------- lectura

def leer_cues(ruta):
    texto = Path(ruta).read_text(encoding="utf-8")
    cues = _parse_srt(texto) if str(ruta).lower().endswith(".srt") else json.loads(texto)
    for c in cues:
        if not {"text", "start", "end"} <= set(c):
            raise ErrorDeEntrada(f"{ruta}: cada cue necesita text, start y end")
    return sorted(({"text": c["text"], "start": float(c["start"]), "end": float(c["end"])} for c in cues),
                  key=lambda c: c["start"])


def _segundos_srt(t):
    h, m, resto = t.replace(",", ".").split(":")
    return int(h) * 3600 + int(m) * 60 + float(resto)


def _parse_srt(texto):
    cues = []
    for bloque in re.split(r"\n\s*\n", texto.strip()):
        lineas = [x for x in bloque.splitlines() if x.strip()]
        tiempo = next((i for i, x in enumerate(lineas) if "-->" in x), None)
        if tiempo is None:
            continue
        a, b = (s.strip() for s in lineas[tiempo].split("-->"))
        cues.append({"text": " ".join(lineas[tiempo + 1:]), "start": _segundos_srt(a), "end": _segundos_srt(b)})
    if not cues:
        raise ErrorDeEntrada("el SRT no tiene ningun cue con tiempos")
    return cues


def leer_transcripcion(ruta):
    datos = json.loads(Path(ruta).read_text(encoding="utf-8"))
    if isinstance(datos, dict):
        crudas = [(w["word"], w["start"], w["end"]) for s in datos.get("segments", []) for w in s.get("words", [])]
    else:
        crudas = [(w["word"], w["start"], w["end"]) if isinstance(w, dict) else tuple(w[:3]) for w in datos]
    palabras = [{"t": w.strip(), "n": norm(w), "s": float(a), "e": float(b)} for w, a, b in crudas if norm(w)]
    if not palabras:
        raise ErrorDeEntrada(f"{ruta}: no hay palabras con tiempos")
    return palabras


# ---------------------------------------------------------------- nivel 1: datos

def duplicados(cues):
    return [f"cue duplicado en {b['start']:.2f}s: {b['text']!r}"
            for a, b in zip(cues, cues[1:]) if a["text"].strip() == b["text"].strip()]


def solapes(cues):
    return [f"el cue {a['start']:.2f}-{a['end']:.2f} se solapa con el de {b['start']:.2f}"
            for a, b in zip(cues, cues[1:]) if a["end"] > b["start"] + TOLERANCIA_SOLAPE]


def encima_de_bloques(cues, bloques):
    return [f"el cue {c['text']!r} ({c['start']:.2f}s) coincide con el grafico {b['text']!r}"
            for c in cues for b in bloques
            if c["start"] < b["end"] - TOLERANCIA_TOQUE and c["end"] > b["start"] + TOLERANCIA_TOQUE]


def _contenido(texto):
    return {norm(x) for x in texto.split() if norm(x) and norm(x) not in FUNCION}


def repeticiones(cues, bloques):
    fallas = []
    for b in bloques:
        for c in cues:
            if c["end"] < b["start"] - VENTANA_REPETICION or c["start"] > b["end"] + VENTANA_REPETICION:
                continue
            comunes = _contenido(b["text"]) & _contenido(c["text"])
            if len(comunes) >= COMUNES_PARA_REPETIR:
                fallas.append(f"el grafico {b['text']!r} repite {sorted(comunes)} en el cue {c['text']!r}")
    return fallas


def ausentes(cues, bloques, palabras, desde=None):
    """Palabras dichas que no salen en pantalla. Lo dicho despues del CTA (`desde`) no se escribe a proposito:
    los subtitulos terminan en la palabra clave y el resto solo se oye."""
    visto = {norm(x) for c in cues + bloques for x in c["text"].split()}
    return [f"no aparece {p['t']!r} (se dice en {p['s']:.2f}s)" for p in palabras
            if p["n"] not in visto and (desde is None or p["s"] <= desde)]


def segundo_del_cta(palabras, palabra_clave):
    """Fin de la ultima vez que se dice la palabra del CTA."""
    clave = norm(palabra_clave)
    veces = [p["e"] for p in palabras if p["n"] == clave]
    if not veces:
        raise ErrorDeEntrada(f"la palabra del CTA {palabra_clave!r} no esta en la transcripcion")
    return veces[-1]


def terminan_en_conector(cues):
    fallas = []
    for c in cues:
        ultima = norm(c["text"].split()[-1]) if c["text"].split() else ""
        if ultima in CONECTORES:
            fallas.append(f"el cue {c['text']!r} ({c['start']:.2f}s) termina en el conector {ultima!r}")
    return fallas


def entran_antes_de_la_voz(cues, palabras):
    fallas = []
    for c in cues:
        primera = norm(c["text"].split()[0]) if c["text"].split() else ""
        cerca = [p for p in palabras if p["n"] == primera and abs(p["s"] - c["start"]) <= BUSQUEDA_PALABRA]
        if not cerca:
            continue
        voz = min(cerca, key=lambda p: abs(p["s"] - c["start"]))["s"]
        if c["start"] < voz - ADELANTO_MAX:
            fallas.append(f"el cue {c['text']!r} entra {voz - c['start']:.2f}s antes de la voz ({c['start']:.2f}s)")
    return fallas


def nivel_datos(cues, bloques, palabras, desde_cta=None):
    return (duplicados(cues) + solapes(cues) + encima_de_bloques(cues, bloques) + repeticiones(cues, bloques)
            + ausentes(cues, bloques, palabras, desde_cta) + terminan_en_conector(cues)
            + entran_antes_de_la_voz(cues, palabras))


# ---------------------------------------------------------------- nivel 3: render

def pixeles_de_texto(cuadro, y_pct):
    """Pixeles claros (blanco o acento calido) en la franja del subtitulo de un cuadro RGB."""
    alto, ancho, _ = cuadro.shape
    lo, hi = max(0.0, y_pct / 100 - FRANJA), min(1.0, y_pct / 100 + FRANJA)
    franja = cuadro[int(alto * lo):int(alto * hi), int(ancho * 0.04):int(ancho * 0.96)].astype(int)
    r, g, b = franja[..., 0], franja[..., 1], franja[..., 2]
    blanco = (r > 205) & (g > 195) & (b > 180)
    acento = (r > 170) & (g > 120) & (b < 140) & ((r - b) > 70)
    return int((blanco | acento).sum())


def cuadro_en(video, segundo, ancho=540, alto=960):
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        raise ErrorDeEntrada("el nivel 3 necesita ffmpeg en el PATH")
    proc = subprocess.run([ffmpeg, "-nostdin", "-v", "error", "-ss", f"{segundo:.3f}", "-i", str(video),
                           "-frames:v", "1", "-vf", f"scale={ancho}:{alto}",
                           "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                          capture_output=True)
    if proc.returncode != 0 or len(proc.stdout) != ancho * alto * 3:
        raise ErrorDeEntrada(f"no se pudo sacar el cuadro {segundo:.2f}s de {video}")
    return np.frombuffer(proc.stdout, np.uint8).reshape(alto, ancho, 3)


def nivel_render(cues, video, y_pct, maximo=24):
    fallas = []
    for c in cues[:maximo]:
        t = (c["start"] + c["end"]) / 2
        px = pixeles_de_texto(cuadro_en(video, t), y_pct)
        if px < PX_TEXTO_MIN:
            fallas.append(f"en {t:.2f}s deberia verse {c['text']!r} y no se ve ({px} px claros)")
    return fallas


# ---------------------------------------------------------------- CLI

def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--cues", required=True)
    p.add_argument("--transcript", required=True)
    p.add_argument("--bloques")
    p.add_argument("--cta", help="palabra clave del CTA: lo que se dice despues no tiene que salir escrito")
    p.add_argument("--video")
    p.add_argument("--y", type=float, default=69.0, help="posicion vertical del subtitulo en %% del alto")
    a = p.parse_args(argv)
    cues, palabras = leer_cues(a.cues), leer_transcripcion(a.transcript)
    bloques = leer_cues(a.bloques) if a.bloques else []
    desde_cta = segundo_del_cta(palabras, a.cta) if a.cta else None
    fallas = nivel_datos(cues, bloques, palabras, desde_cta)
    print(f"NIVEL 1 - DATOS: {len(fallas)} fallas en {len(cues)} cues y {len(palabras)} palabras")
    print("NIVEL 2 - COMPOSICION: corre el validador de tu motor (o revisa la linea de tiempo) y anota el resultado")
    if a.video:
        render = nivel_render(cues, a.video, a.y)
        print(f"NIVEL 3 - RENDER: {len(render)} cuadros sin el texto esperado")
        fallas += render
    else:
        print("NIVEL 3 - RENDER: pendiente (pasa --video cuando haya render)")
    for f in fallas:
        print(f"  - {f}")
    print("REVISION FALLIDA" if fallas else "REVISION OK")
    return 1 if fallas else 0


if __name__ == "__main__":
    sys.exit(main())
