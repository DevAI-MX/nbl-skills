import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import escuchar  # noqa: E402
from audio_io import escribir_wav  # noqa: E402

SR = escuchar.SR


def tono(segundos, amp, f=440):
    return amp * np.sin(2 * np.pi * f * np.arange(int(segundos * SR)) / SR)


def con_golpe(duracion, en, amp, largo=0.2):
    x = np.zeros(int(duracion * SR))
    i = int(en * SR)
    x[i:i + int(largo * SR)] = tono(largo, amp, 1000)
    return x


def test_detecta_el_arranque_de_cada_efecto():
    efectos = con_golpe(3, 0.5, 0.3) + con_golpe(3, 2.0, 0.3)
    assert escuchar.golpes(efectos) == [pytest.approx(0.5, abs=0.02), pytest.approx(2.0, abs=0.02)]


def test_efecto_al_mismo_nivel_que_la_musica_esta_bien():
    musica = tono(3, 0.1)
    d = escuchar.efecto_contra_musica(con_golpe(3, 1.0, 0.1), musica, 1.0)
    assert d == pytest.approx(0, abs=0.5) and escuchar.veredicto(d) == "bien"


def test_limites_del_rango_normal_y_sutil():
    assert escuchar.veredicto(-10.0) == "bien" and escuchar.veredicto(3.0) == "bien"
    assert escuchar.veredicto(-10.5).startswith("enterrado")
    assert escuchar.veredicto(3.5).startswith("tapa")
    assert escuchar.veredicto(-2.0, sutil=True).startswith("tapa")
    assert escuchar.veredicto(-12.0, sutil=True) == "bien"


def test_huecos_largos_sin_efectos():
    assert escuchar.huecos_sin_efectos([0.5, 2.0, 9.0]) == [(2.0, 9.0)]


def test_musica_bajo_voz_mide_solo_donde_habla():
    voz = np.concatenate([tono(1, 0.3), np.zeros(SR)])      # el silencio no debe bajar el nivel de voz
    musica = tono(2, 0.3 / 10 ** (18 / 20))
    assert escuchar.musica_bajo_voz(voz, musica) == pytest.approx(18, abs=0.2)


def test_voz_en_silencio_lanza_error():
    with pytest.raises(escuchar.ErrorDeMezcla):
        escuchar.rms_de_voz(np.zeros(SR))


def test_cli_objetivo_fuera_de_tolerancia_sale_1(tmp_path, capsys):
    voz, mus = tmp_path / "voz.wav", tmp_path / "mus.wav"
    escribir_wav(voz, tono(2, 0.3), SR)
    escribir_wav(mus, tono(2, 0.3 / 10 ** (12 / 20)), SR)
    assert escuchar.main(["--musica", str(mus), "--voz", str(voz), "--objetivo", "18"]) == 1
    assert "no pasa" in capsys.readouterr().out
    assert escuchar.main(["--musica", str(mus), "--voz", str(voz), "--objetivo", "12"]) == 0


def test_cli_efecto_enterrado_sale_1(tmp_path):
    mus, fx = tmp_path / "mus.wav", tmp_path / "fx.wav"
    escribir_wav(mus, tono(3, 0.3), SR)
    escribir_wav(fx, con_golpe(3, 1.0, 0.01), SR)
    assert escuchar.main(["--musica", str(mus), "--efectos", str(fx)]) == 1


def test_cli_con_video_deja_el_mudo(tmp_path):
    import shutil
    import subprocess
    if shutil.which("ffmpeg") is None:
        pytest.skip("ffmpeg no instalado")
    mus, video = tmp_path / "mus.wav", tmp_path / "v.mp4"
    escribir_wav(mus, tono(1, 0.3), SR)
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-f", "lavfi", "-i", "color=c=gray:s=108x192:d=1",
                    "-pix_fmt", "yuv420p", str(video)], check=True)
    assert escuchar.main(["--musica", str(mus), "--video", str(video), "--salida", str(tmp_path / "rev")]) == 0
    assert (tmp_path / "rev" / "mudo.mp4").exists()


def test_pista_de_compas_suma_clics_fuertes_en_el_uno():
    musica = np.zeros(SR)
    pista = escuchar.pista_de_compas(musica, {"tiempos": [0.0, 0.5], "downbeats": [0.0]})
    uno = np.abs(pista[: int(0.03 * SR)]).max()
    otro = np.abs(pista[int(0.5 * SR): int(0.53 * SR)]).max()
    assert uno > otro > 0


def test_cli_compas_deja_compas_wav_y_capas(tmp_path):
    import json
    mus, fx, comp = tmp_path / "mus.wav", tmp_path / "fx.wav", tmp_path / "compas.json"
    escribir_wav(mus, tono(2, 0.1), SR)
    escribir_wav(fx, con_golpe(2, 0.5, 0.1), SR)
    comp.write_text(json.dumps({"bpm": 120, "tiempos": [0, 0.5, 1.0, 1.5], "downbeats": [0]}))
    salida = tmp_path / "rev"
    escuchar.main(["--musica", str(mus), "--efectos", str(fx), "--compas", str(comp), "--salida", str(salida)])
    for nombre in ("compas.wav", "solo-musica.wav", "solo-efectos.wav"):
        assert (salida / nombre).exists()
