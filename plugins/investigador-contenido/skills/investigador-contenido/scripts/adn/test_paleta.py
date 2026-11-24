import json
import os
import subprocess
import sys
import tempfile
import unittest

import numpy as np

import hoja_paletas
import paleta

ROJO, NEGRO, PIEL = (200, 12, 21), (16, 14, 15), (196, 137, 113)


def pixeles(*colores_y_cantidades):
    return np.vstack([np.tile(np.array(c, dtype=float), (n, 1)) for c, n in colores_y_cantidades])


class PruebasPaleta(unittest.TestCase):
    def test_hex(self):
        self.assertEqual(paleta.hx((200, 12, 21.4)), '#C80C15')

    def test_kmeans_ordena_por_proporcion(self):
        centros, partes = paleta.kmeans(pixeles((NEGRO, 300), (ROJO, 100)), 2)
        self.assertEqual([paleta.hx(c) for c in centros], ['#100E0F', '#C80C15'])
        self.assertAlmostEqual(float(partes[0]), 0.75)

    def test_piel_no_cuenta_como_color_de_marca(self):
        self.assertTrue(paleta.es_piel(PIEL))
        self.assertFalse(paleta.es_piel(ROJO))
        self.assertFalse(paleta.es_piel(NEGRO))

    def test_resumen_con_dominantes_acentos_y_piel(self):
        r = paleta.resumir('cuenta', pixeles((NEGRO, 1200), (ROJO, 500), (PIEL, 300)), n_imagenes=3)
        self.assertEqual(r['handle'], 'cuenta')
        self.assertEqual(r['n_imgs'], 3)
        self.assertEqual(r['dominantes'][0][0], '#100E0F')
        self.assertIn('#C80C15', [c for c, _ in r['acentos']])
        self.assertNotIn('#C48971', [c for c, _ in r['acentos']])
        self.assertIn('#C48971', r['piel'])
        self.assertEqual(r['pixeles_saturados_pct'], 25.0)

    def test_sin_pixeles_saturados_no_inventa_acentos(self):
        r = paleta.resumir('gris', pixeles(((120, 120, 120), 500), ((240, 240, 240), 500)), n_imagenes=1)
        self.assertEqual(r['acentos'], [])

    def test_distancia_de_color_delta_e76(self):
        self.assertEqual(paleta.delta_e76('#C80C15', '#C80C15'), 0.0)
        self.assertLess(paleta.delta_e76('#CC1414', '#C80C15'), 5)
        self.assertGreater(paleta.delta_e76('#CC1414', '#2F4BFF'), 15)

    def test_linea_de_comandos_con_imagenes_reales(self):
        from PIL import Image
        d = tempfile.mkdtemp()
        ruta = os.path.join(d, 'portada.png')
        imagen = Image.new('RGB', (40, 40), NEGRO)
        imagen.paste(Image.new('RGB', (40, 15), ROJO), (0, 0))
        imagen.save(ruta)
        aqui = os.path.dirname(os.path.abspath(__file__))
        r = subprocess.run([sys.executable, os.path.join(aqui, 'paleta.py'), 'cuenta', ruta], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads(r.stdout)['dominantes'][0][0], '#100E0F')


class PruebasHoja(unittest.TestCase):
    def test_hoja_lado_a_lado_con_la_propia_al_final_y_choques(self):
        paletas = {'cuenta_a': {'handle': 'cuenta_a', 'n_imgs': 4, 'pixeles_saturados_pct': 12.0,
                                'dominantes': [['#100E0F', 60.0], ['#C80C15', 20.0]], 'acentos': [['#C80C15', 18.0]]}}
        propia = {'titulo': 'Mi marca', 'colores': [['#CC1414', 'rojo'], ['#2F4BFF', 'azul']]}
        html = hoja_paletas.pagina(paletas, {'cuenta_a': {'#C80C15': 'rojo de marca'}}, propia)
        self.assertIn('@cuenta_a', html)
        self.assertIn('rojo de marca', html)
        self.assertLess(html.index('@cuenta_a'), html.index('Mi marca'))
        choques = hoja_paletas.choques(paletas, propia)
        self.assertEqual(choques[0]['color'], '#CC1414')
        self.assertEqual(choques[0]['cercanos'][0][0], 'cuenta_a')
        self.assertEqual(choques[1]['cercanos'], [])


if __name__ == '__main__':
    unittest.main()
