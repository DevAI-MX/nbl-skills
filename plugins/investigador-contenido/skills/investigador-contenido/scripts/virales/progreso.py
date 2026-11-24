#!/usr/bin/env python3
"""Progreso persistente de una investigación hecha a mano (cuenta por cuenta) y su revisión antes de entregar.

Sirve para no volver a visitar cuentas ni búsquedas entre sesiones y para no repetir piezas. Archivo JSON:
  {"nicho", "avatar", "meta", "busquedas": [...], "cuentas": {handle: {"estado": "califica"|"no_califica", ...}},
   "piezas": [{"cuenta", "seguidores", "vistas", "ratio", "url", "formato", ...}]}

Uso:
  python3 progreso.py <archivo> revisar     duplicados, URLs, ratios y criterio; sale con 1 si hay problemas
  python3 progreso.py <archivo> resumen     cuántas búsquedas, cuentas y piezas van (para el informe de límites)
"""
import json
import os
import sys

from seleccion import es_viral

TOLERANCIA_RATIO = 0.05


def nuevo(nicho, avatar, meta):
    return {'nicho': nicho, 'avatar': avatar, 'meta': meta, 'busquedas': [], 'cuentas': {}, 'piezas': []}


def cargar(ruta):
    if not os.path.exists(ruta):
        raise FileNotFoundError(f'no existe {ruta}: créalo con nuevo() y guardar()')
    with open(ruta, encoding='utf-8') as archivo:
        return json.load(archivo)


def guardar(progreso, ruta):
    temporal = ruta + '.tmp'
    with open(temporal, 'w', encoding='utf-8') as archivo:
        json.dump(progreso, archivo, ensure_ascii=False, indent=1)
    os.replace(temporal, ruta)


def ya_visitada(progreso, cuenta):
    return cuenta.lower() in progreso['cuentas']


def ya_buscada(progreso, busqueda):
    return busqueda.lower() in progreso['busquedas']


def marcar_busqueda(progreso, busqueda):
    if not ya_buscada(progreso, busqueda):
        progreso['busquedas'].append(busqueda.lower())


def marcar_cuenta(progreso, cuenta, estado, **datos):
    if estado not in ('califica', 'no_califica'):
        raise ValueError(f'estado desconocido: {estado}')
    progreso['cuentas'][cuenta.lower()] = {'estado': estado, **datos}


def clave(url):
    return url.split('?')[0].rstrip('/').lower()


def agregar_pieza(progreso, pieza):
    """Agrega la pieza si su URL no está ya. Devuelve False si era repetida."""
    if any(clave(p['url']) == clave(pieza['url']) for p in progreso['piezas']):
        return False
    progreso['piezas'].append(pieza)
    return True


def problemas(progreso):
    vistos, salida = set(), []
    for p in progreso['piezas']:
        url = clave(p['url'])
        if url in vistos:
            salida.append(f"URL repetida: {p['url']}")
        vistos.add(url)
        if p.get('formato', 'reel') == 'reel':
            salida += problemas_de_reel(p)
    return salida


def problemas_de_reel(p):
    salida = []
    if '/reel/' not in p['url']:
        salida.append(f"no es URL de reel (/reel/): {p['url']}")
    if not p.get('vistas') or not p.get('seguidores'):
        return salida + [f"sin vistas o sin seguidores: {p['url']}"]
    real = p['vistas'] / p['seguidores']
    if p.get('ratio') is not None and abs(real - p['ratio']) > TOLERANCIA_RATIO * max(real, 1):
        salida.append(f"ratio {p['ratio']} no cuadra con {p['vistas']}/{p['seguidores']} = {real:.1f}: {p['url']}")
    if not es_viral(p['vistas'], p['seguidores']) and not p.get('etiqueta'):
        salida.append(f"no cumple el criterio y no trae etiqueta de rescate: {p['url']}")
    return salida


def resumen(progreso):
    cuentas = progreso['cuentas'].values()
    return (f"{len(progreso['busquedas'])} búsquedas, {len(progreso['cuentas'])} cuentas revisadas "
            f"({sum(1 for c in cuentas if c['estado'] == 'califica')} con piezas), "
            f"{len(progreso['piezas'])} piezas de {progreso.get('meta')} buscadas")


def main():
    if len(sys.argv) != 3 or sys.argv[2] not in ('revisar', 'resumen'):
        sys.exit(__doc__)
    progreso = cargar(sys.argv[1])
    if sys.argv[2] == 'resumen':
        print(resumen(progreso))
        return
    hallados = problemas(progreso)
    print('\n'.join(hallados) if hallados else f"sin problemas en {len(progreso['piezas'])} piezas")
    sys.exit(1 if hallados else 0)


if __name__ == '__main__':
    main()
