"""Pruebas de build.py. Correr desde scripts/: python3 -m unittest discover -s tests"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))
import build  # noqa: E402

PLANTILLAS = SCRIPTS.parent / "assets" / "plantillas"
MARCA_CSS = "/* https://fonts.googleapis.com/css2?family=Inter:wght@400;800&display=swap */\n:root{--acento:#123456;}\n"

CAMPOS_POR_FORMATO = {
    "tipografico": [
        {"plantilla": "portada", "campos": {"GANCHO": "Tu gancho", "SUBTITULO": "Sub"}},
        {"plantilla": "contenido", "clase": "slide claro",
         "campos": {"TITULO": "Título", "TEXTO": "Texto corto"}},
        {"plantilla": "cierre", "campos": {"TITULO": "Te regalo", "ACCION": "Comenta",
                                           "PALABRA": "GUÍA", "QUE_RECIBE": "y te la mando"}},
    ],
}


def carrusel(tmp, slides, formato="tipografico", extra=None):
    carpeta = Path(tmp) / "carruseles" / "2026-01-01_prueba"
    carpeta.mkdir(parents=True)
    spec = {"formato": formato, "campos_comunes": {"HANDLE": "@tu_marca"}, "slides": slides}
    spec.update(extra or {})
    (carpeta / "carrusel.json").write_text(json.dumps(spec), encoding="utf-8")
    marca = Path(tmp) / "marca.css"
    marca.write_text(MARCA_CSS, encoding="utf-8")
    return carpeta, marca


class BloquesOpcionales(unittest.TestCase):
    HTML = "a<!--?IMAGEN--><img src='x'><!--/?IMAGEN-->b<!--?NUM-->9<!--/?NUM-->c"

    def test_quita_los_bloques_no_pedidos(self):
        self.assertEqual(build.quitar_bloques(self.HTML, []), "abc")

    def test_conserva_el_contenido_de_los_pedidos_sin_marcas(self):
        self.assertEqual(build.quitar_bloques(self.HTML, ["NUM"]), "ab9c")


class Llenado(unittest.TestCase):
    def test_reemplaza_campos_y_reporta_pendientes(self):
        html = build.llenar("{{A}} y {{B}}", {"A": "uno"})
        self.assertEqual(html, "uno y {{B}}")
        self.assertEqual(build.pendientes(html), ["B"])

    def test_un_valor_puede_usar_otro_campo_como_raiz(self):
        self.assertEqual(build.llenar('<img src="{{IMG}}">', {"IMG": "{{RAIZ}}/imagenes/a.jpg", "RAIZ": ".."}),
                         '<img src="../imagenes/a.jpg">')

    def test_poner_clase_cambia_solo_el_primer_slide(self):
        html = '<div class="slide"><div class="slide">'
        self.assertEqual(build.poner_clase(html, "slide claro"), '<div class="slide claro"><div class="slide">')

    def test_fuentes_desde_el_comentario_de_marca(self):
        self.assertTrue(build.fuentes_de_marca(MARCA_CSS).startswith("https://fonts.googleapis.com/css2?family=Inter"))
        self.assertEqual(build.fuentes_de_marca(":root{}"), "")


class Construir(unittest.TestCase):
    def test_arma_los_slides_sin_pendientes_ni_marcas_de_css(self):
        with tempfile.TemporaryDirectory() as tmp:
            carpeta, marca = carrusel(tmp, CAMPOS_POR_FORMATO["tipografico"])
            archivos, avisos = build.construir(carpeta, marca, "instagram", PLANTILLAS)
            self.assertEqual([a.name for a in archivos], ["slide-01.html", "slide-02.html", "slide-03.html"])
            for a in archivos:
                html = a.read_text(encoding="utf-8")
                self.assertNotIn("{{", html)
                self.assertNotIn("/*==BASE==*/", html)
                self.assertIn("--acento:#123456", html)
                self.assertIn("@tu_marca", html)
            self.assertIn('class="slide claro"', archivos[1].read_text(encoding="utf-8"))
            self.assertEqual(avisos, [])

    def test_falla_si_queda_un_campo_sin_llenar(self):
        slides = [{"plantilla": "portada", "campos": {"GANCHO": "x"}}]
        with tempfile.TemporaryDirectory() as tmp:
            carpeta, marca = carrusel(tmp, slides)
            with self.assertRaises(build.ErrorDeCarrusel) as e:
                build.construir(carpeta, marca, "instagram", PLANTILLAS)
            self.assertIn("SUBTITULO", str(e.exception))
            self.assertFalse((carpeta / "slides").exists())

    def test_falla_con_mas_de_20_slides(self):
        slides = [CAMPOS_POR_FORMATO["tipografico"][0]] * 21
        with tempfile.TemporaryDirectory() as tmp:
            carpeta, marca = carrusel(tmp, slides)
            with self.assertRaises(build.ErrorDeCarrusel):
                build.construir(carpeta, marca, "instagram", PLANTILLAS)

    def test_molde_propio_con_raiz_y_aviso_de_imagen_faltante(self):
        with tempfile.TemporaryDirectory() as tmp:
            carpeta, marca = carrusel(tmp, [{"molde": "moldes/uno.html", "campos": {"T": "Hola"}}], formato=None)
            (carpeta / "moldes").mkdir()
            (carpeta / "moldes" / "uno.html").write_text(
                "<style>/*==MARCA==*/</style><p>{{T}}</p><img src=\"{{RAIZ}}/imagenes/no-esta.jpg\">", encoding="utf-8")
            archivos, avisos = build.construir(carpeta, marca, "instagram", PLANTILLAS)
            html = archivos[0].read_text(encoding="utf-8")
            self.assertIn("../imagenes/no-esta.jpg", html)
            self.assertEqual(len(avisos), 1)
            self.assertIn("no-esta.jpg", avisos[0])

    def test_imagen_que_si_esta_no_da_aviso_en_la_primera_corrida(self):
        slides = [{"plantilla": "portada", "campos": {"IMAGEN": "{{RAIZ}}/imagenes/a.jpg", "GANCHO": "g"}},
                  {"plantilla": "contenido", "campos": {"IMAGEN": "{{RAIZ}}/imagenes/a.jpg", "TITULO": "t", "TEXTO": "x"}},
                  {"plantilla": "cierre", "campos": {"IMAGEN": "{{RAIZ}}/imagenes/a.jpg", "TITULO": "t", "ACCION": "a",
                                                     "PALABRA": "P", "QUE_RECIBE": "q"}}]
        with tempfile.TemporaryDirectory() as tmp:
            carpeta, marca = carrusel(tmp, slides, formato="foto")
            (carpeta / "imagenes").mkdir()
            (carpeta / "imagenes" / "a.jpg").write_bytes(b"x")
            _, avisos = build.construir(carpeta, marca, "instagram", PLANTILLAS)
            self.assertEqual(avisos, [])

    def test_los_data_uri_del_limpio_no_cuentan_como_imagenes(self):
        slides = [{"plantilla": "portada", "campos": {"GANCHO": "g"}},
                  {"plantilla": "cierre", "campos": {"TITULO": "t", "ACCION": "a", "PALABRA": "P", "QUE_RECIBE": "q"}}]
        with tempfile.TemporaryDirectory() as tmp:
            carpeta, marca = carrusel(tmp, slides, formato="limpio")
            _, avisos = build.construir(carpeta, marca, "instagram", PLANTILLAS)
            self.assertEqual(avisos, [])

    def test_version_tiktok_cambia_handle_y_cierre_en_su_carpeta(self):
        tiktok = {"tiktok": {"campos_comunes": {"HANDLE": "@otra_marca"},
                             "cierre": {"plantilla": "cierre", "campos": {
                                 "TITULO": "Guárdalo", "ACCION": "Sígueme",
                                 "PALABRA": "GUARDA", "QUE_RECIBE": "para más"}}}}
        with tempfile.TemporaryDirectory() as tmp:
            carpeta, marca = carrusel(tmp, CAMPOS_POR_FORMATO["tipografico"], extra=tiktok)
            archivos, _ = build.construir(carpeta, marca, "tiktok", PLANTILLAS)
            self.assertEqual(archivos[0].parent, carpeta / "tiktok" / "slides")
            todo = "".join(a.read_text(encoding="utf-8") for a in archivos)
            self.assertIn("@otra_marca", todo)
            self.assertNotIn("@tu_marca", todo)
            self.assertIn("GUARDA", archivos[-1].read_text(encoding="utf-8"))

    def test_tiktok_sin_configuracion_es_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            carpeta, marca = carrusel(tmp, CAMPOS_POR_FORMATO["tipografico"])
            with self.assertRaises(build.ErrorDeCarrusel):
                build.construir(carpeta, marca, "tiktok", PLANTILLAS)

    def test_sin_marca_css_es_error_claro(self):
        with tempfile.TemporaryDirectory() as tmp:
            carpeta, _ = carrusel(tmp, CAMPOS_POR_FORMATO["tipografico"])
            with self.assertRaises(build.ErrorDeCarrusel) as e:
                build.construir(carpeta, Path(tmp) / "no-existe.css", "instagram", PLANTILLAS)
            self.assertIn("marca", str(e.exception))


class TodasLasPlantillas(unittest.TestCase):
    """Cada plantilla de la skill se llena sin dejar {{...}} cuando se dan sus campos."""

    def test_cada_plantilla_tiene_campos_conocidos_y_sin_paginacion(self):
        for html_file in sorted(PLANTILLAS.glob("*/*.html")):
            html = html_file.read_text(encoding="utf-8")
            with self.subTest(plantilla=str(html_file.relative_to(PLANTILLAS))):
                self.assertIn("/*==BASE==*/", html)
                self.assertNotIn('class="pag"', html)
                self.assertNotIn('class="desliza"', html)
                campos = {k: "x" for k in build.pendientes(html)}
                lleno = build.llenar(build.quitar_bloques(html, []), campos)
                self.assertEqual(build.pendientes(lleno), [])


class PlantillasCumplenSusReglas(unittest.TestCase):
    """Las plantillas no pueden contradecir las reglas de la skill."""

    def leer(self, ruta):
        return (PLANTILLAS / ruta).read_text(encoding="utf-8")

    def test_sin_kickers_en_ninguna_plantilla(self):
        for html_file in sorted(PLANTILLAS.glob("*/*.html")):
            html = html_file.read_text(encoding="utf-8")
            with self.subTest(plantilla=str(html_file.relative_to(PLANTILLAS))):
                for marca in ('class="etiqueta"', 'class="antes"', 'class="meta"', "{{ANTES_DE_IRTE}}", 'class="kicker"'):
                    self.assertNotIn(marca, html)

    def test_cada_cierre_trae_el_molde_del_recurso(self):
        for html_file in sorted(PLANTILLAS.glob("*/cierre.html")):
            html = html_file.read_text(encoding="utf-8")
            with self.subTest(plantilla=html_file.parent.name):
                self.assertIn("<!--?RECURSO-->", html)
                self.assertIn('class="recurso"', html)
                self.assertIn('class="sello"', html)

    def test_tuit_sin_negritas(self):
        for nombre in ("portada", "contenido", "cierre"):
            html = self.leer(f"tuit/{nombre}.html")
            with self.subTest(plantilla=nombre):
                self.assertNotIn(".post b{", html)
                self.assertNotIn("<b>", html)
                self.assertNotRegex(html, r"\.post[^{]*\{[^}]*font-weight:(7|8|9)00")

    def test_noticia_portada_foto_a_sangre_pildora_centrada_y_titular_sin_mayusculas_sostenidas(self):
        html = self.leer("noticia/portada.html")
        self.assertRegex(html, r"\.foto\{position:absolute;inset:0")
        self.assertRegex(html, r"\.barra\{[^}]*justify-content:center")
        self.assertNotRegex(html, r"\.titular\{[^}]*text-transform:uppercase")
        self.assertRegex(html, r"\.titular\{[^}]*text-align:center")


class LineaDeComandos(unittest.TestCase):
    def test_main_devuelve_1_y_no_lanza_con_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            carpeta, marca = carrusel(tmp, [{"plantilla": "portada", "campos": {}}])
            self.assertEqual(build.main([str(carpeta), "--marca", str(marca)]), 1)

    def test_main_ok(self):
        with tempfile.TemporaryDirectory() as tmp:
            carpeta, marca = carrusel(tmp, CAMPOS_POR_FORMATO["tipografico"])
            self.assertEqual(build.main([str(carpeta), "--marca", str(marca)]), 0)


if __name__ == "__main__":
    unittest.main()
