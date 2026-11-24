import json
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import cortes  # noqa: E402
from audio_io import envolvente_dbfs, envolvente_relativa, escribir_wav  # noqa: E402

SR = cortes.SR
VOZ = 0.3              # ~-13 dBFS de RMS para un tono de amplitud 0.3
RESPIRACION = 0.012    # ~-28 dB bajo la voz: por debajo de VOZ_DB
PISO = 0.0005          # ruido de sala ~-69 dBFS


def senal(plan):
    """plan = [(segundos, amplitud)]: tono de 220 Hz con esa amplitud, mas un piso de ruido fijo."""
    rng = np.random.default_rng(7)
    partes = [amp * np.sin(2 * np.pi * 220 * np.arange(int(s * SR)) / SR) for s, amp in plan]
    x = np.concatenate(partes)
    return x + PISO * rng.standard_normal(len(x))


def test_compactar_deja_pausas_de_cola_mas_arranque():
    x = senal([(0.5, 0), (1.0, VOZ), (0.6, 0), (1.0, VOZ), (0.4, 0)])
    db = envolvente_relativa(x, SR)
    tramos = cortes.compactar([(0.0, len(x) / SR)], db)
    assert len(tramos) == 2
    assert cortes.pausas(tramos, db) == [pytest.approx(cortes.COLA + cortes.ARRANQUE, abs=0.021)]


def test_compactar_quita_respiraciones_nerviosas():
    x = senal([(1.0, VOZ), (0.2, 0), (0.3, RESPIRACION), (0.2, 0), (1.0, VOZ)])
    db = envolvente_relativa(x, SR)
    tramos = cortes.compactar([(0.0, len(x) / SR)], db)
    assert len(tramos) == 2
    assert cortes.pausas(tramos, db)[0] < 0.16


def test_compactar_no_toca_huecos_entre_silabas():
    x = senal([(0.6, VOZ), (0.12, 0), (0.6, VOZ)])
    tramos = cortes.compactar([(0.0, len(x) / SR)], envolvente_relativa(x, SR))
    assert len(tramos) == 1


def test_compactar_respeta_los_limites_del_segmento():
    x = senal([(0.3, 0), (1.0, VOZ), (0.3, 0)])
    tramos = cortes.compactar([(0.4, 1.0)], envolvente_relativa(x, SR))
    assert tramos[0][0] >= 0.4 and tramos[-1][1] <= 1.0


def test_pausas_de_un_solo_tramo_es_lista_vacia():
    x = senal([(1.0, VOZ)])
    assert cortes.pausas([(0.0, 1.0)], envolvente_relativa(x, SR)) == []


def test_fin_limpio_cae_dentro_del_silencio_real_y_no_en_el_tiempo_de_whisper():
    x = senal([(1.0, VOZ), (0.5, 0), (1.0, VOZ)])
    env = envolvente_dbfs(x, SR)
    corte = cortes.fin_limpio(env, fin_whisper=1.3, siguiente=1.5)   # whisper alarga la palabra 0.3 s
    assert 1.0 < corte < 1.5 and env[int(corte / 0.01)] < cortes.SILENCIO_DBFS


def test_fin_limpio_no_corta_la_cola_que_whisper_da_por_terminada():
    x = senal([(1.0, VOZ), (0.5, 0), (1.0, VOZ)])
    env = envolvente_dbfs(x, SR)
    corte = cortes.fin_limpio(env, fin_whisper=0.9, siguiente=1.5)   # la voz sigue hasta 1.0
    assert 1.0 < corte < 1.1


def test_fin_limpio_sin_silencio_busca_el_hueco_mas_hondo():
    x = senal([(1.0, VOZ), (0.03, 0.002), (1.0, VOZ)])
    env = envolvente_dbfs(x, SR)
    assert cortes.fin_limpio(env, fin_whisper=0.98, siguiente=1.05) == pytest.approx(1.0, abs=0.02)


def test_inicio_limpio_cae_justo_antes_de_la_voz():
    x = senal([(1.0, VOZ), (0.5, 0), (1.0, VOZ)])
    env = envolvente_dbfs(x, SR)
    corte = cortes.inicio_limpio(env, ini_whisper=1.4)   # whisper adelanta la palabra 0.1 s
    assert 1.4 < corte <= 1.5


def test_bordes_reporta_nivel_en_cada_corte():
    x = senal([(0.5, 0), (1.0, VOZ), (0.5, 0)])
    env = envolvente_dbfs(x, SR)
    r = cortes.bordes(env, [{"ini": 0.45, "fin": 1.6}])[0]
    assert r["nivel_ini_dbfs"] < cortes.SILENCIO_DBFS and r["nivel_fin_dbfs"] < cortes.SILENCIO_DBFS


def test_union_en_silencio_pasa_y_union_sobre_voz_falla():
    limpio = senal([(1.0, VOZ), (0.1, 0), (1.0, VOZ)])
    sobre_voz = senal([(2.1, VOZ)])
    tramos = [(0.0, 1.05), (1.05, 2.1)]
    assert cortes.revisar_uniones(envolvente_dbfs(limpio, SR), tramos)[0]["pasa"]
    assert not cortes.revisar_uniones(envolvente_dbfs(sobre_voz, SR), tramos)[0]["pasa"]


def test_filtro_lleva_un_trim_y_fundidos_por_tramo():
    filtro = cortes.filtro_ffmpeg([(0.0, 1.0), (2.0, 3.5)])
    assert filtro.count("trim=") == 4 and "concat=n=2:v=1:a=1[v][a]" in filtro
    assert "afade=t=out:st=1.488:d=0.012" in filtro


def test_filtro_sin_tramos_lanza_error():
    with pytest.raises(cortes.ErrorDeCorte):
        cortes.filtro_ffmpeg([])


def test_tramos_mal_formados_lanzan_error(tmp_path):
    ruta = tmp_path / "c.json"
    ruta.write_text(json.dumps({"tramos": [[2.0, 1.0]]}))
    with pytest.raises(cortes.ErrorDeCorte):
        cortes._leer_tramos(ruta)


def test_cli_compactar_de_punta_a_punta(tmp_path, capsys):
    wav = tmp_path / "voz.wav"
    escribir_wav(wav, senal([(0.5, 0), (1.0, VOZ), (0.8, 0), (1.0, VOZ), (0.5, 0)]), SR)
    assert cortes.main(["compactar", str(wav)]) == 0
    salida = json.loads(capsys.readouterr().out)
    assert len(salida["tramos"]) == 2 and salida["pausa_max"] <= 0.14
    assert salida["duracion_corte"] < salida["duracion_original"]


def test_cli_uniones_devuelve_1_si_alguna_falla(tmp_path):
    wav, js = tmp_path / "corte.wav", tmp_path / "c.json"
    escribir_wav(wav, senal([(2.0, VOZ)]), SR)
    js.write_text(json.dumps({"tramos": [[0, 1], [1, 2]]}))
    assert cortes.main(["uniones", str(wav), str(js)]) == 1


TOMAS = [{"ini": 1.0, "fin": 2.0, "palabras": [["hola", 1.0, 1.4], ["que", 1.5, 1.6], ["tal", 1.7, 2.0]]},
         {"ini": 2.2, "fin": 3.0, "palabras": [["bien", 2.2, 3.0]]},
         {"ini": 5.0, "fin": 6.0, "palabras": [["adios", 5.0, 6.0]]}]


def test_toma_completa_lleva_respiro_sin_invadir_la_vecina():
    segs = cortes.segmentos_de_tomas(TOMAS, [0, 2], None)
    assert segs[0] == pytest.approx((1.0 - cortes.RESPIRO_ANTES, 2.1))   # hasta la mitad del hueco con la toma 1
    assert segs[1] == pytest.approx((5.0 - cortes.RESPIRO_ANTES, 6.0 + cortes.RESPIRO_DESPUES))


def test_trozo_de_toma_corta_en_el_punto_mas_callado():
    env = [-20.0] * 700
    env[148] = -60.0                                                    # el hueco real entre "hola" y "que"
    segs = cortes.segmentos_de_tomas(TOMAS, [[0, 1, 2]], env)
    assert segs[0][0] == pytest.approx(1.48)


def test_partir_en_tomas_por_silencios_reales():
    x = senal([(0.5, 0), (1.0, VOZ), (0.2, 0), (0.8, VOZ), (0.6, 0), (1.0, VOZ), (0.3, 0)])
    tomas = cortes.partir_en_tomas(envolvente_relativa(x, SR))
    assert len(tomas) == 2                                              # el hueco de 0.2 s no parte la toma
    assert tomas[0][0] == pytest.approx(0.5, abs=0.02)


def test_cli_partir_y_elegir(tmp_path, capsys):
    wav, tomas_json = tmp_path / "voz.wav", tmp_path / "tomas.json"
    escribir_wav(wav, senal([(0.5, 0), (1.0, VOZ), (0.6, 0), (1.0, VOZ), (0.5, 0)]), SR)
    assert cortes.main(["partir", str(wav)]) == 0
    tomas = json.loads(capsys.readouterr().out)["tomas"]
    assert len(tomas) == 2
    tomas_json.write_text(json.dumps([{"ini": a, "fin": b, "palabras": [["x", a, b]]} for a, b in tomas]))
    assert cortes.main(["elegir", str(wav), str(tomas_json), "--elegidas", "[1]"]) == 0
    tramo = json.loads(capsys.readouterr().out)["tramos"][0]
    assert tramo[0] == pytest.approx(tomas[1][0] - cortes.RESPIRO_ANTES, abs=0.001)
