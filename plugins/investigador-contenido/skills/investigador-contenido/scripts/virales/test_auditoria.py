import json
import os
import tempfile
import unittest

import auditoria as au

PUBLICADO = 1780000000  # vault:inventado


def it(code, tipo, comentarios, likes, vistas=None, visibles=None, caption=None):
    return {'code': code, 'pk': '1', 'type': tipo, 'comment_count': comentarios, 'like_count': likes,
            'play_count': vistas, 'vistas_visibles': visibles, 'taken_at': PUBLICADO, 'caption': caption}


REELS = {'handle': 'cuenta', 'followers': 1000, 'items': [it('R1', 'clips', 50, 500, 90000), it('R2', 'clips', 5, 50, None, 1200),
                                                          it('R3', 'clips', 0, 10, 3000)]}
FEED = {'handle': 'cuenta', 'followers': 1000, 'items': [it('R1', 'clips', 50, 500, None, None, 'caption del reel'),
                                                         it('C1', 'carousel_container', 80, 300), it('F1', 'feed', 2, 40)]}


class PruebasAuditoria(unittest.TestCase):
    def setUp(self):
        self.items, self.solo_en_reels = au.unir(REELS, FEED)
        self.por_codigo = {i['code']: i for i in self.items}

    def test_une_por_codigo_sin_repetir_y_cuenta_los_que_solo_salen_en_reels(self):
        self.assertEqual(sorted(self.por_codigo), ['C1', 'F1', 'R1', 'R2', 'R3'])
        self.assertEqual(self.solo_en_reels, 2)
        self.assertEqual(self.por_codigo['R1']['vistas'], 90000)
        self.assertEqual(self.por_codigo['R1']['caption'], 'caption del reel')
        self.assertEqual(self.por_codigo['R2']['vistas'], 1200)
        self.assertEqual([self.por_codigo[c]['tipo'] for c in ('C1', 'F1', 'R1')], ['Carrusel', 'Imagen o video', 'Reel'])

    def test_rankings_por_comentarios_vistas_y_ratio(self):
        self.assertEqual([i['code'] for i in au.top(self.items, 'comentarios', 3)], ['C1', 'R1', 'R2'])
        self.assertEqual([i['code'] for i in au.top(self.items, 'vistas', 2)], ['R1', 'R3'])
        ratio = au.top(self.items, 'ratio', 3)
        self.assertEqual([i['code'] for i in ratio], ['R1', 'R2'])
        self.assertEqual(ratio[0]['ratio'], 1800.0)

    def test_documento_con_las_tres_vistas_y_el_aviso_de_reels(self):
        doc = au.documento('cuenta', 1000, self.items, self.solo_en_reels, 10)
        for titulo in ('## Ranking maestro por comentarios', '## Solo carruseles', '## Solo reels', '## Reels por vistas',
                       '## Reels por vistas entre comentarios'):
            self.assertIn(titulo, doc)
        self.assertIn('2 reels salieron solo en la pestaña /reels/', doc)
        self.assertIn('[abrir](https://www.instagram.com/p/C1/)', doc)

    def test_linea_de_comandos_lee_escaneos_y_escribe_el_documento(self):
        d = tempfile.mkdtemp()
        os.makedirs(os.path.join(d, 'escaneos'))
        for nombre, datos in (('cuenta.json', REELS), ('cuenta.feed.json', FEED)):
            with open(os.path.join(d, 'escaneos', nombre), 'w', encoding='utf-8') as archivo:
                json.dump(datos, archivo)
        salida = os.path.join(d, 'auditoria.md')
        self.assertEqual(au.main([d, 'cuenta', salida]), 0)
        with open(salida, encoding='utf-8') as archivo:
            self.assertIn('@cuenta', archivo.read())


if __name__ == '__main__':
    unittest.main()
