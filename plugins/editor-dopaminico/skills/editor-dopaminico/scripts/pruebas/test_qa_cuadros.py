import json
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import qa_cuadros as qc  # noqa: E402

FPS = 10
HAY_FFMPEG = shutil.which("ffmpeg") is not None


def cuadros_con_movimiento(n, quietos=()):
    """n cuadros 16x9 que cambian siempre salvo en los indices de `quietos` (repiten el anterior)."""
    rng = np.random.default_rng(3)
    salida = [rng.integers(0, 255, (16, 9)).astype(np.float32)]
    for i in range(1, n):
        salida.append(salida[-1].copy() if i in quietos else np.clip(salida[-1] + rng.normal(0, 3, (16, 9)), 0, 255))
    return np.stack(salida)


def test_diferencias_mide_el_cambio_entre_cuadros_seguidos():
    c = np.stack([np.zeros((4, 4)), np.full((4, 4), 10.0), np.full((4, 4), 10.0)])
    assert list(qc.diferencias(c)) == [10.0, 0.0]


def test_pop_es_un_salto_tres_veces_mayor_que_sus_vecinos():
    d = np.array([1.0, 1.0, 9.0, 1.0, 1.0])
    assert qc.pops(d, FPS) == [(0.3, 9.0)]
    assert qc.pops(np.array([1.0, 1.0, 2.5, 1.0]), FPS) == []      # no llega a 3 veces


def test_tramo_muerto_es_mas_de_un_segundo_sin_cambio():
    d = qc.diferencias(cuadros_con_movimiento(40, quietos=range(10, 25)))
    assert qc.tramos_muertos(d, FPS) == [(0.9, 2.4)]
    d_corto = qc.diferencias(cuadros_con_movimiento(40, quietos=range(10, 18)))
    assert qc.tramos_muertos(d_corto, FPS) == []


def test_lectura_frase_y_palabras_sueltas():
    bloques = [{"text": "esto es una frase larga de leer", "start": 0, "end": 1.0},
               {"text": "OK", "start": 2, "end": 2.8}]
    cortos = qc.lectura(bloques)
    assert len(cortos) == 1 and cortos[0]["minimo"] == pytest.approx(25 / 15 + 1.5, abs=0.01)


def test_negro_ignora_el_cierre_del_formato():
    tramos = [(0.0, 0.3), (9.2, 10.0)]
    assert qc.negro_fuera_del_cierre(tramos, duracion=10.0, cierre=1.0) == [(0.0, 0.3)]


def test_lee_blackdetect():
    s = "[blackdetect @ 0x1] black_start:0 black_end:0.4 black_duration:0.4"
    assert qc.leer_negro(s) == [(0.0, 0.4)]


@pytest.mark.skipif(not HAY_FFMPEG, reason="ffmpeg no instalado")
def test_video_real_con_tramo_quieto_y_negro(tmp_path):
    video = tmp_path / "v.mp4"
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-f", "lavfi", "-i", "testsrc=s=90x160:d=4:r=10",
                    "-vf", "drawbox=c=black:t=fill:enable='lt(t,0.5)',loop=loop=15:size=1:start=15",
                    "-pix_fmt", "yuv420p", str(video)], check=True)
    r = qc.revisar(str(video), bloques=[], cierre=0.0)
    assert r["negro"] and r["muertos"]
    assert qc.main([str(video)]) == 1


@pytest.mark.skipif(not HAY_FFMPEG, reason="ffmpeg no instalado")
def test_cli_deja_hojas_y_pasa_con_video_limpio(tmp_path):
    video, bloques = tmp_path / "v.mp4", tmp_path / "b.json"
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-f", "lavfi", "-i", "testsrc=s=90x160:d=3:r=10",
                    "-pix_fmt", "yuv420p", str(video)], check=True)
    bloques.write_text(json.dumps([{"text": "hola", "start": 0.0, "end": 2.0}]))
    assert qc.main([str(video), "--bloques", str(bloques), "--hojas", str(tmp_path / "qa")]) == 0
    assert (tmp_path / "qa" / "hoja.jpg").exists() and (tmp_path / "qa" / "celular.jpg").exists()
