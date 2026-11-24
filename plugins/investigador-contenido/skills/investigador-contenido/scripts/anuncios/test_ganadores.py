import csv
import json
import os
import tempfile
import unittest

import ganadores as g

DIA = 86400
HOY = 1790000000  # segundos unix fijos para la prueba; vault:inventado


def anuncio(id_, pagina, copy, dias, versiones=1, rank=1, activo=True, inicio=None, plataformas=('facebook',)):
    inicio = inicio if inicio is not None else HOY - dias * DIA
    return {'ad_archive_id': id_, 'page_id': pagina, 'page_name': f'Página {pagina}', 'rank': rank, 'is_active': activo,
            'start_date': inicio, 'end_date': None if activo else inicio + dias * DIA, 'collation_count': versiones,
            'publisher_platform': list(plataformas), 'snapshot': {'body': {'text': copy}, 'cta_text': 'Más información'}}


def carpeta_con(anuncios, consulta='kw_prueba'):
    d = tempfile.mkdtemp()
    with open(os.path.join(d, f'{consulta}.json'), 'w', encoding='utf-8') as archivo:
        json.dump({'consulta': {'id': consulta}, 'anuncios': anuncios}, archivo)
    return d


class PruebasNivel(unittest.TestCase):
    def test_reglas_de_nivel(self):
        self.assertEqual(g.nivel(45, 3, 1), 'Ganador fuerte')
        self.assertEqual(g.nivel(30, 1, 2), 'Ganador fuerte')
        self.assertEqual(g.nivel(12, 6, 1), 'Ganador de lanzamiento')
        self.assertEqual(g.nivel(12, 1, 3), 'Ganador de lanzamiento')
        self.assertEqual(g.nivel(40, 1, 1), 'Probable')
        self.assertEqual(g.nivel(None, 4, 2), 'Probable')

    def test_calificacion_con_los_pesos_documentados(self):
        self.assertEqual(g.calificacion(60, 16, 0.0, 5, 2), 100.0)
        self.assertEqual(g.calificacion(30, 1, 1.0, 1, 1), 20.0)
        self.assertEqual(g.calificacion(None, 4, 0.5, 1, 1), 22.5)


class PruebasCalificar(unittest.TestCase):
    def test_relanzamiento_reuso_representante_y_filtro(self):
        relanzado_1 = anuncio('1', 'p1', 'Clase gratis de anuncios', 20, inicio=HOY - 90 * DIA, activo=False)
        relanzado_2 = anuncio('2', 'p1', 'Clase  gratis de ANUNCIOS', 35, versiones=2, rank=2)
        escalado = anuncio('3', 'p2', 'Reto de 5 días', 10, versiones=6, rank=3, plataformas=('facebook', 'instagram'))
        fuera = anuncio('4', 'p3', 'Vendo camioneta', 50, rank=4)
        r = g.calificar([carpeta_con([relanzado_1, relanzado_2, escalado, fuera])], filtros=[r'clase|reto'], hoy=HOY)
        self.assertEqual((r['total_anuncios'], r['pasan_filtro']), (4, 3))
        ids = [f['ad_archive_id'] for f in r['candidatos']]
        self.assertEqual(ids, ['2', '3'])
        primero = r['candidatos'][0]
        self.assertEqual((primero['nivel'], primero['lanzamientos_distintos_del_copy'], primero['reuso_mismo_copy']),
                         ('Ganador fuerte', 2, 2))
        self.assertEqual(r['candidatos'][1]['nivel'], 'Ganador de lanzamiento')

    def test_inventario_cuenta_activos_por_pagina(self):
        lista = [anuncio(str(i), 'lote', f'Unidad {i} con precio', 10, rank=i + 1) for i in range(4)]
        lista.append(anuncio('9', 'viejo', 'Presencia', 200, rank=9))
        lista.append(anuncio('8', 'lote', 'Unidad vendida', 5, activo=False, rank=8))
        r = g.calificar([carpeta_con(lista)], hoy=HOY)
        self.assertEqual(r['paginas'][0], {'anunciante': 'Página lote', 'page_id': 'lote', 'activos': 4})

    def test_mismo_anuncio_en_dos_busquedas_guarda_ambas_y_su_mejor_posicion(self):
        a = anuncio('1', 'p', 'x', 10, rank=3)
        b = dict(a, rank=1)
        otro = [anuncio(str(i), 'q', f'c{i}', 1, rank=i) for i in range(2, 5)]
        r = g.calificar([carpeta_con([a] + otro, 'kw_a'), carpeta_con([b], 'kw_b')], hoy=HOY)
        uno = next(f for f in r['candidatos'] if f['ad_archive_id'] == '1')
        self.assertEqual((uno['busquedas'], uno['rank_pct_en_busqueda']), (['kw_a', 'kw_b'], 0.0))

    def test_linea_de_comandos_escribe_json_y_csv(self):
        d = carpeta_con([anuncio('1', 'p', 'Clase', 40, versiones=3)])
        salida, tabla = os.path.join(d, 'g.json'), os.path.join(d, 'g.csv')
        g.main([d, '--salida', salida, '--csv', tabla, '--top', '5'])
        with open(salida, encoding='utf-8') as archivo:
            self.assertEqual(json.load(archivo)['candidatos'][0]['nivel'], 'Ganador fuerte')
        with open(tabla, encoding='utf-8') as archivo:
            filas = list(csv.DictReader(archivo))
        self.assertEqual((filas[0]['nivel'], filas[0]['versiones']), ('Ganador fuerte', '3'))


if __name__ == '__main__':
    unittest.main()
