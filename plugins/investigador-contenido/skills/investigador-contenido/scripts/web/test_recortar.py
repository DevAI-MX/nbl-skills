import os
import tempfile
import unittest

from recortar import recortar_carpeta, tramos


class RecorteFalso:
    def __init__(self, caja, guardadas):
        self.caja, self.guardadas = caja, guardadas

    def save(self, ruta, quality):
        open(ruta, 'w').close()
        self.guardadas.append((os.path.basename(ruta), self.caja))


class ImagenFalsa:
    def __init__(self, ancho, alto, guardadas):
        self.size, self.guardadas = (ancho, alto), guardadas

    def convert(self, _modo):
        return self

    def crop(self, caja):
        return RecorteFalso(caja, self.guardadas)


class PruebasRecortar(unittest.TestCase):
    def test_tramos_exactos_y_ultimo_corto(self):
        self.assertEqual(tramos(4000, 1800, 18), ([(0, 1800), (1800, 3600), (3600, 4000)], False))
        self.assertEqual(tramos(1800, 1800, 18), ([(0, 1800)], False))

    def test_pagina_larguisima_queda_recortada(self):
        cortes, recortada = tramos(10_000, 1000, 3)
        self.assertEqual((len(cortes), recortada), (3, True))

    def test_recorta_cada_landing_una_sola_vez(self):
        base = tempfile.mkdtemp()
        os.makedirs(os.path.join(base, 'landing_a'))
        open(os.path.join(base, 'landing_a', 'shot.png'), 'w').close()
        guardadas = []
        hechas = recortar_carpeta(base, lambda _ruta: ImagenFalsa(390, 2000, guardadas))
        self.assertEqual(hechas, [('landing_a', 2, False)])
        self.assertEqual(guardadas, [('shot_01.jpg', (0, 0, 390, 1800)), ('shot_02.jpg', (0, 1800, 390, 2000))])
        with open(os.path.join(base, 'landing_a', 'tramos.txt'), encoding='utf-8') as archivo:
            self.assertIn('2 tramos', archivo.read())
        self.assertEqual(recortar_carpeta(base, lambda _ruta: ImagenFalsa(390, 2000, guardadas)), [])


if __name__ == '__main__':
    unittest.main()
