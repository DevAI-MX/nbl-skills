import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from revisar_bio import revisar

SCRIPT = Path(__file__).with_name("revisar_bio.py")
BIO_BUENA = (
    "🎯 Te ayudo a llenar tu agenda con clientes que sí pagan\n"
    "🏆 +120 alumnos con su primera venta en 60 días\n"
    "👇 Empieza aquí\n"
    "tupagina.com/empieza"
)


def reglas(texto):
    return [falla.regla for falla in revisar(texto)]


class BioValida(unittest.TestCase):
    def test_bio_completa_no_tiene_fallas(self):
        self.assertEqual(reglas(BIO_BUENA), [])

    def test_link_con_https_tampoco_cuenta_como_linea(self):
        bio = BIO_BUENA.replace("tupagina.com/empieza", "https://tupagina.com/empieza?x=1")
        self.assertEqual(reglas(bio), [])

    def test_cta_por_mensaje_con_palabra_clave_pasa(self):
        bio = BIO_BUENA.replace("👇 Empieza aquí", "💬 DM VIDEO para empezar")
        self.assertEqual(reglas(bio), [])


class Estructura(unittest.TestCase):
    def test_bio_vacia_falla(self):
        self.assertEqual(reglas("  \n "), ["la bio está vacía"])

    def test_cuatro_lineas_exceden_el_maximo(self):
        bio = "🎯 Uno\n🏆 Dos\n👇 Tres\n🔥 Cuatro\ntupagina.com"
        self.assertIn("la bio tiene 4 líneas (máximo 3)", reglas(bio))

    def test_dos_lineas_fallan_porque_la_prueba_social_es_obligatoria(self):
        bio = "🎯 Te ayudo a vender\n👇 Empieza aquí\ntupagina.com"
        self.assertIn("faltan líneas: la bio lleva 3 (ayuda, prueba social e invitación)", reglas(bio))

    def test_exactamente_tres_lineas_no_exceden(self):
        bio = "🎯 Uno\n🏆 Dos\n👇 Tres\ntupagina.com"
        self.assertEqual(reglas(bio), [])

    def test_linea_sin_emoji_falla(self):
        bio = "Te ayudo a vender\n👇 Empieza aquí\ntupagina.com"
        self.assertIn("la línea no empieza con emoji", reglas(bio))

    def test_emoji_con_selector_de_variacion_o_keycap_cuentan(self):
        for emoji in ("⏰", "⬇️", "▶️", "1️⃣"):
            bio = f"{emoji} Te ayudo a vender en 30 días\n🏆 +40 clientes\n👇 Empieza aquí\ntupagina.com"
            self.assertEqual(reglas(bio), [], emoji)

    def test_un_numero_con_punto_no_cuenta_como_emoji(self):
        bio = "1. Te ayudo a vender\n🏆 +40 clientes\n👇 Empieza aquí\ntupagina.com"
        self.assertIn("la línea no empieza con emoji", reglas(bio))

    def test_una_flecha_simple_no_cuenta_como_emoji(self):
        bio = "↓ Empieza aquí\ntupagina.com"
        self.assertIn("la línea no empieza con emoji", reglas(bio))

    def test_sin_link_falla(self):
        self.assertIn("no hay link en la bio", reglas("🎯 Te ayudo a vender"))

    def test_formato_de_codigo_falla(self):
        bio = "```\n🎯 Te ayudo\n```\ntupagina.com"
        self.assertIn("la bio viene como código: debe ser texto plano", reglas(bio))


class Vocabulario(unittest.TestCase):
    def assert_prohibida(self, frase):
        bio = f"🎯 {frase}\n👇 Empieza aquí\ntupagina.com"
        self.assertTrue(any("prohibid" in regla for regla in reglas(bio)), frase)

    def test_palabras_gastadas(self):
        for frase in ("Te acompaño a crecer", "Mi proceso de 8 semanas", "Más ingresos para ti"):
            self.assert_prohibida(frase)

    def test_el_acento_no_salva_la_frase(self):
        self.assert_prohibida("Desbloquea tu potencial")
        self.assert_prohibida("Transforma tu vida")

    def test_cta_vago(self):
        self.assert_prohibida("Agenda tu llamada gratuita")
        self.assert_prohibida("Si te interesa, escríbeme")

    def test_llamada_gratis_en_cualquier_forma(self):
        self.assert_prohibida("Llamada gratuita aquí")
        self.assert_prohibida("Llamada gratis")

    def test_llamada_sin_costo_tambien_es_llamada_gratis(self):
        self.assert_prohibida("Agenda tu llamada sin costo")
        self.assert_prohibida("Primera llamada de 15 min sin costo")
        self.assert_prohibida("Sesión gratuita aquí")
        self.assert_prohibida("Consulta sin costo")
        self.assert_prohibida("Diagnóstico gratis")
        self.assert_prohibida("Diagnóstico gratuito")

    def test_regalar_un_recurso_gratis_si_se_vale(self):
        bio = "🎯 Te ayudo a vender\n🏆 +40 clientes\n🎁 Guía gratis aquí\ntupagina.com"
        self.assertEqual(reglas(bio), [])

    def test_procesador_no_es_proceso(self):
        bio = "🎯 Vendo procesadores usados\n🏆 +300 equipos vendidos\n👇 Empieza aquí\ntupagina.com"
        self.assertEqual(reglas(bio), [])


class SeguidoresComoPrueba(unittest.TestCase):
    REGLA = "seguidores usados como prueba"

    def bio_con(self, linea):
        return f"🎯 Te ayudo a vender\n🏆 {linea}\n👇 Empieza aquí\ntupagina.com"

    def test_cifra_de_seguidores_sola_falla(self):
        for linea in ("40 mil seguidores", "+40,000 seguidores", "40k seguidores", "Seguidores: 40.000"):
            self.assertIn(self.REGLA, reglas(self.bio_con(linea)), linea)

    def test_seguidores_junto_a_otra_metrica_real_tambien_falla(self):
        for linea in ("+15K seguidores y 40 clientes", "120 alumnos y 40 mil seguidores", "Tengo 15K de seguidores"):
            self.assertIn(self.REGLA, reglas(self.bio_con(linea)), linea)

    def test_seguidores_disfrazados_de_comunidad_o_familia_fallan(self):
        for linea in (
            "Comunidad de +15K",
            "Familia de 20k",
            "Una comunidad de más de 30 mil",
            "+15K followers",
            "15 mil personas me siguen",
            "Me siguen más de 15 mil",
            "+15K en IG",
        ):
            self.assertIn(self.REGLA, reglas(self.bio_con(linea)), linea)

    def test_comunidad_de_clientes_reales_no_es_seguidores(self):
        self.assertNotIn(self.REGLA, reglas(self.bio_con("Comunidad de 300 alumnos activos")))

    def test_seguidores_como_promesa_no_como_prueba_pasan(self):
        bio = "🎯 Te ayudo a llegar a tus primeros 10 mil seguidores\n🏆 +40 clientes\n👇 Empieza aquí\ntupagina.com"
        self.assertEqual(reglas(bio), [])

    def test_seguidores_ganados_por_sus_clientes_son_resultado(self):
        linea = "120 alumnos llevados a sus primeros 10k seguidores"
        self.assertNotIn(self.REGLA, reglas(self.bio_con(linea)))

    def test_seguidores_generados_para_clientes_son_prueba_valida(self):
        for linea in (
            "+2M de seguidores generados para mis clientes",
            "+500K seguidores generados",
            "1 millón de seguidores ganados por mis clientes",
            "Ayudé a 50 marcas a ganar 1M de seguidores",
            "Mis clientes han ganado +2M de seguidores",
        ):
            self.assertNotIn(self.REGLA, reglas(self.bio_con(linea)), linea)

    def test_crecimiento_propio_sigue_siendo_alcance_propio(self):
        self.assertIn(self.REGLA, reglas(self.bio_con("Logré ganar 15k seguidores en 3 meses")))

    def test_bio_completa_con_seguidores_generados_pasa(self):
        bio = BIO_BUENA.replace("🏆 +120 alumnos con su primera venta en 60 días", "🚀 +2M de seguidores generados para mis clientes")
        self.assertEqual(reglas(bio), [])


class OtrasCuentas(unittest.TestCase):
    REGLA = "menciona otra cuenta"

    def test_arroba_a_otra_cuenta_falla(self):
        bio = "🎯 Te ayudo a vender\n🏆 +40 clientes\n👉 Sígueme en @micuenta_2\ntupagina.com"
        self.assertTrue(any(self.REGLA in regla for regla in reglas(bio)))

    def test_correo_no_cuenta_como_otra_cuenta(self):
        bio = "🎯 Te ayudo a vender\n📩 hola@tupagina.com\ntupagina.com"  # vault:inventado
        self.assertFalse(any(self.REGLA in regla for regla in reglas(bio)))


class LineaDeComandos(unittest.TestCase):
    def correr(self, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args], capture_output=True, text=True, timeout=20, check=False
        )

    def archivo_con(self, contenido: bytes):
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as temporal:
            temporal.write(contenido)
        self.addCleanup(Path(temporal.name).unlink)
        return temporal.name

    def test_bio_limpia_sale_con_cero(self):
        resultado = self.correr(self.archivo_con(BIO_BUENA.encode()))
        self.assertEqual(resultado.returncode, 0)
        self.assertIn("sin fallas", resultado.stdout)

    def test_bio_con_fallas_sale_con_uno_y_cita_la_linea(self):
        resultado = self.correr(self.archivo_con("Te acompaño".encode()))
        self.assertEqual(resultado.returncode, 1)
        self.assertIn("Línea 1", resultado.stdout)

    def test_archivo_inexistente_sale_con_dos(self):
        resultado = self.correr("/no/existe.txt")
        self.assertEqual(resultado.returncode, 2)
        self.assertIn("No pude leer", resultado.stderr)

    def test_archivo_que_no_es_texto_sale_con_dos(self):
        resultado = self.correr(self.archivo_con(b"\xff\xfe\x00\x81"))
        self.assertEqual(resultado.returncode, 2)

    def test_guion_lee_la_bio_desde_la_entrada_estandar(self):
        resultado = subprocess.run(
            [sys.executable, str(SCRIPT), "-"], input=BIO_BUENA, capture_output=True, text=True, timeout=20, check=False
        )
        self.assertEqual(resultado.returncode, 0)
        self.assertIn("sin fallas", resultado.stdout)

    def test_sin_argumentos_sale_con_dos(self):
        self.assertEqual(self.correr().returncode, 2)


if __name__ == "__main__":
    unittest.main()
