#!/usr/bin/env python3
"""Califica los anuncios que bajó adlib.mjs con las señales públicas de la Biblioteca de anuncios de Meta.

Uso: python3 ganadores.py <carpeta_adlib> [<otra> ...] --salida ganadores.json [--top 150] [--filtro REGEX ...] [--csv lista.csv]

Señales públicas (lo único que Meta muestra de anuncios comerciales fuera de la UE; no hay gasto, impresiones
exactas, alcance ni clics):
- dias: días en circulación, de start_date al último día visto.
- versiones: collation_count, anuncios con el mismo contenido corriendo a la vez (duplicado en conjuntos = escalado).
- reuso: anuncios distintos del mismo anunciante con el mismo copy.
- lanzamientos: fechas de inicio distintas del mismo copy del mismo anunciante (relanzado = probado).
- rank_pct: posición en su búsqueda, que Meta ordena por impresiones totales (0 = el más visto).
- plataformas: en cuántas corre.
Calificación de 0 a 100: 40 por días (tope a los 60), 25 por versiones (log2, tope en 16), 20 por posición,
10 por reuso del copy (tope en 5) y 5 si corre en 2 plataformas o más.
Niveles: Ganador fuerte (30 días o más y 3 versiones o más o el copy en 2 fechas o más); Ganador de lanzamiento
(menos de 30 días y 5 versiones o más o el copy en 3 fechas o más); Probable (el resto).
--filtro (repetible) deja solo los anuncios cuyo texto cumple TODAS las expresiones (por ejemplo, que invite a una clase
y que sea del nicho). En giros de inventario lee también "paginas": anuncios activos por página.
"""
import argparse
import collections
import csv
import datetime
import glob
import json
import math
import os
import re
import sys

DIA = 86400
ORDEN_NIVELES = {'Ganador fuerte': 0, 'Ganador de lanzamiento': 1, 'Probable': 2}


def snapshot(ad):
    return ad.get('snapshot') or {}


def copy_de(ad):
    return ((snapshot(ad).get('body') or {}).get('text') or '').strip()


def texto(ad):
    s = snapshot(ad)
    partes = [copy_de(ad), s.get('title'), s.get('link_description'), s.get('caption'), s.get('cta_text'), s.get('link_url')]
    for c in s.get('cards') or []:
        partes += [c.get('body'), c.get('title'), c.get('link_description'), c.get('link_url')]
    return '\n'.join(p for p in partes if p)


def miniatura(ad):
    s = snapshot(ad)
    for v in s.get('videos') or []:
        if v.get('video_preview_image_url'):
            return v['video_preview_image_url']
    for c in (s.get('images') or []) + (s.get('cards') or []):
        url = c.get('video_preview_image_url') or c.get('original_image_url') or c.get('resized_image_url')
        if url:
            return url
    return None


def video_url(ad):
    for v in (snapshot(ad).get('videos') or []) + (snapshot(ad).get('cards') or []):
        if v.get('video_hd_url') or v.get('video_sd_url'):
            return v.get('video_hd_url') or v.get('video_sd_url')
    return None


def clave_copy(ad):
    return (ad.get('page_id'), re.sub(r'\s+', ' ', copy_de(ad).lower())[:160])


def fecha(segundos):
    return datetime.datetime.fromtimestamp(segundos, tz=datetime.timezone.utc).date().isoformat()


def dias_activo(ad, hoy):
    inicio = ad.get('start_date')
    if not inicio:
        return None
    return round((min(ad.get('end_date') or hoy, hoy) - inicio) / DIA, 1)


def calificacion(dias, versiones, rank_pct, reuso, plataformas):
    return round(40 * min((dias or 0) / 60, 1) + 25 * min(math.log2(max(versiones, 1)) / 4, 1)
                 + 20 * (1 - rank_pct) + 10 * min((reuso - 1) / 4, 1) + 5 * (1 if plataformas >= 2 else 0), 1)


def nivel(dias, versiones, lanzamientos):
    dias = dias or 0
    if dias >= 30 and (versiones >= 3 or lanzamientos >= 2):
        return 'Ganador fuerte'
    if dias < 30 and (versiones >= 5 or lanzamientos >= 3):
        return 'Ganador de lanzamiento'
    return 'Probable'


def leer_carpetas(carpetas):
    """Todos los anuncios sin repetir, las búsquedas donde salió cada uno y su mejor posición relativa."""
    anuncios, busquedas, rank_pct = {}, collections.defaultdict(set), {}
    for carpeta in carpetas:
        for ruta in sorted(glob.glob(os.path.join(carpeta, '*.json'))):
            with open(ruta, encoding='utf-8') as archivo:
                datos = json.load(archivo)
            lista = datos.get('anuncios') or []
            for ad in lista:
                k = ad['ad_archive_id']
                anuncios.setdefault(k, ad)
                busquedas[k].add(datos['consulta']['id'])
                rank_pct[k] = min(rank_pct.get(k, 1.0), (ad['rank'] - 1) / max(len(lista), 1))
    return anuncios, busquedas, rank_pct


def senales_de_copy(anuncios):
    reuso, fechas = collections.Counter(), collections.defaultdict(set)
    for ad in anuncios.values():
        if copy_de(ad):
            reuso[clave_copy(ad)] += 1
        if ad.get('start_date'):
            fechas[clave_copy(ad)].add(fecha(ad['start_date']))
    return reuso, fechas


def fila(k, ad, hoy, busquedas, rank_pct, reuso, fechas):
    s = snapshot(ad)
    dias = dias_activo(ad, hoy)
    versiones = ad.get('collation_count') or 1
    reusado = reuso[clave_copy(ad)] if copy_de(ad) else 1
    lanzamientos = len(fechas[clave_copy(ad)]) or 1
    plataformas = ad.get('publisher_platform') or []
    rp = rank_pct.get(k, 1.0)
    return {
        'ad_archive_id': k, 'url_biblioteca': f'https://www.facebook.com/ads/library/?id={k}',
        'anunciante': ad.get('page_name') or s.get('page_name'), 'page_id': ad.get('page_id'),
        'seguidores_pagina': s.get('page_like_count'), 'activo': ad.get('is_active'),
        'inicio': fecha(ad['start_date']) if ad.get('start_date') else None,
        'ultimo_dia_visto': fecha(min(ad.get('end_date') or hoy, hoy)) if ad.get('start_date') else None,
        'dias': dias, 'versiones': versiones, 'reuso_mismo_copy': reusado, 'lanzamientos_distintos_del_copy': lanzamientos,
        'rank_pct_en_busqueda': round(rp, 3), 'plataformas': plataformas, 'formato': s.get('display_format'),
        'cta': s.get('cta_text'), 'link_url': s.get('link_url'), 'titulo': s.get('title'),
        'descripcion_link': s.get('link_description'), 'copy': copy_de(ad),
        'tarjetas': [{'titulo': c.get('title'), 'copy': c.get('body'), 'link': c.get('link_url')} for c in (s.get('cards') or [])][:5],
        'miniatura': miniatura(ad), 'video': video_url(ad), 'busquedas': sorted(busquedas[k]),
        'calificacion': calificacion(dias, versiones, rp, reusado, len(plataformas)),
        'nivel': nivel(dias, versiones, lanzamientos),
    }


def representantes(filas):
    """Un anuncio por anunciante y copy (el de mejor calificación), ordenados por nivel y calificación."""
    mejor = {}
    for f in filas:
        k = (f['page_id'], re.sub(r'\s+', ' ', f['copy'].lower())[:160]) if f['copy'] else ('id', f['ad_archive_id'])
        if k not in mejor or f['calificacion'] > mejor[k]['calificacion']:
            mejor[k] = f
    return sorted(mejor.values(), key=lambda f: (ORDEN_NIVELES[f['nivel']], -f['calificacion']))


def activos_por_pagina(filas):
    """En giros de inventario gana la página que mantiene muchos anuncios a la vez, no el anuncio más viejo."""
    conteo = collections.Counter((f['anunciante'], f['page_id']) for f in filas if f['activo'])
    return [{'anunciante': a, 'page_id': p, 'activos': n} for (a, p), n in conteo.most_common()]


def calificar(carpetas, filtros=(), hoy=None):
    hoy = hoy or datetime.datetime.now(tz=datetime.timezone.utc).timestamp()
    anuncios, busquedas, rank_pct = leer_carpetas(carpetas)
    reuso, fechas = senales_de_copy(anuncios)
    patrones = [re.compile(f, re.I) for f in filtros]
    filas = [fila(k, ad, hoy, busquedas, rank_pct, reuso, fechas) for k, ad in anuncios.items()
             if all(p.search(texto(ad)) for p in patrones)]
    return {'total_anuncios': len(anuncios), 'pasan_filtro': len(filas), 'candidatos': representantes(filas),
            'paginas': activos_por_pagina(filas)}


COLUMNAS_CSV = ['nivel', 'calificacion', 'anunciante', 'dias', 'versiones', 'lanzamientos_distintos_del_copy',
                'reuso_mismo_copy', 'activo', 'inicio', 'formato', 'cta', 'link_url', 'url_biblioteca', 'copy']


def escribir_csv(filas, ruta):
    with open(ruta, 'w', encoding='utf-8', newline='') as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=COLUMNAS_CSV, extrasaction='ignore')
        escritor.writeheader()
        escritor.writerows(filas)


def main(argv=None):
    ap = argparse.ArgumentParser(description='Califica anuncios de la Biblioteca de Meta con señales públicas.')
    ap.add_argument('carpetas', nargs='+')
    ap.add_argument('--salida', required=True)
    ap.add_argument('--top', type=int, default=150)
    ap.add_argument('--filtro', action='append', default=[])
    ap.add_argument('--csv')
    a = ap.parse_args(argv)
    r = calificar(a.carpetas, a.filtro)
    r['candidatos'] = r['candidatos'][:a.top]
    with open(a.salida, 'w', encoding='utf-8') as archivo:
        json.dump(r, archivo, ensure_ascii=False, indent=1)
    if a.csv:
        escribir_csv(r['candidatos'], a.csv)
    niveles = collections.Counter(f['nivel'] for f in r['candidatos'])
    print(f"{r['total_anuncios']} anuncios leídos, {r['pasan_filtro']} pasan el filtro; guardados {len(r['candidatos'])} "
          f"en {a.salida}. Niveles: {dict(niveles)}. Son señales públicas, no resultados: la Biblioteca no da gasto ni clics.")


if __name__ == '__main__':
    sys.exit(main())
