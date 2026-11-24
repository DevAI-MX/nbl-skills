import csv
import os
import tempfile
import unittest

import denue


def negocio(nombre, municipio, codigo, actividad, personal):
    return {'nom_estab': nombre, 'raz_social': '', 'codigo_act': codigo, 'nombre_act': actividad, 'per_ocu': personal,
            'municipio': municipio, 'localidad': municipio, 'telefono': '', 'correoelec': '', 'www': ''}


FILAS = [
    negocio('TALLER UNO', 'Municipio Ejemplo', '811111', 'Reparación mecánica en general de automóviles y camiones', '6 a 10 personas'),
    negocio('TALLER DOS', 'Municipio Ejemplo', '811111', 'Reparación mecánica en general de automóviles y camiones', '0 a 5 personas'),
    negocio('CLIMAS TRES', 'Municipio Ejemplo', '811192', 'Otros servicios de reparación de automóviles', '31 a 50 personas'),
    negocio('TALLER OTRO', 'Otro Municipio', '811111', 'Reparación mecánica', '101 a 250 personas'),
    negocio('POLLERIA', 'Municipio Ejemplo', '461123', 'Comercio al por menor de carnes de aves', '11 a 30 personas'),
]


class PruebasDenue(unittest.TestCase):
    def test_rangos_de_personal_en_orden(self):
        self.assertEqual(denue.estrato('0 a 5 personas'), 0)
        self.assertEqual(denue.estrato('251 y mas personas'), 6)
        with self.assertRaises(ValueError):
            denue.estrato('mucha gente')

    def test_filtra_por_municipio_giro_y_tamano(self):
        r = denue.filtrar(FILAS, ['municipio ejemplo'], ['8111'], minimo='6 a 10 personas')
        self.assertEqual([f['nom_estab'] for f in r], ['CLIMAS TRES', 'TALLER UNO'])
        r = denue.filtrar(FILAS, actividad=r'mec[aá]nica', minimo='6 a 10 personas')
        self.assertEqual([f['nom_estab'] for f in r], ['TALLER OTRO', 'TALLER UNO'])

    def test_lee_latin1_y_escribe_utf8(self):
        d = tempfile.mkdtemp()
        entrada, salida = os.path.join(d, 'denue.csv'), os.path.join(d, 'salida.csv')
        with open(entrada, 'w', encoding='latin-1', newline='') as archivo:
            escritor = csv.DictWriter(archivo, fieldnames=list(FILAS[0]))
            escritor.writeheader()
            escritor.writerows(FILAS)
        self.assertEqual(denue.main([entrada, salida, '--municipio', 'Municipio Ejemplo', '--scian', '811']), 0)
        with open(salida, encoding='utf-8') as archivo:
            filas = list(csv.DictReader(archivo))
        self.assertEqual([f['nom_estab'] for f in filas], ['CLIMAS TRES', 'TALLER UNO'])
        self.assertIn('Reparación', filas[1]['nombre_act'])


if __name__ == '__main__':
    unittest.main()
