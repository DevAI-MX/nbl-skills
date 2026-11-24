import shutil
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import tv_vieja  # noqa: E402


def test_textura_alterna_dos_filas_blancas_y_dos_a_196():
    t = tv_vieja.textura_lineas(3, 10)
    assert t.shape == (10, 3)
    assert list(t[:8, 0]) == [255, 255, 196, 196, 255, 255, 196, 196]


def test_pgm_tiene_cabecera_y_tamano_correctos(tmp_path):
    ruta = tmp_path / "l.pgm"
    tv_vieja.escribir_pgm(ruta, tv_vieja.textura_lineas(4, 8))
    datos = ruta.read_bytes()
    assert datos.startswith(b"P5\n4 8\n255\n") and len(datos) == len(b"P5\n4 8\n255\n") + 32


def test_cadena_es_la_receta_aprobada_sin_parpadeo():
    for pieza in ("saturation=0.8", "contrast=1.04", "brightness=0.045", "rgbashift=rh=-3:bh=3",
                  "noise=alls=16:allf=t+u", "blend=all_mode=multiply", "lenscorrection=k1=0.05:k2=0.02",
                  "vignette=angle=PI/6"):
        assert pieza in tv_vieja.CADENA
    assert "flicker" not in tv_vieja.CADENA and "geq" not in tv_vieja.CADENA


def test_comando_copia_el_audio_si_existe():
    cmd = tv_vieja.comando("ffmpeg", "a.mp4", "l.pgm", "b.mp4")
    assert cmd[cmd.index("-c:a") + 1] == "copy" and "0:a?" in cmd


@pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="ffmpeg no instalado")
def test_aplica_el_look_a_un_video_real(tmp_path):
    entrada, salida = tmp_path / "e.mp4", tmp_path / "s.mp4"
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-f", "lavfi", "-i", "testsrc=s=108x192:d=1:r=30",
                    "-pix_fmt", "yuv420p", str(entrada)], check=True)
    tv_vieja.aplicar(entrada, salida, 108, 192)
    assert salida.stat().st_size > 0


def test_entrada_inexistente_lanza_error(tmp_path):
    if shutil.which("ffmpeg") is None:
        pytest.skip("ffmpeg no instalado")
    with pytest.raises(tv_vieja.ErrorDeLook):
        tv_vieja.aplicar(tmp_path / "no.mp4", tmp_path / "s.mp4", 108, 192)


@pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="ffmpeg no instalado")
def test_cli(tmp_path, capsys):
    entrada, salida = tmp_path / "e.mp4", tmp_path / "s.mp4"
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-f", "lavfi", "-i", "testsrc=s=108x192:d=1:r=30",
                    "-pix_fmt", "yuv420p", str(entrada)], check=True)
    assert tv_vieja.main([str(entrada), str(salida), "--ancho", "108", "--alto", "192"]) == 0
    assert "listo" in capsys.readouterr().out
