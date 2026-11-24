"""Corre la investigación completa de pasos.py sobre datos inventados, sin red: de la búsqueda al documento."""
import contextlib
import io
import json
import os
import subprocess
import tempfile
import unittest
import unittest.mock

import pasos

PUBLICADO = 1780000000  # segundos unix dentro de la ventana; vault:inventado


def escribir(carpeta, nombre, datos):
    ruta = os.path.join(carpeta, nombre)
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, 'w', encoding='utf-8') as archivo:
        json.dump(datos, archivo, ensure_ascii=False)


def leer(carpeta, nombre):
    with open(os.path.join(carpeta, nombre), encoding='utf-8') as archivo:
        return json.load(archivo)


def medio(code, usuario, tipo, likes, caption=''):
    return {'code': code, 'pk': '1', 'media_type': tipo, 'user': usuario, 'likes': likes, 'taken_at': PUBLICADO,
            'caption': caption}


def reel(code, vistas, likes):
    return {'code': code, 'pk': '1', 'type': 'clips', 'play_count': vistas, 'like_count': likes,
            'comment_count': 10, 'taken_at': PUBLICADO, 'thumb': None}


class PruebaDePuntaAPunta(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        escribir(self.dir, 'config.json', {
            'titulo': 'Virales de prueba', 'subtitulo': 'Datos inventados', 'desde': '2026-01-01',
            'min_likes_video': 100, 'min_likes_carrusel': 100, 'cuotas': {'en': 1, 'es': 1}, 'max_por_cuenta': 3,
            'salida_md': 'salida/doc.md', 'carpeta_portadas': 'salida/portadas',
            'excluidas_a_mano': {'cuentas': [], 'codes': ['A2']}, 'grupos': [['Ganchos', 'gancho']]})
        escribir(self.dir, 'serp.json', {'done': {'ganchos': 3}, 'media': {
            'A1': medio('A1', 'cuenta_a', 2, 4000, 'Tres ganchos que retienen'),
            'B1': medio('B1', 'cuenta_b', 2, 40000, 'Ganchos en español'),
            'C1': medio('C1', 'cuenta_c', 8, 5000, 'Carrusel de ganchos'),
            'Z1': medio('Z1', 'cuenta_z', 2, 50)}})
        escribir(self.dir, 'escaneos/cuenta_a.json', {'handle': 'cuenta_a', 'followers': 10000, 'header_text': 'bio a',
                                                      'items': [reel('A1', 200000, 4000), reel('A2', 150000, 3000)]})
        escribir(self.dir, 'escaneos/cuenta_b.json', {'handle': 'cuenta_b', 'followers': 80000, 'header_text': 'bio b',
                                                      'items': [reel('B1', 2000000, 40000)]})
        carrusel = {'code': 'C1', 'pk': '1', 'type': 'carousel_container', 'like_count': 5000, 'comment_count': 40,
                    'taken_at': PUBLICADO, 'caption': 'Carrusel de ganchos', 'slides': 8, 'thumb': None}
        escribir(self.dir, 'escaneos/cuenta_c.feed.json', {'handle': 'cuenta_c', 'followers': 20000, 'header_text': 'bio c',
                                                           'items': [carrusel]})

    def paso(self, nombre):
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida):
            pasos.PASOS[nombre](pasos.Investigacion(self.dir))
        return salida.getvalue()

    def clasificar_pool(self):
        for n in range(1, pasos.LOTES + 1):
            lote = leer(self.dir, f'lote_{n}.json')
            escribir(self.dir, f'clasificacion_lote_{n}.json', [{
                'id': str(p['id']), 'idioma': p['idioma'], 'en_nicho': True, 'excluir': [], 'tema': 'Ganchos y retención',
                'gancho_portada': f"PORTADA {p['code']}", 'gancho_caption': '', 'de_que_trata': 'Enseña ganchos.',
                'formato_visual': 'Creador a cámara', 'mercado': 'EE. UU.' if p['idioma'] == 'en' else ''} for p in lote])

    def test_de_la_busqueda_al_documento(self):
        self.assertIn('2 cuentas de reels y 1 de carruseles', self.paso('listas'))
        self.assertEqual(sorted(leer(self.dir, 'cuentas_a.json') + leer(self.dir, 'cuentas_b.json')), ['cuenta_a', 'cuenta_b'])
        self.assertEqual(leer(self.dir, 'carruseles_a.json'), ['cuenta_c'])

        self.assertIn('50.0 vistas por like', self.paso('candidatos'))
        candidatos = {c['code']: c for c in leer(self.dir, 'candidatos.json')}
        self.assertEqual(set(candidatos), {'A1', 'A2', 'B1', 'C1'})
        self.assertEqual(candidatos['C1']['alcance'], 250000)
        self.assertEqual(candidatos['B1']['nivel'], 'S')

        self.paso('cuentas')
        self.assertEqual(leer(self.dir, 'cuentas_para_clasificar.json')[0]['bio'], 'bio a')
        escribir(self.dir, 'clasificacion_cuentas.json', [
            {'cuenta': 'cuenta_a', 'nicho': 'si', 'idioma': 'en', 'excluir_por': []},
            {'cuenta': 'cuenta_b', 'nicho': 'si', 'idioma': 'es', 'excluir_por': []},
            {'cuenta': 'cuenta_c', 'nicho': 'mixto', 'idioma': 'en', 'excluir_por': []}])

        self.paso('faltantes')
        self.assertEqual(leer(self.dir, 'pks_sin_caption.json'), ['1'])
        self.paso('pool')
        self.clasificar_pool()

        self.paso('elegibles')
        self.assertNotIn('A2', [p['code'] for p in leer(self.dir, 'elegibles.json')])
        self.paso('final')
        self.assertEqual([(p['n'], p['code']) for p in leer(self.dir, 'final.json')], [(1, 'C1'), (2, 'B1')])
        self.assertIn('Ganchos: 2 piezas', self.paso('tendencias'))

        with open(os.path.join(self.dir, 'tendencias_texto.md'), 'w', encoding='utf-8') as archivo:
            archivo.write('## Tendencias\nTexto.')
        with open(os.path.join(self.dir, 'metodo.md'), 'w', encoding='utf-8') as archivo:
            archivo.write('## Método y límites\nTexto.')
        self.paso('documento')
        with open(os.path.join(self.dir, 'salida/doc.md'), encoding='utf-8') as archivo:
            documento = archivo.read()
        self.assertIn('| # | Cuenta | Seguidores | Mercado | Idioma |', documento)
        self.assertIn('| 1 | @cuenta_c | 20,000 | EE. UU. | Inglés | carrusel |', documento)
        self.assertIn('| 2 | @cuenta_b | 80,000 | no visible | Español | reel | 2,000,000 vistas | 25.0x (nivel S) |', documento)
        self.assertIn('## Aparte: los 12 carruseles con más likes de cada idioma', documento)
        self.assertIn('## Método y límites', documento)


class PruebaCarpetaDeEscaneos(unittest.TestCase):
    """pasos.py y los recolectores de Node deben leer y escribir los escaneos en la MISMA carpeta."""
    AQUI = os.path.dirname(os.path.abspath(__file__))

    def carpeta_en_node(self, carpeta, entorno):
        codigo = ("import('" + os.path.join(self.AQUI, '..', 'ig', 'config.mjs') + "').then(m => "
                  "console.log(m.carpetaEscaneos(process.env, m.carpetaDeLaCorrida(process.argv[1]))))")
        r = subprocess.run(['node', '-e', codigo, os.path.join(carpeta, 'cuentas_a.json')], capture_output=True,
                           text=True, env={**os.environ, **entorno}, cwd=tempfile.mkdtemp(), check=True)
        return r.stdout.strip()

    def carpeta_en_pasos(self, carpeta, entorno):
        escribir(carpeta, 'config.json', {'desde': '2026-01-01'})
        with unittest.mock.patch.dict(os.environ, entorno):
            return pasos.Investigacion(carpeta).carpeta_escaneos

    def test_misma_carpeta_por_omision_y_con_ruta_relativa(self):
        for entorno in ({}, {'ESCANEOS_DIR': '../escaneos_comunes'}, {'ESCANEOS_DIR': '/tmp/escaneos_fijos'}):
            carpeta = tempfile.mkdtemp()
            sin_entorno = {k: v for k, v in os.environ.items() if k != 'ESCANEOS_DIR'}
            with unittest.mock.patch.dict(os.environ, sin_entorno, clear=True):
                self.assertEqual(os.path.realpath(self.carpeta_en_pasos(carpeta, entorno)),
                                 os.path.realpath(self.carpeta_en_node(carpeta, entorno)), entorno)


if __name__ == '__main__':
    unittest.main()
