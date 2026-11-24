"""Pruebas de revisar.py. Correr desde scripts/: python3 -m unittest discover -s tests"""
import json
import struct
import sys
import tempfile
import unittest
import zlib
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))
import revisar  # noqa: E402


def png(ruta, ancho, alto):
    """PNG mínimo válido de ancho x alto (solo importa la cabecera)."""
    def bloque(tipo, datos):
        return struct.pack(">I", len(datos)) + tipo + datos + struct.pack(">I", zlib.crc32(tipo + datos) & 0xFFFFFFFF)
    ihdr = struct.pack(">IIBBBBB", ancho, alto, 8, 0, 0, 0, 0)
    Path(ruta).write_bytes(b"\x89PNG\r\n\x1a\n" + bloque(b"IHDR", ihdr) + bloque(b"IEND", b""))


PIE = '<div class="pie"><span class="handle">@tu_marca</span><span></span></div>'


def slide(cuerpo, pie=PIE):
    return f"<html><head><style>.x{{}}</style></head><body><div class='slide'>{cuerpo}{pie}</div></body></html>"


def carrusel(tmp, htmls, spec=None, pngs=None):
    carpeta = Path(tmp) / "c"
    (carpeta / "slides").mkdir(parents=True)
    for n, html in enumerate(htmls, 1):
        (carpeta / "slides" / f"slide-{n:02d}.html").write_text(html, encoding="utf-8")
    if spec is not None:
        (carpeta / "carrusel.json").write_text(json.dumps(spec), encoding="utf-8")
    if pngs is not None:
        (carpeta / "png").mkdir()
        for n, (w, h) in enumerate(pngs, 1):
            png(carpeta / "png" / f"slide-{n:02d}.png", w, h)
    return carpeta


class Texto(unittest.TestCase):
    def test_texto_visible_quita_estilos_scripts_comentarios_y_etiquetas(self):
        html = "<style>a{}</style><script>x=1</script><!-- c --><p>Hola &amp; <b>adiós</b></p>"
        self.assertEqual(revisar.texto_visible(html), "Hola & adiós")

    def test_contar_palabras_ignora_html(self):
        self.assertEqual(revisar.contar_palabras('Cómo <span class="mk-lima">escribir</span> un gancho'), 4)

    def test_sin_acento(self):
        self.assertEqual(revisar.sin_acento("CÓDIGOS"), "CODIGOS")


class Reglas(unittest.TestCase):
    def test_marca_flecha_y_numero_de_slide(self):
        errores, avisos = revisar.revisar_paginacion([slide("<span class='desliza'>desliza</span>"), slide("2 / 8")])
        self.assertEqual(len(errores), 1)
        self.assertEqual(len(avisos), 1)

    def test_pies_distintos_son_error(self):
        otro = '<div class="pie"><span class="handle">@tu_marca</span><span>3</span></div>'
        self.assertEqual(revisar.revisar_pies([slide("a"), slide("b")]), [])
        self.assertEqual(len(revisar.revisar_pies([slide("a"), slide("b", pie=otro)])), 1)

    def test_handle_repetido_en_una_slide(self):
        self.assertEqual(len(revisar.revisar_handle([slide("Sígueme @tu_marca")], "@tu_marca")), 1)
        self.assertEqual(revisar.revisar_handle([slide("Hola")], "@tu_marca"), [])

    def test_pendientes(self):
        self.assertEqual(len(revisar.revisar_pendientes([slide("{{TITULO}}")])), 1)

    def test_limites_de_palabras_en_laminas_interiores(self):
        largo = " ".join(["palabra"] * 31)
        spec = {"slides": [{"campos": {"GANCHO": largo}},
                           {"campos": {"TITULO": " ".join(["t"] * 15), "TEXTO": largo}},
                           {"campos": {"TITULO": "cierre " * 20}}]}
        errores, info = revisar.revisar_palabras(spec)
        self.assertEqual(len(errores), 2)
        self.assertIn("31 palabras", info[0])

    def test_total_de_slides(self):
        self.assertEqual(revisar.revisar_total(8), ([], []))
        self.assertEqual(len(revisar.revisar_total(5)[1]), 1)
        self.assertEqual(len(revisar.revisar_total(21)[0]), 1)

    def test_palabra_clave_choca_con_activa_sin_importar_acentos(self):
        with tempfile.TemporaryDirectory() as tmp:
            activas = Path(tmp) / "activas.txt"
            activas.write_text("# palabras activas\nCODIGOS\nREELS\n", encoding="utf-8")
            errores, info = revisar.revisar_palabra_clave("Códigos", activas)
            self.assertEqual(len(errores), 1)
            self.assertIn("CODIGOS", info[0])
            self.assertEqual(revisar.revisar_palabra_clave("GUIA", activas)[0], [])

    def test_pngs_tamano_y_cuenta(self):
        with tempfile.TemporaryDirectory() as tmp:
            carpeta = carrusel(tmp, [slide("a"), slide("b")], pngs=[(2160, 2700), (1080, 1350)])
            errores = revisar.revisar_pngs(carpeta / "png", 2)
            self.assertEqual(len(errores), 1)
            self.assertIn("1080x1350", errores[0])
            self.assertEqual(len(revisar.revisar_pngs(carpeta / "png", 3)), 2)

    def test_png_corrupto_es_error_no_excepcion(self):
        with tempfile.TemporaryDirectory() as tmp:
            carpeta = carrusel(tmp, [slide("a")], pngs=[])
            (carpeta / "png" / "slide-01.png").write_bytes(b"no soy png")
            self.assertEqual(len(revisar.revisar_pngs(carpeta / "png", 1)), 1)


class ReglasDeSegundaRonda(unittest.TestCase):
    def test_kicker_por_clase_es_error(self):
        errores, _ = revisar.revisar_kickers([slide('<div class="etiqueta">GUÍA RÁPIDA</div><h1>Gancho</h1>')])
        self.assertEqual(len(errores), 1)

    def test_kicker_en_mayusculas_antes_del_titulo_es_aviso(self):
        errores, avisos = revisar.revisar_kickers([slide("<span>EL PATRÓN</span><h2>Título real</h2>")])
        self.assertEqual(errores, [])
        self.assertEqual(len(avisos), 1)

    def test_pastilla_de_noticia_no_es_kicker(self):
        self.assertEqual(revisar.revisar_kickers([slide('<span class="pastilla">ÚLTIMO MOMENTO</span><h1>Titular</h1>')]),
                         ([], []))

    def test_negritas_en_tuit(self):
        self.assertEqual(len(revisar.revisar_negritas_tuit([slide('<p class="post">hola <b>fuerte</b></p>')])), 1)
        self.assertEqual(len(revisar.revisar_negritas_tuit([slide('<p class="post">hola <strong>x</strong></p>')])), 1)
        self.assertEqual(revisar.revisar_negritas_tuit([slide('<p class="post">hola</p>')]), [])

    def test_cierre_con_palabra_debe_ensenar_el_recurso(self):
        self.assertEqual(len(revisar.revisar_recurso([slide("a"), slide("Comenta GUIA")], "GUIA")), 1)
        self.assertEqual(revisar.revisar_recurso([slide("a"), slide('<div class="recurso"></div>')], "GUIA"), [])
        self.assertEqual(revisar.revisar_recurso([slide("a"), slide("Sígueme")], ""), [])

    def test_paginacion_permitida_si_la_referencia_la_trae(self):
        with tempfile.TemporaryDirectory() as tmp:
            spec = {"copia_paginacion_de_referencia": True, "slides": [{"campos": {}}]}
            carpeta = carrusel(tmp, [slide("<span class='pag'>1 / 1</span>")], spec)
            self.assertEqual(revisar.main([str(carpeta), "--sin-png"]), 0)

    def test_tuit_con_negritas_sale_1(self):
        with tempfile.TemporaryDirectory() as tmp:
            spec = {"formato": "tuit", "slides": [{"campos": {}}]}
            carpeta = carrusel(tmp, [slide('<p class="post"><b>x</b></p>')], spec)
            self.assertEqual(revisar.main([str(carpeta), "--sin-png"]), 1)


class LineaDeComandos(unittest.TestCase):
    def test_carrusel_limpio_sale_0(self):
        with tempfile.TemporaryDirectory() as tmp:
            spec = {"campos_comunes": {"HANDLE": "@tu_marca"},
                    "slides": [{"campos": {"GANCHO": "Tu gancho aquí"}}] + [{"campos": {"TITULO": "Uno"}}] * 6
                    + [{"campos": {"PALABRA": "GUIA"}}]}
            htmls = [slide(f"texto {n}") for n in range(7)] + [slide('<div class="recurso"></div> Comenta GUIA')]
            carpeta = carrusel(tmp, htmls, spec, pngs=[(2160, 2700)] * 8)
            self.assertEqual(revisar.main([str(carpeta), "--palabra", "GUIA"]), 0)

    def test_errores_salen_1(self):
        with tempfile.TemporaryDirectory() as tmp:
            carpeta = carrusel(tmp, [slide("{{X}}")])
            self.assertEqual(revisar.main([str(carpeta), "--sin-png"]), 1)

    def test_sin_slides_sale_1(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(revisar.main([tmp]), 1)


if __name__ == "__main__":
    unittest.main()
