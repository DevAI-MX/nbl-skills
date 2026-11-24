import datetime
import unittest

from seleccion import (carrusel_es_viral, carruseles_por_idioma, carruseles_virales, cascada_comentarios, elegir_por_cuota,
                       es_viral, es_viral_nivel_2, fecha_de_pk, fecha_de_publicacion, mediana_vistas_por_like, nivel,
                       reels_virales, tope_por_cuenta)

PK_CON_FECHA_CONOCIDA = '3963304110324151101'  # id de reel público con fecha conocida; no es teléfono (vault:inventado)
TAKEN_AT_CONOCIDO = 1786895789  # segundos unix, no es teléfono (vault:inventado)
ANTES = datetime.datetime(2026, 1, 1, tzinfo=datetime.timezone.utc)
DESPUES = datetime.datetime(2027, 1, 1, tzinfo=datetime.timezone.utc)


def escaneo(items, seguidores=10_000):
    return {'handle': 'cuenta', 'followers': seguidores, 'items': items}


def reel(vistas, likes=None, code='R'):
    return {'code': code, 'pk': PK_CON_FECHA_CONOCIDA, 'type': 'clips', 'play_count': vistas, 'like_count': likes}


class PruebasCriterio(unittest.TestCase):
    def test_cuenta_chica_necesita_diez_veces_sus_seguidores(self):
        self.assertTrue(es_viral(100_000, 10_000))
        self.assertFalse(es_viral(99_999, 10_000))

    def test_cuenta_grande_necesita_mas_de_un_millon(self):
        self.assertTrue(es_viral(1_000_001, 50_000))
        self.assertFalse(es_viral(1_000_000, 50_000))

    def test_carrusel_pasa_likes_a_vistas_con_la_equivalencia_dada(self):
        self.assertTrue(carrusel_es_viral(24_700, 300_000, 40.5))
        self.assertFalse(carrusel_es_viral(24_600, 300_000, 40.5))
        self.assertTrue(carrusel_es_viral(50_000, 300_000, 20.1))


class PruebasNiveles(unittest.TestCase):
    def test_nivel_s_a_y_b(self):
        self.assertEqual(nivel(1_500_000, 100_000), 'S')
        self.assertEqual(nivel(1_500_000, 200_000), 'A')
        self.assertEqual(nivel(400_000, 30_000), 'B')
        self.assertIsNone(nivel(200_000, 30_000))
        self.assertEqual(nivel(1_000_000, 100_000), 'B')

    def test_nivel_2_es_el_umbral_a_la_mitad(self):
        self.assertTrue(es_viral_nivel_2(50_000, 10_000))
        self.assertFalse(es_viral_nivel_2(49_999, 10_000))
        self.assertTrue(es_viral_nivel_2(500_001, 80_000))
        self.assertFalse(es_viral_nivel_2(500_000, 80_000))


class PruebasCascadaComentarios(unittest.TestCase):
    def pieza(self, code, comentarios):
        return {'code': code, 'comentarios': comentarios}

    def test_baja_de_escalon_solo_si_no_alcanza(self):
        piezas = [self.pieza('a', 1500), self.pieza('b', 800), self.pieza('c', 650), self.pieza('d', 90)]
        elegidas = cascada_comentarios(piezas, 3)
        self.assertEqual([(p['code'], p['escalon']) for p in elegidas], [('a', 1000), ('b', 700), ('c', 500)])

    def test_sin_cantidad_trae_el_maximo_posible_y_nunca_baja_de_100(self):
        piezas = [self.pieza('a', 101), self.pieza('b', 100), self.pieza('c', None)]
        self.assertEqual([p['code'] for p in cascada_comentarios(piezas)], ['a'])

    def test_dentro_de_un_escalon_ordena_de_mas_a_menos(self):
        piezas = [self.pieza('a', 1200), self.pieza('b', 3000)]
        self.assertEqual([p['code'] for p in cascada_comentarios(piezas, 1)], ['b'])


class PruebasFecha(unittest.TestCase):
    def test_fecha_del_identificador_es_la_de_subida_y_no_pasa_de_la_publicacion(self):
        real = datetime.datetime.fromtimestamp(TAKEN_AT_CONOCIDO, tz=datetime.timezone.utc)
        adelanto = real - fecha_de_pk(PK_CON_FECHA_CONOCIDA)
        self.assertGreaterEqual(adelanto, datetime.timedelta(0))
        self.assertLess(adelanto, datetime.timedelta(days=7))

    def test_usa_la_fecha_de_publicacion_cuando_existe(self):
        publicacion = {'pk': PK_CON_FECHA_CONOCIDA, 'taken_at': str(TAKEN_AT_CONOCIDO)}
        self.assertEqual(fecha_de_publicacion(publicacion).timestamp(), TAKEN_AT_CONOCIDO)


class PruebasEquivalencia(unittest.TestCase):
    def test_mediana_de_vistas_por_like_de_reels_recientes(self):
        items = [reel(1000, 10), reel(3000, 100), reel(4000, 100)]
        self.assertEqual(mediana_vistas_por_like([escaneo(items)], ANTES), (40.0, 3))

    def test_sin_reels_recientes_no_inventa_equivalencia(self):
        with self.assertRaises(ValueError):
            mediana_vistas_por_like([escaneo([reel(1000, 10)])], DESPUES)


class PruebasFiltro(unittest.TestCase):
    def test_reel_reciente_y_viral_entra_con_su_caption(self):
        [resultado] = reels_virales(escaneo([reel(200_000, code='X1')]), ANTES, {'X1': 'hola'})
        self.assertEqual((resultado['veces_seguidores'], resultado['caption'], resultado['alcance']), (20.0, 'hola', 200_000))

    def test_sin_vistas_en_el_payload_usa_el_contador_visible_y_marca_nivel(self):
        sin_payload = {**reel(None, code='X2'), 'vistas_visibles': 1_200_000}
        [resultado] = reels_virales(escaneo([sin_payload], seguidores=100_000), ANTES, {})
        self.assertEqual((resultado['vistas'], resultado['nivel']), (1_200_000, 'S'))

    def test_reel_viejo_sin_vistas_o_sin_seguidores_no_entra(self):
        self.assertEqual(reels_virales(escaneo([reel(200_000)]), DESPUES, {}), [])
        self.assertEqual(reels_virales(escaneo([reel(None)]), ANTES, {}), [])
        self.assertEqual(reels_virales(escaneo([reel(200_000)], seguidores=None), ANTES, {}), [])

    def test_carrusel_ignora_reels_y_estima_alcance_con_likes(self):
        carrusel = {'code': 'C', 'pk': PK_CON_FECHA_CONOCIDA, 'type': 'carousel_container', 'like_count': 3_000}
        [resultado] = carruseles_virales(escaneo([reel(9_000, 9_000), carrusel]), ANTES, 40.5)
        self.assertEqual((resultado['code'], resultado['alcance']), ('C', 121_500))


class PruebasCuota(unittest.TestCase):
    def pieza(self, cuenta, idioma, alcance):
        return {'cuenta': cuenta, 'idioma': idioma, 'alcance': alcance}

    def test_tope_por_cuenta_conserva_las_de_mas_alcance(self):
        piezas = [self.pieza('a', 'en', 5), self.pieza('a', 'en', 9), self.pieza('a', 'en', 7), self.pieza('b', 'en', 1)]
        self.assertEqual([p['alcance'] for p in tope_por_cuenta(piezas, 2)], [9, 7, 1])

    def test_cuota_en_orden_y_numerada(self):
        piezas = [self.pieza('a', 'es', 100), self.pieza('b', 'en', 1), self.pieza('c', 'pt', 2)]
        final = elegir_por_cuota(piezas, {'en': 1, 'pt': 1, 'es': 1}, 3)
        self.assertEqual([(p['n'], p['idioma']) for p in final], [(1, 'en'), (2, 'pt'), (3, 'es')])

    def test_si_un_idioma_no_alcanza_completa_el_primero(self):
        piezas = [self.pieza('a', 'en', 3), self.pieza('b', 'en', 2), self.pieza('c', 'en', 1)]
        final = elegir_por_cuota(piezas, {'en': 1, 'pt': 2}, 3)
        self.assertEqual(len(final), 3)

    def test_solo_el_primer_idioma_rellena_y_si_no_alcanza_la_lista_sale_corta(self):
        piezas = [self.pieza('a', 'en', 3), self.pieza('b', 'pt', 2), self.pieza('c', 'pt', 1)]
        final = elegir_por_cuota(piezas, {'en': 1, 'pt': 1, 'es': 2}, 3)
        self.assertEqual([p['cuenta'] for p in final], ['a', 'b'])


class PruebasNivelBSoloDeRelleno(unittest.TestCase):
    def pieza(self, cuenta, nivel, alcance):
        return {'cuenta': cuenta, 'idioma': 'en', 'nivel': nivel, 'alcance': alcance}

    def test_b_no_entra_si_s_y_a_llenan_la_cuota_aunque_tenga_mas_alcance(self):
        piezas = [self.pieza('a', 'B', 9_000_000), self.pieza('b', 'S', 2_000_000), self.pieza('c', 'A', 1_500_000)]
        final = elegir_por_cuota(piezas, {'en': 2}, 3)
        self.assertEqual([p['nivel'] for p in final], ['S', 'A'])

    def test_b_rellena_solo_lo_que_falta_y_queda_marcado(self):
        piezas = [self.pieza('a', 'B', 900_000), self.pieza('b', 'S', 2_000_000), self.pieza('c', 'B', 800_000)]
        final = elegir_por_cuota(piezas, {'en': 2}, 3)
        self.assertEqual([(p['nivel'], p['relleno_nivel_b']) for p in final], [('S', False), ('B', True)])

    def test_el_carrusel_lleva_su_nivel_calculado_con_el_alcance_estimado(self):
        carrusel = {'code': 'C', 'pk': PK_CON_FECHA_CONOCIDA, 'type': 'carousel_container', 'like_count': 3_000}
        [resultado] = carruseles_virales(escaneo([carrusel]), ANTES, 40.5)
        self.assertEqual(resultado['nivel'], 'B')


class PruebasCarruselesPorIdioma(unittest.TestCase):
    def carrusel(self, cuenta, idioma, likes, formato='carrusel'):
        return {'cuenta': cuenta, 'idioma': idioma, 'formato': formato, 'likes': likes, 'alcance': likes * 40}

    def test_agrupa_en_el_orden_pedido_y_de_mas_a_menos_likes(self):
        piezas = [self.carrusel('a', 'en', 9), self.carrusel('b', 'es', 1), self.carrusel('c', 'es', 5)]
        grupos = carruseles_por_idioma(piezas, ['es', 'en'], cupo=20, maximo_por_cuenta=2)
        self.assertEqual([(idioma, [c['likes'] for c in lista]) for idioma, lista in grupos],
                         [('es', [5, 1]), ('en', [9])])

    def test_respeta_cupo_tope_por_cuenta_e_ignora_reels(self):
        piezas = [self.carrusel('a', 'pt', n) for n in (9, 8, 7)] + [self.carrusel('b', 'pt', 6),
                                                                     self.carrusel('c', 'pt', 99, formato='reel')]
        [(_, lista)] = carruseles_por_idioma(piezas, ['pt'], cupo=2, maximo_por_cuenta=2)
        self.assertEqual([c['likes'] for c in lista], [9, 8])

    def test_idioma_sin_carruseles_queda_vacio(self):
        self.assertEqual(carruseles_por_idioma([], ['es'], cupo=5, maximo_por_cuenta=2), [('es', [])])


if __name__ == '__main__':
    unittest.main()
