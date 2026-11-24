#!/usr/bin/env python3
"""Transcribe varios videos en un solo proceso con Whisper local (el modelo se carga una vez, no uno por video).

  python3 transcribir.py <salida.json> <video1> [<video2> ...] [--modelo mlx-community/whisper-large-v3-mlx]

Usa la librería mlx_whisper (Mac con Apple Silicon) con condition_on_previous_text=False para evitar bucles.
Retoma: los videos ya transcritos en <salida.json> se saltan. Un video sin pista de audio queda como "sin voz"
(su guion es el texto en pantalla). Marca "posible_bucle" cuando un mismo segmento se repite seguido: revísalo.
No transcribas en masa mientras la persona edita video o renderiza: compite por el procesador.
"""
import argparse
import json
import os
import sys

MODELO = 'mlx-community/whisper-large-v3-mlx'
REPETICIONES_SOSPECHOSAS = 3


def posible_bucle(segmentos, repeticiones=REPETICIONES_SOSPECHOSAS):
    """True si el mismo texto aparece `repeticiones` veces seguidas: Whisper a veces se queda repitiendo."""
    seguidas, previo = 1, None
    for s in segmentos:
        texto = (s.get('text') or '').strip().lower()
        seguidas = seguidas + 1 if texto and texto == previo else 1
        if seguidas >= repeticiones:
            return True
        previo = texto
    return False


def resultado(texto, segmentos):
    partes = [{'inicio': round(s['start'], 1), 'fin': round(s['end'], 1), 'texto': s['text'].strip()} for s in segmentos]
    return {'texto': texto.strip(), 'segmentos': partes, 'posible_bucle': posible_bucle(segmentos)}


def transcribir_lote(videos, ya_hechos, transcribir):
    """Aplica `transcribir(video) -> {'text', 'segments'}` a cada video que falte. Los que fallan al cargar el audio
    quedan como sin voz; cualquier otro error queda anotado sin detener el lote."""
    salida = dict(ya_hechos)
    for video in videos:
        clave = os.path.basename(video)
        if clave in salida:
            continue
        try:
            r = transcribir(video)
            salida[clave] = resultado(r.get('text', ''), r.get('segments', []))
        except Exception as e:  # el transcriptor es de terceros: cualquier fallo se registra por video
            salida[clave] = {'sin_voz': True} if 'Failed to load audio' in str(e) else {'error': str(e)[:300]}
        yield clave, salida


def transcriptor_mlx(modelo):
    import mlx_whisper  # se importa aquí: solo existe en Mac con Apple Silicon
    return lambda video: mlx_whisper.transcribe(video, path_or_hf_repo=modelo, condition_on_previous_text=False)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('salida')
    ap.add_argument('videos', nargs='+')
    ap.add_argument('--modelo', default=MODELO)
    a = ap.parse_args(argv)
    ya = {}
    if os.path.exists(a.salida):
        with open(a.salida, encoding='utf-8') as archivo:
            ya = json.load(archivo)
    for clave, salida in transcribir_lote(a.videos, ya, transcriptor_mlx(a.modelo)):
        with open(a.salida, 'w', encoding='utf-8') as archivo:
            json.dump(salida, archivo, ensure_ascii=False, indent=1)
        print(clave, 'listo')
    return 0


if __name__ == '__main__':
    sys.exit(main())
