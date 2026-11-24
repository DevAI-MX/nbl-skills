#!/usr/bin/env python3
"""Carruseles de referencia por comentarios y likes, con sus láminas, para analizarlos lámina por lámina o rehacerlos.

Flujo: escanear el feed de las cuentas del nicho (ig/batchscan.mjs ... feed) -> pool de carruseles recientes ->
rangos por comentarios y por likes -> [subagentes: clasificación de nicho e idioma por caption] -> selección por grupo
-> fichas con sesión (ig/fichas-por-codigo.mjs) -> carpetas con datos.json y descarga de láminas a referencia/
-> [subagentes: ficha.md o analisis.md con el molde de references/carruseles-referencia.md].

  python3 carruseles.py pool <carpeta> <desde AAAA-MM-DD> <cuentas.json>   pool.json con rangos (lee los .feed.json)
  python3 carruseles.py top <carpeta> <n>                                  top_comentarios.json para clasificar
  python3 carruseles.py seleccionar <carpeta>                              seleccion.json con config.json y clasificacion_*.json
  python3 carruseles.py carpetas <carpeta> <seleccion.json> <fichas.json>  carpetas, datos.json y descargas.json
config.json: {"cuotas": {"<nicho>": {"en": 50, "pt": 30, "es": 20}}, "oficiales": [...], "previos": [códigos ya usados],
"fuerte": 60}. clasificacion_N.json (subagentes): [{"code", "nicho", "idioma", "excluir": [], "nota"}].
Los escaneos se buscan como en pasos.py: ESCANEOS_DIR (absoluta o relativa a la carpeta) o <carpeta>/escaneos.
"""
import collections
import datetime
import glob
import json
import os
import sys

from seleccion import fecha_de_publicacion

MAXIMO_POR_CUENTA = 3


def pool_de_escaneos(escaneos, desde):
    pool = []
    for escaneo in escaneos:
        for it in escaneo['items']:
            if it.get('type') != 'carousel_container' or not it.get('pk') or fecha_de_publicacion(it) < desde:
                continue
            pool.append({'code': it['code'], 'cuenta': escaneo['handle'], 'seguidores': escaneo.get('followers'),
                         'comentarios': it.get('comment_count') or 0, 'likes': it.get('like_count') or 0,
                         'fecha': fecha_de_publicacion(it).date().isoformat(), 'laminas': it.get('slides'),
                         'caption': it.get('caption') or '', 'enlace': f"https://www.instagram.com/p/{it['code']}/"})
    return pool


def con_rangos(pool):
    """Lugar por comentarios y por likes (1 = el más alto) y su promedio, que es el orden combinado."""
    salida = [dict(p) for p in pool]
    for campo, rango in (('comentarios', 'rank_com'), ('likes', 'rank_likes')):
        for lugar, p in enumerate(sorted(salida, key=lambda x: -x[campo]), 1):
            p[rango] = lugar
    for p in salida:
        p['score'] = (p['rank_com'] + p['rank_likes']) / 2
    return salida


def top_por_comentarios(pool, n):
    return sorted(pool, key=lambda p: p['rank_com'])[:n]


def seleccionar(pool, cuotas, oficiales=frozenset(), previos=frozenset(), fuerte=60, maximo_por_cuenta=MAXIMO_POR_CUENTA):
    """Por grupo (nicho, idioma) en orden combinado, con tope por cuenta y sin cuentas oficiales de marcas. Lo que ya
    salió antes solo entra si está entre los `fuerte` primeros por comentarios o por likes, y va marcado."""
    elegidos, faltan = [], {}
    for grupo, cupo in cuotas.items():
        por_cuenta, del_grupo = collections.Counter(), []
        for p in sorted((p for p in pool if (p['nicho'], p['idioma']) == grupo), key=lambda p: p['score']):
            es_fuerte = p['rank_com'] <= fuerte or p['rank_likes'] <= fuerte
            if p['cuenta'] in oficiales or (p['code'] in previos and not es_fuerte) or por_cuenta[p['cuenta']] >= maximo_por_cuenta:
                continue
            por_cuenta[p['cuenta']] += 1
            del_grupo.append({**p, 'repetido_fuerte': p['code'] in previos})
            if len(del_grupo) == cupo:
                break
        if len(del_grupo) < cupo:
            faltan[grupo] = cupo - len(del_grupo)
        elegidos += del_grupo
    return elegidos, faltan


def unir_clasificacion(pool, clasificaciones):
    """Solo las piezas clasificadas y sin exclusión, con su nicho e idioma."""
    por_codigo = {c['code']: c for c in clasificaciones}
    return [{**p, 'nicho': c['nicho'], 'idioma': c['idioma'], 'nota': c.get('nota', '')}
            for p in pool for c in [por_codigo.get(p['code'])] if c and not c.get('excluir')]


def seleccion_de_carpeta(carpeta):
    config = leer(os.path.join(carpeta, 'config.json'))
    clasificaciones = [c for ruta in sorted(glob.glob(os.path.join(carpeta, 'clasificacion_*.json'))) for c in leer(ruta)]
    pool = unir_clasificacion(leer(os.path.join(carpeta, 'pool.json')), clasificaciones)
    cuotas = {(nicho, idioma): cupo for nicho, por_idioma in config['cuotas'].items() for idioma, cupo in por_idioma.items()}
    return seleccionar(pool, cuotas, set(config.get('oficiales', [])), set(config.get('previos', [])), config.get('fuerte', 60))


def preparar_carpetas(seleccion, fichas, carpeta):
    """Una carpeta NN_fecha_cuenta_codigo/ por carrusel con datos.json; devuelve [[url, destino]] de cada lámina.
    Los que no tienen ficha van a faltan_laminas.json (se prueban con el lector público web/carrusel-publico.mjs)."""
    plan, faltan = [], []
    for posicion, p in enumerate(seleccion, 1):
        ficha = fichas.get(p['code'])
        if not ficha or ficha.get('error') or not ficha.get('partes'):
            faltan.append(p['code'])
            continue
        destino = os.path.join(carpeta, f"{posicion:02d}_{p['fecha']}_{p['cuenta']}_{p['code']}")
        os.makedirs(os.path.join(destino, 'referencia'), exist_ok=True)
        partes = []
        for n, parte in enumerate(ficha['partes'], 1):
            archivo = f'referencia/{n:02d}.jpg'
            partes.append({'lamina': n, 'tipo': 'video' if parte.get('media_type') == 2 else 'imagen', 'archivo': archivo})
            if parte.get('imagen'):
                plan.append([parte['imagen'], os.path.join(destino, archivo)])
        guardar(os.path.join(destino, 'datos.json'), {'posicion': posicion, **p, 'partes': partes})
    guardar(os.path.join(carpeta, 'faltan_laminas.json'), faltan)
    return plan


def guardar(ruta, datos):
    with open(ruta, 'w', encoding='utf-8') as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=1)


def leer(ruta):
    with open(ruta, encoding='utf-8') as archivo:
        return json.load(archivo)


def escaneos_feed(carpeta, cuentas):
    base = os.path.abspath(os.path.join(carpeta, os.environ.get('ESCANEOS_DIR') or 'escaneos'))
    for cuenta in cuentas:
        ruta = os.path.join(base, f'{cuenta}.feed.json')
        if os.path.exists(ruta):
            yield leer(ruta)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    orden = argv[0] if argv else ''
    if orden == 'pool' and len(argv) == 4:
        desde = datetime.datetime.fromisoformat(argv[2]).replace(tzinfo=datetime.timezone.utc)
        pool = con_rangos(pool_de_escaneos(escaneos_feed(argv[1], leer(argv[3])), desde))
        guardar(os.path.join(argv[1], 'pool.json'), pool)
        print(f'{len(pool)} carruseles en la ventana')
    elif orden == 'top' and len(argv) == 3:
        top = top_por_comentarios(leer(os.path.join(argv[1], 'pool.json')), int(argv[2]))
        guardar(os.path.join(argv[1], 'top_comentarios.json'), top)
        print(f'{len(top)} para clasificar')
    elif orden == 'seleccionar' and len(argv) == 2:
        elegidos, faltan = seleccion_de_carpeta(argv[1])
        guardar(os.path.join(argv[1], 'seleccion.json'), elegidos)
        print(f'{len(elegidos)} elegidos; faltan por grupo: {dict((f"{n}-{i}", c) for (n, i), c in faltan.items())}')
    elif orden == 'carpetas' and len(argv) == 4:
        plan = preparar_carpetas(leer(argv[2]), leer(argv[3]), argv[1])
        guardar(os.path.join(argv[1], 'descargas.json'), plan)
        print(f'{len(plan)} láminas por bajar: python3 guiones/medios.py plan {os.path.join(argv[1], "descargas.json")}')
    else:
        sys.exit(__doc__)
    return 0


if __name__ == '__main__':
    sys.exit(main())
