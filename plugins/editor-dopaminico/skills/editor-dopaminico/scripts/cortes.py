#!/usr/bin/env python3
"""Cortes en el silencio real de la voz, medidos sobre el audio y nunca con los tiempos de Whisper.

Subcomandos (todos imprimen JSON):
  partir voz.wav                             tomas del crudo por sus silencios reales, para transcribir cada una sola
  elegir voz.wav tomas.json --elegidas '[0, 2, [3, 1, 5]]'
                                             tramos de las tomas elegidas (indice, o [indice, palabra_ini, palabra_fin])
                                             con respiro de 0.07 s antes y 0.11 s despues sin invadir la toma vecina
  compactar voz.wav [--tramos tramos.json]   deja solo la voz: huecos de mas de 0.16 s quedan en ~0.13 s
  bordes voz.wav frases.json                 punto de corte limpio al inicio y al final de cada frase elegida
  uniones corte.wav cortes.json              nivel en cada union del video ya cortado (pasa si llega a <= -40 dB)
  filtro cortes.json                         filter_complex de ffmpeg con los tramos y fundidos de 12 ms

tramos.json y cortes.json: {"tramos": [[ini, fin], ...]} en segundos del original.
tomas.json: [{"ini": s, "fin": s, "palabras": [[palabra, ini, fin], ...]}] (cada toma transcrita por separado).
frases.json: [{"ini": s, "fin": s, "siguiente": s_opcional}] con los tiempos que dio Whisper para cada frase.
"""
import argparse
import json
import sys
from itertools import accumulate
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audio_io import PASO, envolvente_dbfs, envolvente_relativa, leer_audio, percentil  # noqa: E402

SR = 16000
# Corte compactado (vigente desde el 2-nov para todo corte nuevo; defaults reafirmados el 4-nov)
VOZ_DB = -24.0          # relativo al nivel alto de la voz: la voz va de 0 a -20, las respiraciones de -26 a -33
COLA = 0.08             # lo que se deja tras cada tramo de voz (colas de "s")
ARRANQUE = 0.05         # lo que se deja antes del siguiente tramo
HUECO_MAX = 0.16        # todo hueco mas largo se quita y queda COLA + ARRANQUE de pausa
TRAMO_MIN = 0.06        # un tramo de voz mas corto que esto es un chasquido, no voz
# Bordes de frase (corte limpio del 24/25-oct)
SILENCIO_DBFS = -38.0   # silencio real: al menos 80 ms seguidos bajo -38 dBFS (piso de sala tipico ~-50)
SILENCIO_MIN_VENTANAS = 8
# Verificacion de uniones
UNION_MAX_DBFS = -40.0  # cada union del corte tiene que pasar por este nivel o menos
UNION_RADIO = 0.02      # se busca el punto mas bajo a +-20 ms de la union
FUNDIDO = 0.012         # micro fundido de audio en cada tramo contra clics
# Tomas (partir el crudo y elegir las buenas contra el guion)
SOBRE_PISO_DB = 9.0     # es voz lo que queda 9 dB sobre el piso de la sala (percentil 10 de la envolvente)
SILENCIO_ENTRE_TOMAS = 0.35
VOZ_MIN_TOMA = 0.25
RESPIRO_ANTES = 0.07    # silencio real que se conserva antes de una toma completa...
RESPIRO_DESPUES = 0.11  # ...y despues, sin pasar nunca de la mitad del hueco con la toma vecina
MARGEN_PALABRA = 0.03   # al cortar dentro de una toma se busca el punto mas callado entre dos palabras, +-30 ms


class ErrorDeCorte(Exception):
    """Datos de entrada que no permiten calcular el corte."""


# ---------------------------------------------------------------- compactar

def tramos_de_voz(mascara):
    """[(i, j)] de los tramos seguidos en True de una mascara booleana (j exclusivo)."""
    tramos, inicio = [], None
    for k, activo in enumerate(mascara):
        if activo and inicio is None:
            inicio = k
        elif not activo and inicio is not None:
            tramos.append((inicio, k))
            inicio = None
    if inicio is not None:
        tramos.append((inicio, len(mascara)))
    return tramos


def _por_encima(valores, umbral):
    return [v > umbral for v in valores]


def compactar(segmentos, db_rel, paso=PASO, cola=COLA, arranque=ARRANQUE, hueco_max=HUECO_MAX, voz_db=VOZ_DB):
    """Dentro de cada segmento se queda solo lo que suena a voz, para que suene dicho de corrido."""
    salida = []
    for ini, fin in segmentos:
        voz = _por_encima(db_rel[int(round(ini / paso)):int(round(fin / paso))], voz_db)
        for a, b in _unir_huecos_cortos(tramos_de_voz(voz), ini, paso, hueco_max):
            if b - a > TRAMO_MIN:
                salida.append((round(max(ini, a - arranque), 3), round(min(fin, b + cola), 3)))
    return salida


def _unir_huecos_cortos(tramos, ini, paso, hueco_max):
    unidos = []
    for i, j in tramos:
        a, b = ini + i * paso, ini + j * paso
        if unidos and a - unidos[-1][1] <= hueco_max:     # huecos entre silabas no se tocan
            unidos[-1][1] = b
        else:
            unidos.append([a, b])
    return unidos


def pausas(tramos, db_rel, paso=PASO, voz_db=VOZ_DB):
    """Pausas del video cortado: cola sin voz de un tramo mas arranque sin voz del siguiente."""
    bordes_mudos = [_bordes_sin_voz(_por_encima(db_rel[int(round(a / paso)):int(round(b / paso))], voz_db), paso)
                    for a, b in tramos]
    return [round(cola + arranque, 3) for (_, cola), (arranque, _) in zip(bordes_mudos, bordes_mudos[1:])]


def _bordes_sin_voz(voz, paso):
    """(segundos sin voz al inicio, segundos sin voz al final) de un tramo."""
    if not any(voz):
        return len(voz) * paso, 0.0
    return voz.index(True) * paso, voz[::-1].index(True) * paso


# ---------------------------------------------------------------- bordes limpios

def silencios(env_dbfs, i0, i1, umbral=SILENCIO_DBFS, minimo=SILENCIO_MIN_VENTANAS):
    """[(i, j)] de los silencios reales (al menos `minimo` ventanas bajo `umbral`) entre las ventanas i0 e i1."""
    i0, i1 = max(0, i0), min(len(env_dbfs), i1)
    if i1 <= i0:
        return []
    bajo = [v < umbral for v in env_dbfs[i0:i1]]
    return [(i0 + a, i0 + b) for a, b in tramos_de_voz(bajo) if b - a >= minimo]


def _mas_callado(env_dbfs, a, b):
    a, b = max(0, a), min(len(env_dbfs), max(b, a + 1))
    tramo = list(env_dbfs[a:b])
    return (a + tramo.index(min(tramo))) * PASO


def fin_limpio(env_dbfs, fin_whisper, siguiente=None):
    """Corte al final de una frase: dentro del primer silencio real; si habla de corrido, en el hueco mas hondo."""
    sig = fin_whisper + 2.0 if siguiente is None else siguiente
    i0 = int((fin_whisper - 0.03) / PASO)
    sil = silencios(env_dbfs, i0, int(min(fin_whisper + 1.0, sig - 0.05) / PASO))
    if sil:
        return round(sil[0][0] * PASO + 0.05, 3)
    return round(_mas_callado(env_dbfs, i0, int(min(fin_whisper + 0.35, sig + 0.15) / PASO)), 3)


def inicio_limpio(env_dbfs, ini_whisper):
    """Corte al inicio de una frase: al final del ultimo silencio real antes de ella, o en el hueco mas hondo."""
    sil = [s for s in silencios(env_dbfs, int((ini_whisper - 0.5) / PASO), int((ini_whisper + 0.15) / PASO))
           if s[1] > int((ini_whisper - 0.3) / PASO)]
    if sil:
        return round(max(0.0, sil[-1][1] * PASO - 0.05), 3)
    return round(_mas_callado(env_dbfs, int((ini_whisper - 0.25) / PASO), int((ini_whisper + 0.12) / PASO)), 3)


def bordes(env_dbfs, frases):
    """Para cada frase {"ini", "fin", "siguiente"?} devuelve su corte limpio y el nivel en cada borde."""
    salida = []
    for f in frases:
        a = inicio_limpio(env_dbfs, float(f["ini"]))
        b = fin_limpio(env_dbfs, float(f["fin"]), f.get("siguiente"))
        salida.append({"ini": a, "fin": b,
                       "nivel_ini_dbfs": _nivel(env_dbfs, a), "nivel_fin_dbfs": _nivel(env_dbfs, b)})
    return salida


def _nivel(env_dbfs, t):
    return round(float(env_dbfs[min(len(env_dbfs) - 1, max(0, int(t / PASO)))]), 1)


# ---------------------------------------------------------------- tomas

def partir_en_tomas(db_rel, paso=PASO):
    """[(ini, fin)] de cada toma: tramos de voz separados por silencios de al menos 0.35 s."""
    piso = percentil(db_rel, 10) + SOBRE_PISO_DB
    voz = [v > piso for v in db_rel]
    salida, i, n = [], 0, len(voz)
    while i < n:
        if not voz[i]:
            i += 1
            continue
        j = _fin_de_toma(voz, i, paso)
        if (j - i) * paso >= VOZ_MIN_TOMA:
            salida.append((round(i * paso, 2), round(j * paso, 2)))
        i = j
    return salida


def _fin_de_toma(voz, i, paso):
    j, n = i, len(voz)
    while j < n:
        if voz[j]:
            j += 1
            continue
        k = j
        while k < n and not voz[k]:
            k += 1
        if (k - j) * paso >= SILENCIO_ENTRE_TOMAS or k == n:
            break
        j = k
    return j


def _elegida(e, tomas):
    i, k0, k1 = (e[0], e[1], e[2] if len(e) > 2 else None) if isinstance(e, (list, tuple)) else (e, 0, None)
    ultima = len(tomas[i]["palabras"]) - 1
    return i, k0, ultima if k1 is None else k1


def _callado_entre(env_dbfs, a, b):
    if env_dbfs is None or b <= a:
        return round((a + b) / 2, 3)
    return round(_mas_callado(env_dbfs, int(a / PASO), int(b / PASO) + 1), 3)


def segmentos_de_tomas(tomas, elegidas, env_dbfs):
    """[(ini, fin)] del original para cada toma elegida (o trozo de toma) con su respiro."""
    salida = []
    for e in elegidas:
        i, k0, k1 = _elegida(e, tomas)
        toma, palabras = tomas[i], tomas[i]["palabras"]
        if k0 > 0:
            ini = _callado_entre(env_dbfs, palabras[k0 - 1][2] - MARGEN_PALABRA, palabras[k0][1] + MARGEN_PALABRA)
        else:
            antes = tomas[i - 1]["fin"] if i > 0 else 0.0
            ini = max(toma["ini"] - RESPIRO_ANTES, (antes + toma["ini"]) / 2)
        if k1 < len(palabras) - 1:
            fin = _callado_entre(env_dbfs, palabras[k1][2] - MARGEN_PALABRA, palabras[k1 + 1][1] + MARGEN_PALABRA)
        else:
            despues = tomas[i + 1]["ini"] if i + 1 < len(tomas) else toma["fin"] + 2 * RESPIRO_DESPUES
            fin = min(toma["fin"] + RESPIRO_DESPUES, (toma["fin"] + despues) / 2)
        salida.append((round(ini, 3), round(fin, 3)))
    return salida


# ---------------------------------------------------------------- uniones y filtro

def puntos_de_union(tramos):
    """Segundos del video cortado donde se pega un tramo con el siguiente."""
    return list(accumulate(b - a for a, b in tramos))[:-1]


def revisar_uniones(env_dbfs, tramos, maximo=UNION_MAX_DBFS):
    """[{segundo, nivel_dbfs, pasa}] con el punto mas bajo alrededor de cada union del corte."""
    radio = int(round(UNION_RADIO / PASO))
    salida = []
    for t in puntos_de_union(tramos):
        i = int(round(t / PASO))
        nivel = float(min(env_dbfs[max(0, i - radio):min(len(env_dbfs), i + radio + 1)]))
        salida.append({"segundo": round(float(t), 3), "nivel_dbfs": round(nivel, 1), "pasa": nivel <= maximo})
    return salida


def filtro_ffmpeg(tramos):
    """filter_complex que recorta cada tramo (video y audio con fundido de 12 ms) y los concatena en [v][a]."""
    if not tramos:
        raise ErrorDeCorte("no hay tramos que cortar")
    partes, entradas = [], []
    for k, (a, b) in enumerate(tramos):
        partes.append(f"[0:v]trim={a:.3f}:{b:.3f},setpts=PTS-STARTPTS[v{k}];"
                      f"[0:a]atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS,afade=t=in:d={FUNDIDO},"
                      f"afade=t=out:st={max(0.0, b - a - FUNDIDO):.3f}:d={FUNDIDO}[a{k}];")
        entradas.append(f"[v{k}][a{k}]")
    return "".join(partes) + "".join(entradas) + f"concat=n={len(tramos)}:v=1:a=1[v][a]"


# ---------------------------------------------------------------- CLI

def _leer_tramos(ruta):
    datos = json.loads(Path(ruta).read_text(encoding="utf-8"))
    tramos = datos["tramos"] if isinstance(datos, dict) else datos
    if not tramos or any(len(t) != 2 or float(t[1]) <= float(t[0]) for t in tramos):
        raise ErrorDeCorte(f"{ruta}: los tramos van como [[ini, fin], ...] con fin > ini")
    return [(float(a), float(b)) for a, b in tramos]


def _cmd_compactar(args):
    x = leer_audio(args.audio, SR)
    segmentos = _leer_tramos(args.tramos) if args.tramos else [(0.0, len(x) / SR)]
    db_rel = envolvente_relativa(x, SR)
    tramos = compactar(segmentos, db_rel, hueco_max=args.hueco_max)
    huecos = pausas(tramos, db_rel)
    return {"tramos": tramos, "pausa_max": max(huecos, default=0.0), "pausas": huecos,
            "duracion_original": round(len(x) / SR, 3), "duracion_corte": round(sum(b - a for a, b in tramos), 3)}


def _cmd_bordes(args):
    frases = json.loads(Path(args.frases).read_text(encoding="utf-8"))
    return {"cortes": bordes(envolvente_dbfs(leer_audio(args.audio, SR), SR), frases)}


def _cmd_partir(args):
    tomas = partir_en_tomas(envolvente_relativa(leer_audio(args.audio, SR), SR))
    return {"tomas": tomas, "nota": "transcribe cada toma por separado y elige las buenas contra el guion"}


def _cmd_elegir(args):
    tomas = json.loads(Path(args.tomas).read_text(encoding="utf-8"))
    elegidas = json.loads(args.elegidas)
    env = envolvente_dbfs(leer_audio(args.audio, SR), SR)
    return {"tramos": segmentos_de_tomas(tomas, elegidas, env)}


def _cmd_uniones(args):
    resultado = revisar_uniones(envolvente_dbfs(leer_audio(args.corte, SR), SR), _leer_tramos(args.cortes))
    return {"uniones": resultado, "todas_pasan": all(u["pasa"] for u in resultado), "maximo_dbfs": UNION_MAX_DBFS}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("compactar")
    c.add_argument("audio")
    c.add_argument("--tramos")
    c.add_argument("--hueco-max", type=float, default=HUECO_MAX)
    b = sub.add_parser("bordes")
    b.add_argument("audio")
    b.add_argument("frases")
    u = sub.add_parser("uniones")
    u.add_argument("corte")
    u.add_argument("cortes")
    t = sub.add_parser("partir")
    t.add_argument("audio")
    e = sub.add_parser("elegir")
    e.add_argument("audio")
    e.add_argument("tomas")
    e.add_argument("--elegidas", required=True)
    f = sub.add_parser("filtro")
    f.add_argument("cortes")
    args = p.parse_args(argv)
    if args.cmd == "filtro":
        print(filtro_ffmpeg(_leer_tramos(args.cortes)))
        return 0
    comandos = {"compactar": _cmd_compactar, "bordes": _cmd_bordes, "uniones": _cmd_uniones,
                "partir": _cmd_partir, "elegir": _cmd_elegir}
    resultado = comandos[args.cmd](args)
    print(json.dumps(resultado, ensure_ascii=False, indent=1))
    return 0 if resultado.get("todas_pasan", True) else 1


if __name__ == "__main__":
    sys.exit(main())
