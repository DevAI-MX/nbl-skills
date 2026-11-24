import json
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import revisar_subtitulos as rs  # noqa: E402


def cue(text, start, end):
    return {"text": text, "start": start, "end": end}


def palabras(*trios):
    return [{"t": w, "n": rs.norm(w), "s": s, "e": e} for w, s, e in trios]


def test_detecta_cue_duplicado():
    assert len(rs.duplicados([cue("hola mundo", 0, 1), cue("hola mundo", 1, 2)])) == 1


def test_detecta_solape_pero_no_el_toque():
    assert len(rs.solapes([cue("a", 0, 1.2), cue("b", 1.0, 2)])) == 1
    assert rs.solapes([cue("a", 0, 1.0), cue("b", 1.0, 2)]) == []


def test_cue_encima_de_grafico_con_tolerancia_de_borde():
    graf = [cue("ventas", 2.0, 3.0)]
    assert len(rs.encima_de_bloques([cue("x", 2.5, 3.5)], graf)) == 1
    assert rs.encima_de_bloques([cue("x", 2.95, 4.0)], graf) == []


def test_repeticion_solo_con_dos_palabras_de_contenido_cerca():
    graf = [cue("vender mas caro", 10, 11)]
    assert len(rs.repeticiones([cue("puedes vender mas caro hoy", 12, 13)], graf)) == 1
    assert rs.repeticiones([cue("vender en la tienda", 12, 13)], graf) == []
    assert rs.repeticiones([cue("vender mas caro", 30, 31)], graf) == []


def test_palabra_dicha_que_no_aparece():
    fallas = rs.ausentes([cue("hola", 0, 1)], [], palabras(("hola", 0.1, 0.4), ("amigo", 0.5, 0.9)))
    assert fallas == ["no aparece 'amigo' (se dice en 0.50s)"]


def test_ausentes_ignora_signos_y_acentos():
    assert rs.ausentes([cue("Rapido!", 0, 1)], [], palabras(("rápido", 0.1, 0.4))) == []


def test_frase_que_termina_en_conector():
    assert len(rs.terminan_en_conector([cue("lo que hago para", 0, 1)])) == 1
    assert rs.terminan_en_conector([cue("lo que hago", 0, 1)]) == []


def test_subtitulo_que_entra_antes_de_la_voz():
    voz = palabras(("hoy", 1.20, 1.4))
    assert len(rs.entran_antes_de_la_voz([cue("hoy toca", 1.00, 2)], voz)) == 1
    assert rs.entran_antes_de_la_voz([cue("hoy toca", 1.18, 2)], voz) == []


def test_lee_srt(tmp_path):
    srt = tmp_path / "s.srt"
    srt.write_text("1\n00:00:01,000 --> 00:00:02,500\nhola mundo\n\n2\n00:00:02,500 --> 00:00:03,000\nadios\n")
    cues = rs.leer_cues(srt)
    assert cues[0] == {"text": "hola mundo", "start": 1.0, "end": 2.5} and len(cues) == 2


def test_srt_sin_tiempos_lanza_error(tmp_path):
    srt = tmp_path / "s.srt"
    srt.write_text("hola\n")
    with pytest.raises(rs.ErrorDeEntrada):
        rs.leer_cues(srt)


def test_lee_transcripcion_de_whisper_y_de_lista(tmp_path):
    w = tmp_path / "w.json"
    w.write_text(json.dumps({"segments": [{"words": [{"word": " Hola", "start": 0.1, "end": 0.3}]}]}))
    lista = tmp_path / "l.json"
    lista.write_text(json.dumps([["Hola", 0.1, 0.3], [",", 0.3, 0.3]]))
    assert rs.leer_transcripcion(w)[0]["n"] == "hola"
    assert len(rs.leer_transcripcion(lista)) == 1


def test_pixeles_de_texto_cuenta_blanco_en_la_franja():
    cuadro = np.zeros((960, 540, 3), np.uint8)
    cuadro[650:670, 100:400] = 255                      # una linea de "texto" al ~69 %
    assert rs.pixeles_de_texto(cuadro, 69) > rs.PX_TEXTO_MIN
    assert rs.pixeles_de_texto(cuadro, 20) == 0


def test_cli_limpio_sale_0_y_con_fallas_sale_1(tmp_path, capsys):
    cues, trans = tmp_path / "c.json", tmp_path / "t.json"
    trans.write_text(json.dumps([["hola", 0.10, 0.4], ["amigo", 0.5, 0.9]]))
    cues.write_text(json.dumps([cue("hola amigo", 0.10, 1.0)]))
    assert rs.main(["--cues", str(cues), "--transcript", str(trans)]) == 0
    cues.write_text(json.dumps([cue("hola de", 0.10, 1.0), cue("hola de", 0.9, 1.5)]))
    assert rs.main(["--cues", str(cues), "--transcript", str(trans)]) == 1
    assert "REVISION FALLIDA" in capsys.readouterr().out


@pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="ffmpeg no instalado")
def test_nivel_render_con_video_real(tmp_path):
    video = tmp_path / "v.mp4"
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-f", "lavfi", "-i", "color=c=black:s=540x960:d=2",
                    "-vf", "drawbox=x=100:y=650:w=300:h=20:color=white:t=fill:enable='lt(t,1)'",
                    "-pix_fmt", "yuv420p", str(video)], check=True)
    assert rs.nivel_render([cue("se ve", 0.2, 0.8)], video, 69) == []
    assert len(rs.nivel_render([cue("no se ve", 1.2, 1.8)], video, 69)) == 1


def test_lo_dicho_tras_el_cta_no_cuenta_como_ausente():
    voz = palabras(("comenta", 10.0, 10.3), ("clave", 10.4, 10.8), ("nos", 11.0, 11.1), ("vemos", 11.2, 11.5))
    cues = [cue("comenta clave", 10.0, 12.0)]
    assert len(rs.ausentes(cues, [], voz)) == 2
    assert rs.ausentes(cues, [], voz, desde=rs.segundo_del_cta(voz, "CLAVE")) == []


def test_segundo_del_cta_es_la_ultima_vez_que_se_dice():
    voz = palabras(("clave", 1.0, 1.3), ("hola", 2.0, 2.2), ("clave", 9.0, 9.4))
    assert rs.segundo_del_cta(voz, "clave") == 9.4
    with pytest.raises(rs.ErrorDeEntrada):
        rs.segundo_del_cta(voz, "otra")


def test_cli_con_cta_exime_lo_que_sigue(tmp_path):
    cues, trans = tmp_path / "c.json", tmp_path / "t.json"
    trans.write_text(json.dumps([["comenta", 0.1, 0.4], ["clave", 0.5, 0.9], ["chao", 1.2, 1.5]]))
    cues.write_text(json.dumps([cue("comenta clave", 0.1, 1.0)]))
    assert rs.main(["--cues", str(cues), "--transcript", str(trans)]) == 1
    assert rs.main(["--cues", str(cues), "--transcript", str(trans), "--cta", "clave"]) == 0
