import json
import os
import tempfile
import types
import unittest
import unittest.mock

import medios
import transcribir as tr


class PruebasMedios(unittest.TestCase):
    fichas = {
        'C1': {'partes': [{'imagen': 'https://example.invalid/1.jpg', 'video': None},
                          {'imagen': 'https://example.invalid/2.jpg', 'video': 'https://example.invalid/2.mp4'}]},
        'MALO': {'error': 404},
        '../fuera': {'partes': [{'imagen': 'https://example.invalid/x.jpg'}]},
        'R1': {'partes': [{'imagen': None, 'video': 'https://example.invalid/r.mp4'}]},
    }

    def test_plan_por_lamina_y_salta_fichas_con_error_o_codigo_raro(self):
        plan = medios.plan_de_descargas(self.fichas, 'c')
        self.assertEqual(plan, [('https://example.invalid/1.jpg', os.path.join('c', 'C1', '01.jpg')),
                                ('https://example.invalid/2.jpg', os.path.join('c', 'C1', '02.jpg')),
                                ('https://example.invalid/2.mp4', os.path.join('c', 'C1', '02.mp4')),
                                ('https://example.invalid/r.mp4', os.path.join('c', 'R1', '01.mp4'))])
        self.assertEqual(len(medios.plan_de_descargas(self.fichas, 'c', 'imagenes')), 2)

    def test_baja_con_pausa_salta_lo_que_existe_y_reporta_fallos(self):
        d = tempfile.mkdtemp()
        existente = os.path.join(d, 'C1', '01.jpg')
        os.makedirs(os.path.dirname(existente))
        open(existente, 'w').close()
        plan = [('u1', existente), ('u2', os.path.join(d, 'C1', '02.jpg')), ('u3', os.path.join(d, 'C1', '03.jpg'))]
        llamadas, pausas = [], []
        ejecutar = lambda cmd, check: llamadas.append(cmd) or types.SimpleNamespace(returncode=0 if cmd[-1] == 'u2' else 22)
        hechos, fallos = medios.bajar(plan, 2.0, ejecutar, pausas.append)
        self.assertEqual((hechos, fallos, len(llamadas), pausas), (1, [os.path.join(d, 'C1', '03.jpg')], 2, [2.0, 2.0]))

    def test_plan_de_descargas_desde_archivo(self):
        d = tempfile.mkdtemp()
        lista = os.path.join(d, 'descargas.json')
        destino = os.path.join(d, 'x', 'referencia', '01.jpg')
        with open(lista, 'w') as archivo:
            json.dump([['https://example.invalid/1.jpg', destino]], archivo)
        llamadas = []
        falso = lambda cmd, check: llamadas.append(cmd) or types.SimpleNamespace(returncode=0)
        with unittest.mock.patch.object(medios.subprocess, 'run', falso), unittest.mock.patch.object(medios.time, 'sleep', lambda s: None):
            self.assertEqual(medios.main(['plan', lista, '--pausa', '0']), 0)
        self.assertEqual(llamadas[0][-3:], ['-o', destino, 'https://example.invalid/1.jpg'])

    def test_comandos_de_curl_y_hoja_de_cuadros(self):
        self.assertEqual(medios.comando_curl('u', 'd')[-3:], ['-o', 'd', 'u'])
        self.assertEqual(medios.comando_hoja('v.mp4', 'h.jpg')[-3:], ['-vf', 'fps=1,scale=320:-1,tile=6x6', 'h-%02d.jpg'])


class PruebasTranscribir(unittest.TestCase):
    def test_detecta_bucles(self):
        seg = lambda t: {'text': t, 'start': 0, 'end': 1}
        self.assertTrue(tr.posible_bucle([seg('hola'), seg(' Hola'), seg('hola ')]))
        self.assertFalse(tr.posible_bucle([seg('hola'), seg('adiós'), seg('hola')]))
        self.assertFalse(tr.posible_bucle([seg(''), seg(''), seg('')]))

    def test_lote_retoma_marca_sin_voz_y_no_se_detiene(self):
        def falso(video):
            if video.endswith('mudo.mp4'):
                raise RuntimeError('Failed to load audio: no stream')
            if video.endswith('roto.mp4'):
                raise ValueError('otro problema')
            return {'text': ' Hola ', 'segments': [{'start': 0.04, 'end': 1.26, 'text': ' Hola '}]}
        videos = ['/v/ya.mp4', '/v/nuevo.mp4', '/v/mudo.mp4', '/v/roto.mp4']
        *_, (_, salida) = tr.transcribir_lote(videos, {'ya.mp4': {'texto': 'previo'}}, falso)
        self.assertEqual(salida['ya.mp4'], {'texto': 'previo'})
        self.assertEqual(salida['nuevo.mp4'], {'texto': 'Hola', 'segmentos': [{'inicio': 0.0, 'fin': 1.3, 'texto': 'Hola'}],
                                               'posible_bucle': False})
        self.assertEqual(salida['mudo.mp4'], {'sin_voz': True})
        self.assertIn('otro problema', salida['roto.mp4']['error'])


if __name__ == '__main__':
    unittest.main()
