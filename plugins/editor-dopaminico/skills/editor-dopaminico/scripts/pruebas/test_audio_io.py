import shutil
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import audio_io  # noqa: E402

SR = 16000


def test_wav_de_16_bits_se_lee_sin_ffmpeg(tmp_path):
    ruta = tmp_path / "a.wav"
    audio_io.escribir_wav(ruta, [0.5] * SR, SR)
    x = audio_io.leer_audio(ruta, SR)
    assert len(x) == SR and x[0] == pytest.approx(0.5, abs=1e-3)


def test_envolvente_relativa_pone_el_nivel_alto_en_cero():
    x = [0.3] * SR + [0.003] * SR
    env = audio_io.envolvente_relativa(x, SR)
    assert max(env) == pytest.approx(0, abs=0.1) and min(env) == pytest.approx(-40, abs=0.5)


def test_audio_mas_corto_que_una_ventana_lanza_error():
    with pytest.raises(audio_io.ErrorDeAudio):
        audio_io.envolvente_dbfs([0.0] * 10, SR)


def test_rms_de_tramo_vacio_es_el_piso():
    assert audio_io.rms_db([]) == audio_io.PISO_DB


@pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="ffmpeg no instalado")
def test_otros_formatos_y_otra_frecuencia_pasan_por_ffmpeg(tmp_path):
    m4a, wav48 = tmp_path / "a.m4a", tmp_path / "b.wav"
    for ruta in (m4a, wav48):
        subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-f", "lavfi", "-i", "sine=f=220:d=1:sample_rate=48000",
                        str(ruta)], check=True)
    assert abs(len(audio_io.leer_audio(m4a, SR)) - SR) < SR * 0.1
    assert abs(len(audio_io.leer_audio(wav48, SR)) - SR) < SR * 0.05


@pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="ffmpeg no instalado")
def test_archivo_inexistente_lanza_error_con_contexto(tmp_path):
    with pytest.raises(audio_io.ErrorDeAudio, match="no pudo leer"):
        audio_io.leer_audio(tmp_path / "no.mp4", SR)


def test_percentil_interpola_como_numpy():
    assert audio_io.percentil([0, 10, 20, 30, 40], 50) == 20
    assert audio_io.percentil([0, 10], 99) == pytest.approx(9.9)
    with pytest.raises(audio_io.ErrorDeAudio):
        audio_io.percentil([], 50)


def test_wav_estereo_se_mezcla_a_mono(tmp_path):
    import wave
    from array import array
    ruta = tmp_path / "st.wav"
    with wave.open(str(ruta), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(array("h", [16384, 0] * 100).tobytes())
    x = audio_io.leer_audio(ruta, SR)
    assert len(x) == 100 and x[0] == pytest.approx(0.25, abs=1e-3)
