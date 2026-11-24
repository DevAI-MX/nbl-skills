import os
import subprocess
import sys
import tempfile
import unittest

import progreso as pr


def pieza(url, vistas=200_000, seguidores=10_000, ratio=20.0, **extra):
    return {'cuenta': 'c', 'url': url, 'vistas': vistas, 'seguidores': seguidores, 'ratio': ratio, **extra}


class PruebasProgreso(unittest.TestCase):
    def setUp(self):
        self.p = pr.nuevo('marca personal', 'hombres 20-30', 20)

    def test_no_repite_cuentas_ni_busquedas_sin_importar_mayusculas(self):
        pr.marcar_cuenta(self.p, 'Cuenta', 'no_califica', motivo='máximo 50 mil vistas')
        pr.marcar_busqueda(self.p, 'Marca Personal')
        pr.marcar_busqueda(self.p, 'marca personal')
        self.assertTrue(pr.ya_visitada(self.p, 'cuenta'))
        self.assertEqual(self.p['busquedas'], ['marca personal'])
        with self.assertRaises(ValueError):
            pr.marcar_cuenta(self.p, 'x', 'quizas')

    def test_la_misma_url_entra_una_sola_vez(self):
        self.assertTrue(pr.agregar_pieza(self.p, pieza('https://www.instagram.com/c/reel/AB1/')))
        self.assertFalse(pr.agregar_pieza(self.p, pieza('https://www.instagram.com/c/reel/ab1?igsh=x')))
        self.assertEqual(len(self.p['piezas']), 1)

    def test_revisa_url_ratio_criterio_y_duplicados(self):
        self.p['piezas'] = [
            pieza('https://www.instagram.com/c/reel/OK/'),
            pieza('https://www.instagram.com/c/p/MAL/'),
            pieza('https://www.instagram.com/c/reel/RATIO/', ratio=55.9),
            pieza('https://www.instagram.com/c/reel/BAJO/', vistas=90_000, ratio=9.0),
            pieza('https://www.instagram.com/c/reel/RESCATE/', vistas=60_000, ratio=6.0, etiqueta='Nivel 2'),
            pieza('https://www.instagram.com/c/reel/OK/'),
            {'url': 'https://www.instagram.com/p/CARRUSEL/', 'formato': 'carrusel'},
        ]
        hallados = pr.problemas(self.p)
        self.assertEqual(len(hallados), 4)
        self.assertTrue(any('repetida' in h for h in hallados))
        self.assertTrue(any('/reel/' in h and 'MAL' in h for h in hallados))
        self.assertTrue(any('no cuadra' in h for h in hallados))
        self.assertTrue(any('BAJO' in h for h in hallados))

    def test_guarda_retoma_y_revisa_por_linea_de_comandos(self):
        ruta = os.path.join(tempfile.mkdtemp(), 'progreso.json')
        pr.agregar_pieza(self.p, pieza('https://www.instagram.com/c/reel/OK/'))
        pr.guardar(self.p, ruta)
        self.assertEqual(pr.cargar(ruta), self.p)
        aqui = os.path.dirname(os.path.abspath(__file__))
        r = subprocess.run([sys.executable, os.path.join(aqui, 'progreso.py'), ruta, 'revisar'], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn('sin problemas en 1 piezas', r.stdout)
        with self.assertRaises(FileNotFoundError):
            pr.cargar(ruta + '.no')


if __name__ == '__main__':
    unittest.main()
