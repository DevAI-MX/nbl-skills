#!/usr/bin/env python3
"""La mezcla medida: cada efecto contra la musica en su instante y la musica contra la voz.

Quien edita con IA no escucha: lo unico confiable es medir y pedirle a la persona un minuto de escucha.

Uso:
  python3 escuchar.py --musica musica.wav [--efectos sfx.wav] [--sutil] [--voz voz.wav --objetivo 18]
                      [--video final.mp4 --salida revision/]

--efectos: cada efecto tiene que quedar entre -10 y +3 dB de la musica (con --sutil, entre -12 y -3).
--voz y --objetivo: diferencia entre la voz (medida donde habla) y la musica; pasa a +-1 dB del objetivo.
--video: deja revision/mudo.mp4 para ver el ritmo sin sonido.
--compas compas.json ({"bpm", "tiempos": [s...], "downbeats": [s...]}): deja revision/compas.wav, la musica con un clic
en cada tiempo (mas fuerte en el uno); si el clic camina contra la bateria, la rejilla esta mal.
Con --compas o --video tambien deja las capas solo-musica.wav y solo-efectos.wav.
Sale con codigo 1 si algo no pasa.
"""
import argparse
import json
import shutil
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import audio_io  # noqa: E402

SR = 48000
RANGO_NORMAL = (-10.0, 3.0)
RANGO_SUTIL = (-12.0, -3.0)
TOLERANCIA_OBJETIVO = 1.0     # dB alrededor del nivel de musica del formato
VENTANA_GOLPE = 0.05          # el efecto se mide en su punto mas fuerte de 50 ms...
BUSQUEDA_GOLPE = 0.6          # ...buscado hasta 0.6 s despues del arranque (un barrido sube despacio)
SEPARACION_GOLPES = 0.12
HUECO_SIN_EFECTOS = 6.0
PICO_RECORTE = -0.3
VOZ_ACTIVA_DBFS = -45.0       # bloques de 50 ms por encima de esto cuentan como voz
CLIC_UNO_HZ, CLIC_UNO_GAN = 2000, 0.55
CLIC_HZ, CLIC_GAN = 1300, 0.3
CLIC_DURACION = 0.035
MUSICA_BAJO_CLIC = 0.8


class ErrorDeMezcla(Exception):
    """Faltan capas o no se pueden comparar."""


def leer_audio(ruta):
    return np.asarray(audio_io.leer_audio(ruta, SR), dtype=np.float64)


def rms_db(x):
    return float(20 * np.log10(np.sqrt(np.mean(np.square(x))) + 1e-12)) if len(x) else audio_io.PISO_DB


def envolvente_lineal(x, paso=0.01):
    v = int(paso * SR)
    return np.sqrt(np.convolve(x ** 2, np.ones(v) / v, mode="same"))[::v]


def golpes(efectos):
    """Segundos donde arranca cada efecto: subidas fuertes de la envolvente separadas al menos 0.12 s."""
    env = envolvente_lineal(efectos)
    umbral = max(env.max() * 0.03, 10 ** (-50 / 20))
    salida, ultimo = [], -1.0
    for i in range(1, len(env)):
        t = i * 0.01
        previo = max(env[max(0, i - 8):i].mean(), 1e-9)
        if env[i] > umbral and env[i] > 2.5 * previo and t - ultimo > SEPARACION_GOLPES:
            salida.append(round(t, 2))
            ultimo = t
    return salida


def _rms(x, i):
    return rms_db(x[max(0, i):max(0, i) + int(VENTANA_GOLPE * SR)])


def efecto_contra_musica(efectos, musica, t):
    """Diferencia en dB entre el efecto en su punto mas fuerte y la musica en ese mismo instante."""
    candidatos = [int((t + k * 0.025) * SR) for k in range(int(BUSQUEDA_GOLPE / 0.025))]
    pico = max(candidatos, key=lambda i: _rms(efectos, i))
    return round(_rms(efectos, pico) - _rms(musica, pico), 1)


def veredicto(diferencia, sutil=False):
    lo, hi = RANGO_SUTIL if sutil else RANGO_NORMAL
    if diferencia < lo:
        return "enterrado: no se va a oir"
    if diferencia > hi:
        return "tapa la musica: bajar"
    return "bien"


def huecos_sin_efectos(tiempos):
    return [(a, b) for a, b in zip(tiempos, tiempos[1:]) if b - a > HUECO_SIN_EFECTOS]


def rms_de_voz(voz):
    """RMS de los tramos donde habla (bloques de 50 ms sobre -45 dBFS): los silencios no bajan la medida."""
    n = SR // 20
    bloques = voz[: len(voz) // n * n].reshape(-1, n)
    nivel = 20 * np.log10(np.sqrt((bloques ** 2).mean(axis=1)) + 1e-12)
    activos = bloques[nivel > VOZ_ACTIVA_DBFS]
    if activos.size == 0:
        raise ErrorDeMezcla("la voz no tiene ningun tramo por encima de -45 dBFS")
    return rms_db(activos.ravel())


def musica_bajo_voz(voz, musica):
    """Cuantos dB queda la musica por debajo de la voz (positivo = la musica esta debajo)."""
    return round(rms_de_voz(voz) - rms_db(musica), 1)


def reporte_efectos(efectos, musica, sutil):
    lineas, fallas = ["| Segundo | Efecto vs musica | Veredicto |", "|---|---|---|"], 0
    tiempos = golpes(efectos)
    for t in tiempos:
        d = efecto_contra_musica(efectos, musica, t)
        v = veredicto(d, sutil)
        fallas += v != "bien"
        lineas.append(f"| {t:.2f} | {d:+.1f} dB | {v} |")
    pico = 20 * np.log10(np.abs(efectos).max() + 1e-12)
    if pico > PICO_RECORTE:
        fallas += 1
        lineas.append(f"- La capa de efectos recorta: pico {pico:.1f} dBFS")
    lineas += [f"- Tramo de mas de 6 s sin efecto: {a:.1f}-{b:.1f} s" for a, b in huecos_sin_efectos(tiempos)]
    return lineas, fallas


def escribir_wav(ruta, x):
    with wave.open(str(ruta), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype("<i2").tobytes())


def clic(frecuencia, ganancia):
    t = np.arange(int(CLIC_DURACION * SR)) / SR
    return np.sin(2 * np.pi * frecuencia * t) * np.exp(-t / (CLIC_DURACION / 4)) * ganancia


def pista_de_compas(musica, compas):
    """La musica con un clic en cada tiempo del compas, mas agudo y fuerte en el uno."""
    pista = musica.copy() * MUSICA_BAJO_CLIC
    unos = {round(float(t), 3) for t in compas.get("downbeats", [])}
    for t in compas.get("tiempos", []):
        es_uno = round(float(t), 3) in unos
        k = clic(CLIC_UNO_HZ, CLIC_UNO_GAN) if es_uno else clic(CLIC_HZ, CLIC_GAN)
        i = int(float(t) * SR)
        if 0 <= i < len(pista) - len(k):
            pista[i:i + len(k)] += k
    return pista


def dejar_capas(carpeta, musica, efectos):
    Path(carpeta).mkdir(parents=True, exist_ok=True)
    escribir_wav(Path(carpeta) / "solo-musica.wav", musica)
    if efectos is not None:
        escribir_wav(Path(carpeta) / "solo-efectos.wav", efectos)


def dejar_mudo(video, carpeta):
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        raise ErrorDeMezcla("hace falta ffmpeg para dejar el mudo")
    Path(carpeta).mkdir(parents=True, exist_ok=True)
    destino = Path(carpeta) / "mudo.mp4"
    subprocess.run([ffmpeg, "-nostdin", "-v", "error", "-y", "-i", str(video), "-an", "-c:v", "copy", str(destino)],
                   check=True)
    return destino


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--musica", required=True)
    p.add_argument("--efectos")
    p.add_argument("--sutil", action="store_true")
    p.add_argument("--voz")
    p.add_argument("--objetivo", type=float, help="dB que la musica debe quedar bajo la voz en este formato")
    p.add_argument("--video")
    p.add_argument("--compas")
    p.add_argument("--salida", default="revision")
    a = p.parse_args(argv)
    musica, fallas, lineas = leer_audio(a.musica), 0, ["# Revision de sonido", ""]
    if a.voz:
        diferencia = musica_bajo_voz(leer_audio(a.voz), musica)
        linea = f"- Musica {diferencia:.1f} dB bajo la voz"
        if a.objetivo is not None:
            pasa = abs(diferencia - a.objetivo) <= TOLERANCIA_OBJETIVO
            fallas += not pasa
            linea += f" (objetivo {a.objetivo:.0f} dB: {'pasa' if pasa else 'no pasa'})"
        lineas.append(linea)
    efectos = leer_audio(a.efectos) if a.efectos else None
    if efectos is not None:
        tabla, malos = reporte_efectos(efectos, musica, a.sutil)
        lineas += [""] + tabla
        fallas += malos
    if a.compas or a.video:
        dejar_capas(a.salida, musica, efectos)
        lineas.append(f"- Capas por separado en {a.salida}/ (solo-musica.wav, solo-efectos.wav)")
    if a.compas:
        compas = json.loads(Path(a.compas).read_text(encoding="utf-8"))
        escribir_wav(Path(a.salida) / "compas.wav", pista_de_compas(musica, compas))
        bpm = compas.get("bpm", "?")
        lineas.append(f"- compas.wav: clic en cada tiempo ({bpm} BPM); 10 s bastan para oir si camina")
    if a.video:
        lineas.append(f"- Mudo para revisar el ritmo sin sonido: {dejar_mudo(a.video, a.salida)}")
    lineas += ["", "Pidele a la persona un minuto de escucha: el mudo completo, el video con sonido una vez y el",
               "final (la musica cierra o se corta). Nada de oido se marca como revisado sin su confirmacion."]
    print("\n".join(lineas))
    return 1 if fallas else 0


if __name__ == "__main__":
    sys.exit(main())
