#!/usr/bin/env python3
"""Filtra el DENUE de INEGI (directorio de negocios de México) para prospectar negocios locales que pueden pagar.

  python3 denue.py <denue.csv> <salida.csv> --municipio "Nombre" [--municipio ...] [--scian 8111 ...]
                   [--actividad REGEX] [--minimo "6 a 10 personas"]

El CSV masivo por estado viene en latin-1. El tamaño sale de per_ocu (rangos de personal ocupado) y el giro del código
SCIAN (codigo_act; --scian filtra por prefijo) o del nombre de la actividad (nombre_act). La salida va en UTF-8,
ordenada de más a menos personal, con el rango tal como lo publica INEGI. El personal ocupado es un rango, no ventas:
"puede pagar" es un supuesto que se marca como tal en el entregable.
"""
import argparse
import csv
import re
import sys
import unicodedata

ESTRATOS = ['0 a 5 personas', '6 a 10 personas', '11 a 30 personas', '31 a 50 personas', '51 a 100 personas',
            '101 a 250 personas', '251 y más personas']
COLUMNAS = ['nom_estab', 'raz_social', 'codigo_act', 'nombre_act', 'per_ocu', 'nom_vial', 'numero_ext', 'nomb_asent',
            'municipio', 'localidad', 'telefono', 'correoelec', 'www', 'latitud', 'longitud']


def normal(texto):
    sin_acentos = unicodedata.normalize('NFKD', texto or '').encode('ascii', 'ignore').decode()
    return re.sub(r'\s+', ' ', sin_acentos).strip().lower()


def estrato(per_ocu):
    """Posición del rango de personal (0 = 0 a 5 personas). Un rango desconocido es error: no se adivina."""
    for i, nombre in enumerate(ESTRATOS):
        if normal(nombre) == normal(per_ocu):
            return i
    raise ValueError(f'rango de personal desconocido: {per_ocu!r}')


def filtrar(filas, municipios=(), scian=(), actividad=None, minimo=ESTRATOS[0]):
    piso = estrato(minimo)
    municipios = {normal(m) for m in municipios}
    patron = re.compile(actividad, re.I) if actividad else None
    elegidas = [f for f in filas
                if (not municipios or normal(f['municipio']) in municipios)
                and (not scian or any(f['codigo_act'].startswith(s) for s in scian))
                and (not patron or patron.search(f['nombre_act']))
                and estrato(f['per_ocu']) >= piso]
    return sorted(elegidas, key=lambda f: -estrato(f['per_ocu']))


def leer(ruta, codificacion='latin-1'):
    with open(ruta, encoding=codificacion, newline='') as archivo:
        return list(csv.DictReader(archivo))


def escribir(filas, ruta):
    with open(ruta, 'w', encoding='utf-8', newline='') as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=COLUMNAS, extrasaction='ignore')
        escritor.writeheader()
        escritor.writerows(filas)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('denue')
    ap.add_argument('salida')
    ap.add_argument('--municipio', action='append', default=[])
    ap.add_argument('--scian', action='append', default=[])
    ap.add_argument('--actividad')
    ap.add_argument('--minimo', default=ESTRATOS[1], choices=ESTRATOS)
    ap.add_argument('--codificacion', default='latin-1')
    a = ap.parse_args(argv)
    filas = leer(a.denue, a.codificacion)
    elegidas = filtrar(filas, a.municipio, a.scian, a.actividad, a.minimo)
    escribir(elegidas, a.salida)
    conteo = {e: sum(1 for f in elegidas if f['per_ocu'] == e) for e in ESTRATOS if any(f['per_ocu'] == e for f in elegidas)}
    print(f'{len(elegidas)} de {len(filas)} negocios con {a.minimo} o más; por rango: {conteo}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
