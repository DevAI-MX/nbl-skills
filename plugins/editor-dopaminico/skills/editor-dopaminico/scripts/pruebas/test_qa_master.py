import shutil
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import qa_master as qa  # noqa: E402

OBJ = {"lufs": -16.0, "pico": -1.5, "pausa_max": 0.25, "resolucion": "1080x1920"}
STDERR_LOUDNORM = 'basura\n[Parsed_loudnorm_0 @ 0x1]\n{\n "input_i" : "-16.2",\n "input_tp" : "-1.9"\n}\n'


def test_lee_loudnorm():
    assert qa.leer_loudnorm(STDERR_LOUDNORM) == (-16.2, -1.9)


def test_loudnorm_sin_json_lanza_error():
    with pytest.raises(qa.ErrorDeQA):
        qa.leer_loudnorm("nada que ver")


def test_lee_silencios():
    s = "[silencedetect] silence_end: 3.1 | silence_duration: 0.31\n[silencedetect] silence_duration: 0.5"
    assert qa.leer_silencios(s) == [0.31, 0.5]


def test_lee_stream_con_y_sin_transferencia():
    assert qa.leer_stream("h264,1080,1920,bt709\n") == (1080, 1920, "h264", "bt709")
    assert qa.leer_stream("h264,1080,1920") == (1080, 1920, "h264", "")
    with pytest.raises(qa.ErrorDeQA):
        qa.leer_stream("")


def test_todo_en_regla_pasa():
    filas = qa.juzgar((1080, 1920, "h264", "bt709"), (-16.2, -1.9), [], OBJ)
    assert all(p for _, _, p in filas)


def test_hevc_o_hlg_es_clip_hdr_colado():
    assert not qa.juzgar((1080, 1920, "hevc", ""), (-16, -2), [], OBJ)[1][2]
    assert not qa.juzgar((1080, 1920, "h264", "arib-std-b67"), (-16, -2), [], OBJ)[1][2]


def test_loudness_fuera_de_tolerancia_y_pico_alto_fallan():
    filas = dict((n, p) for n, _, p in qa.juzgar((1080, 1920, "h264", ""), (-14.0, -1.0), [0.4], OBJ))
    assert not filas["Loudness integrado"] and not filas["Pico real"] and not filas["Pausas"]


@pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="ffmpeg no instalado")
def test_mide_un_archivo_real(tmp_path):
    mp4 = tmp_path / "f.mp4"
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-f", "lavfi", "-i", "color=c=gray:s=108x192:d=3",
                    "-f", "lavfi", "-i", "aevalsrc='0.3*sin(2*PI*220*t)*lt(mod(t,1.5),1.0)':s=48000:d=3",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", str(mp4)], check=True)
    assert qa.medir_video(str(mp4))[:3] == (108, 192, "h264")
    assert len(qa.medir_pausas(str(mp4), 0.25)) >= 1
    lufs, pico = qa.medir_loudness(str(mp4))
    assert -40 < lufs < 0 and pico < 0
    assert qa.main([str(mp4)]) == 1
