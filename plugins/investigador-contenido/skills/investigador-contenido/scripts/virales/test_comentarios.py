import unittest

from comentarios import es_palabra_suelta, lectura


def c(texto):
    return {'u': 'x', 't': texto}


class PruebasComentarios(unittest.TestCase):
    def test_palabra_suelta(self):
        self.assertTrue(es_palabra_suelta('GUIA'))
        self.assertTrue(es_palabra_suelta('guía 🙌'))
        self.assertFalse(es_palabra_suelta('me pasó lo mismo a los 25'))
        self.assertFalse(es_palabra_suelta('🙌'))

    def test_mide_la_palabra_dominante_y_deja_la_conversacion(self):
        r = lectura([c('GUIA'), c('guia!'), c('Guia'), c('¿y si no tengo dinero para empezar?')], muestra=3)
        self.assertEqual((r['palabra_mas_repetida'], r['veces'], r['proporcion']), ('guia', 3, 0.75))
        self.assertEqual(r['muestra_conversacion'], ['¿y si no tengo dinero para empezar?'])

    def test_sin_comentarios(self):
        self.assertEqual(lectura([]), {'leidos': 0, 'palabra_mas_repetida': None, 'veces': 0, 'proporcion': 0.0,
                                       'muestra_conversacion': []})


if __name__ == '__main__':
    unittest.main()
