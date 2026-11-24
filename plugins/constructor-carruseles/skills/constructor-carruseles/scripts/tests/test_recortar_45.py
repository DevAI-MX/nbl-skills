"""Pruebas de recortar_45.py. Correr desde scripts/: python3 -m unittest discover -s tests"""
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))
import recortar_45  # noqa: E402

try:
    from PIL import Image
except ImportError:
    Image = None


class Caja(unittest.TestCase):
    def test_imagen_cuadrada_recorta_los_lados(self):
        self.assertEqual(recortar_45.caja_45(1000, 1000), (100, 0, 900, 1000))

    def test_imagen_alta_recorta_arriba_y_abajo_segun_el_centro(self):
        self.assertEqual(recortar_45.caja_45(800, 2000), (0, 500, 800, 1500))
        self.assertEqual(recortar_45.caja_45(800, 2000, centro_y=0.0), (0, 0, 800, 1000))
        self.assertEqual(recortar_45.caja_45(800, 2000, centro_y=1.0), (0, 1000, 800, 2000))

    def test_ya_en_45_no_recorta(self):
        self.assertEqual(recortar_45.caja_45(1122, 1402), (0, 0, 1122, 1402))

    def test_centro_fuera_de_rango_es_error(self):
        with self.assertRaises(ValueError):
            recortar_45.caja_45(100, 100, centro_x=1.5)


@unittest.skipIf(Image is None, "Pillow no está instalado")
class Archivo(unittest.TestCase):
    def test_sale_en_2160x2700(self):
        with tempfile.TemporaryDirectory() as tmp:
            entrada, salida = Path(tmp) / "in.jpg", Path(tmp) / "out.png"
            Image.new("RGB", (1600, 900), "red").save(entrada)
            self.assertEqual(recortar_45.main([str(entrada), str(salida)]), 0)
            with Image.open(salida) as im:
                self.assertEqual(im.size, (2160, 2700))

    def test_archivo_que_no_existe_sale_1(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(recortar_45.main([str(Path(tmp) / "no.jpg"), str(Path(tmp) / "o.png")]), 1)


if __name__ == "__main__":
    unittest.main()
