import datetime
import json
import os
import tempfile
import unittest

import carruseles as ca

PUBLICADO = 1780000000  # vault:inventado
DESDE = datetime.datetime(2026, 1, 1, tzinfo=datetime.timezone.utc)


def item(code, comentarios, likes, tipo='carousel_container', taken_at=PUBLICADO):
    return {'code': code, 'pk': '1', 'type': tipo, 'comment_count': comentarios, 'like_count': likes,
            'taken_at': taken_at, 'slides': 5, 'caption': f'caption {code}'}


def pieza(code, cuenta, com, likes, nicho='ia', idioma='en'):
    return {'code': code, 'cuenta': cuenta, 'comentarios': com, 'likes': likes, 'nicho': nicho, 'idioma': idioma}


class PruebasPool(unittest.TestCase):
    def test_solo_carruseles_recientes_del_feed_con_sus_cifras(self):
        escaneo = {'handle': 'c', 'followers': 900, 'items': [item('A', 50, 900), item('R', 9, 9, tipo='clips'),
                                                              item('V', 70, 70, taken_at=1700000000)]}  # vault:inventado
        pool = ca.pool_de_escaneos([escaneo], DESDE)
        self.assertEqual([(p['code'], p['cuenta'], p['comentarios'], p['likes'], p['laminas']) for p in pool],
                         [('A', 'c', 50, 900, 5)])
        self.assertEqual(pool[0]['enlace'], 'https://www.instagram.com/p/A/')


class PruebasRangos(unittest.TestCase):
    def test_rango_por_comentarios_por_likes_y_combinado(self):
        pool = ca.con_rangos([pieza('a', 'x', 100, 10), pieza('b', 'y', 50, 500), pieza('c', 'z', 10, 50)])
        por_codigo = {p['code']: p for p in pool}
        self.assertEqual((por_codigo['a']['rank_com'], por_codigo['a']['rank_likes']), (1, 3))
        self.assertEqual(por_codigo['b']['score'], 1.5)
        self.assertEqual(ca.top_por_comentarios(pool, 2), [por_codigo['a'], por_codigo['b']])


class PruebasSeleccion(unittest.TestCase):
    def test_cuota_por_grupo_tope_por_cuenta_oficiales_y_repetidos(self):
        pool = ca.con_rangos([pieza('a1', 'a', 900, 900), pieza('a2', 'a', 800, 800), pieza('a3', 'a', 700, 700),
                              pieza('a4', 'a', 600, 600), pieza('o1', 'openai', 999, 999), pieza('p1', 'p', 500, 500),
                              pieza('q1', 'q', 1, 1)])
        sel, faltan = ca.seleccionar(pool, {('ia', 'en'): 5}, oficiales={'openai'}, previos={'p1', 'a1'}, fuerte=2)
        self.assertEqual([p['code'] for p in sel], ['a1', 'a2', 'a3', 'q1'])
        self.assertTrue(sel[0]['repetido_fuerte'])
        self.assertEqual(faltan, {('ia', 'en'): 1})


class PruebasClasificacionYConfig(unittest.TestCase):
    def test_une_la_clasificacion_y_quita_excluidas_y_sin_clasificar(self):
        pool = [{'code': 'a'}, {'code': 'b'}, {'code': 'c'}]
        clas = [{'code': 'a', 'nicho': 'ia', 'idioma': 'en', 'excluir': []},
                {'code': 'b', 'nicho': 'ia', 'idioma': 'es', 'excluir': ['humor o meme']}]
        self.assertEqual(ca.unir_clasificacion(pool, clas), [{'code': 'a', 'nicho': 'ia', 'idioma': 'en', 'nota': ''}])

    def test_seleccion_por_linea_de_comandos(self):
        d = tempfile.mkdtemp()
        ca.guardar(os.path.join(d, 'pool.json'), ca.con_rangos([pieza('a', 'x', 9, 9), pieza('b', 'y', 5, 5)]))
        ca.guardar(os.path.join(d, 'clasificacion_1.json'), [{'code': 'a', 'nicho': 'ia', 'idioma': 'en', 'excluir': []},
                                                            {'code': 'b', 'nicho': 'ia', 'idioma': 'en', 'excluir': []}])
        ca.guardar(os.path.join(d, 'config.json'), {'cuotas': {'ia': {'en': 1}}, 'oficiales': [], 'previos': [], 'fuerte': 60})
        ca.main(['seleccionar', d])
        self.assertEqual([p['code'] for p in ca.leer(os.path.join(d, 'seleccion.json'))], ['a'])


class PruebasCarpetas(unittest.TestCase):
    def test_arma_datos_json_y_el_plan_de_descargas_de_cada_lamina(self):
        d = tempfile.mkdtemp()
        sel = [{**pieza('A', 'cuenta', 10, 20), 'fecha': '2026-11-12', 'laminas': 2, 'caption': 'x',
                'enlace': 'https://www.instagram.com/p/A/'}]
        fichas = {'A': {'partes': [{'media_type': 1, 'imagen': 'https://example.invalid/1.jpg'},
                                   {'media_type': 2, 'imagen': 'https://example.invalid/2.jpg', 'video': 'v'}]}}
        plan = ca.preparar_carpetas(sel, fichas, d)
        carpeta = os.path.join(d, '01_2026-11-12_cuenta_A')
        with open(os.path.join(carpeta, 'datos.json'), encoding='utf-8') as archivo:
            datos = json.load(archivo)
        self.assertEqual(datos['posicion'], 1)
        self.assertEqual(datos['partes'][1], {'lamina': 2, 'tipo': 'video', 'archivo': 'referencia/02.jpg'})
        self.assertEqual(plan[0], ['https://example.invalid/1.jpg', os.path.join(carpeta, 'referencia', '01.jpg')])

    def test_sin_ficha_queda_en_la_lista_de_faltantes(self):
        d = tempfile.mkdtemp()
        sel = [{**pieza('B', 'cuenta', 1, 1), 'fecha': '2026-11-01', 'laminas': 3, 'caption': '', 'enlace': 'e'}]
        self.assertEqual(ca.preparar_carpetas(sel, {}, d), [])
        with open(os.path.join(d, 'faltan_laminas.json'), encoding='utf-8') as archivo:
            self.assertEqual(json.load(archivo), ['B'])


if __name__ == '__main__':
    unittest.main()
