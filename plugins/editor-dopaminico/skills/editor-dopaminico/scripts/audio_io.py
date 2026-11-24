#!/usr/bin/env python3
"""Lectura de audio y envolventes compartidas por los scripts de la skill, en Python puro (sin numpy).

Un WAV PCM de 16 bits se lee sin dependencias; cualquier otro formato (mp4, mp3, m4a) o frecuencia se pasa por
ffmpeg, que tiene que estar en el PATH.
"""
import math
import shutil
import subprocess
import sys
import wave
from array import array

PASO = 0.01            # la envolvente se mide cada 10 ms
PISO_DB = -120.0       # lo que devuelve un tramo en silencio digital total


class ErrorDeAudio(Exception):
    """El audio no se pudo leer o no sirve para medir."""


def leer_audio(ruta, sr=16000):
    """Audio mono como array('d') entre -1 y 1, a `sr` muestras por segundo."""
    if str(ruta).lower().endswith(".wav"):
        try:
            return _leer_wav(ruta, sr)
        except (wave.Error, ErrorDeAudio):
            pass                                   # WAV en float o a otra frecuencia: que lo convierta ffmpeg
    return _leer_con_ffmpeg(ruta, sr)


def _leer_wav(ruta, sr):
    with wave.open(str(ruta)) as w:
        if w.getsampwidth() != 2 or w.getframerate() != sr:
            raise ErrorDeAudio("WAV que no es PCM de 16 bits a la frecuencia pedida")
        canales = w.getnchannels()
        muestras = array("h", w.readframes(w.getnframes()))
    if sys.byteorder == "big":
        muestras.byteswap()
    if canales == 1:
        return array("d", (m / 32768.0 for m in muestras))
    return array("d", (sum(muestras[i:i + canales]) / (32768.0 * canales)
                       for i in range(0, len(muestras) - canales + 1, canales)))


def _leer_con_ffmpeg(ruta, sr):
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        raise ErrorDeAudio(f"hace falta ffmpeg en el PATH para leer {ruta}")
    proc = subprocess.run([ffmpeg, "-nostdin", "-v", "error", "-i", str(ruta), "-ac", "1", "-ar", str(sr),
                           "-f", "f32le", "-"], capture_output=True)
    if proc.returncode != 0:
        raise ErrorDeAudio(f"ffmpeg no pudo leer {ruta}: {proc.stderr.decode(errors='ignore').strip()}")
    flotantes = array("f", proc.stdout[: len(proc.stdout) // 4 * 4])
    if sys.byteorder == "big":
        flotantes.byteswap()
    return array("d", flotantes)


def escribir_wav(ruta, x, sr=16000):
    """WAV mono PCM de 16 bits (para pruebas y para dejar capas de revision)."""
    muestras = array("h", (int(max(-1.0, min(1.0, float(v))) * 32767) for v in x))
    if sys.byteorder == "big":
        muestras.byteswap()
    with wave.open(str(ruta), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(muestras.tobytes())


def a_db(rms):
    return max(20 * math.log10(rms + 1e-12), PISO_DB)


def envolvente_dbfs(x, sr, paso=PASO):
    """Lista con el RMS en dBFS cada `paso` segundos (valor absoluto: 0 dB es el maximo digital)."""
    n = int(round(sr * paso))
    k = len(x) // n
    if k == 0:
        raise ErrorDeAudio("el audio dura menos que una ventana de medicion")
    return [a_db(math.sqrt(sum(v * v for v in x[i * n:(i + 1) * n]) / n)) for i in range(k)]


def percentil(valores, p):
    """Percentil con interpolacion lineal (el mismo criterio que numpy por defecto)."""
    orden = sorted(valores)
    if not orden:
        raise ErrorDeAudio("no hay valores para calcular el percentil")
    pos = (len(orden) - 1) * p / 100.0
    i = int(math.floor(pos))
    j = min(i + 1, len(orden) - 1)
    return orden[i] + (orden[j] - orden[i]) * (pos - i)


def envolvente_relativa(x, sr, paso=PASO):
    """Envolvente en dB relativa al nivel alto de la voz (percentil 99 = 0 dB), como la usa el corte compactado."""
    db = envolvente_dbfs(x, sr, paso)
    alto = percentil(db, 99)
    return [v - alto for v in db]


def rms_db(x):
    """Nivel RMS en dBFS de un tramo."""
    return a_db(math.sqrt(sum(float(v) * float(v) for v in x) / len(x))) if len(x) else PISO_DB
