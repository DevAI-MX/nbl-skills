#!/usr/bin/env python3
"""Pasos de una investigación de virales de Instagram. Cada investigación vive en una carpeta con config.json.

Uso: python3 pasos.py <carpeta> <paso>
Orden: precuentas -> (agente: preclasificacion.json, opcional) -> listas -> (batchscan reels y feed) -> candidatos -> cuentas -> (agente: clasificacion_cuentas.json)
       -> faltantes -> (minfo.mjs: fichas.json) -> pool -> (agentes: clasificacion_lote_N.json)
       -> elegibles -> final -> tendencias -> documento
Los pasos entre paréntesis corren fuera de este script (recolectores de scripts/ig/ o subagentes).
Los escaneos por cuenta se leen de ESCANEOS_DIR (absoluta, o relativa a la carpeta) o de <carpeta>/escaneos: la misma
regla que usan los recolectores de Node. Las rutas relativas de config.json se resuelven contra la carpeta.
"""
import collections
import datetime
import json
import os
import re
import shutil
import subprocess
import sys

from seleccion import (carruseles_por_idioma, carruseles_virales, elegir_por_cuota, fecha_de_publicacion, mediana_vistas_por_like,
                       reels_virales, tope_por_cuenta)

TIPO_VIDEO, TIPO_CARRUSEL = 2, 8
MARGEN_POOL = 3
MARGEN_CARRUSELES_EN_POOL = 1.5
LOTES = 3
IDIOMA = {'en': 'Inglés', 'pt': 'Portugués', 'es': 'Español', 'otro': 'Otro idioma'}
LARGO_CAPTION = 600
CARRUSELES_APARTE, CARRUSELES_POR_CUENTA_APARTE = 12, 2


class Investigacion:
    def __init__(self, carpeta):
        self.carpeta = carpeta
        self.config = self.leer('config.json')
        self.desde = datetime.datetime.fromisoformat(self.config['desde']).replace(tzinfo=datetime.timezone.utc)
        self.carpeta_escaneos = os.path.abspath(self.ruta(os.environ.get('ESCANEOS_DIR') or 'escaneos'))

    def ruta(self, nombre):
        return os.path.join(self.carpeta, os.path.expanduser(nombre))

    def leer(self, nombre):
        with open(self.ruta(nombre), encoding='utf-8') as archivo:
            return json.load(archivo)

    def guardar(self, nombre, datos):
        with open(self.ruta(nombre), 'w', encoding='utf-8') as archivo:
            json.dump(datos, archivo, ensure_ascii=False, indent=1)

    def carruseles_aparte(self):
        """Cupo por idioma y orden de idiomas de la sección aparte de carruseles."""
        return (self.config.get('carruseles_aparte_por_idioma', CARRUSELES_APARTE),
                self.config.get('orden_carruseles_aparte', list(self.config['cuotas'])))

    def texto(self, nombre):
        with open(self.ruta(nombre), encoding='utf-8') as archivo:
            return archivo.read().strip()

    def medios_de_busqueda(self):
        return list(self.leer('serp.json')['media'].values())

    def escaneos(self, listas, sufijo):
        cuentas = sorted({c for lista in listas for c in self.leer(lista)})
        for cuenta in cuentas:
            ruta = os.path.join(self.carpeta_escaneos, f'{cuenta}{sufijo}.json')
            if os.path.exists(ruta):
                with open(ruta, encoding='utf-8') as archivo:
                    yield json.load(archivo)

    def bio_de(self, cuenta):
        for sufijo in ('', '.feed'):
            ruta = os.path.join(self.carpeta_escaneos, f'{cuenta}{sufijo}.json')
            if os.path.exists(ruta):
                with open(ruta, encoding='utf-8') as archivo:
                    return json.load(archivo).get('header_text', '')[:400]
        return ''


def partir_en_dos(investigacion, cuentas, prefijo):
    investigacion.guardar(f'{prefijo}_a.json', cuentas[0::2])
    investigacion.guardar(f'{prefijo}_b.json', cuentas[1::2])


def cuentas_por_likes(medios, tipo, desde, minimo):
    mejor = collections.defaultdict(int)
    for m in medios:
        if m['media_type'] == tipo and m['taken_at'] >= desde.timestamp():
            mejor[m['user']] = max(mejor[m['user']], m['likes'] or 0)
    return [cuenta for cuenta, likes in sorted(mejor.items(), key=lambda kv: -kv[1]) if likes >= minimo]


def cuentas_fuera_del_nicho(inv):
    if not os.path.exists(inv.ruta('preclasificacion.json')):
        return set()
    return {c['cuenta'] for c in inv.leer('preclasificacion.json') if c['nicho'] == 'no'}


def paso_precuentas(inv):
    """Captions recientes por cuenta, para descartar cuentas fuera del nicho antes de escanearlas."""
    recientes = collections.defaultdict(list)
    for m in inv.medios_de_busqueda():
        if m['media_type'] in (TIPO_VIDEO, TIPO_CARRUSEL) and m['taken_at'] >= inv.desde.timestamp():
            recientes[m['user']].append(m)
    salida = [{'cuenta': cuenta, 'captions_de_muestra': [(m['caption'] or '')[:220].replace('\n', ' ')
                                                         for m in sorted(ms, key=lambda m: -(m['likes'] or 0))[:5]]}
              for cuenta, ms in sorted(recientes.items())]
    inv.guardar('cuentas_para_preclasificar.json', salida)
    print(f'{len(salida)} cuentas con publicaciones recientes para preclasificar')


def paso_listas(inv):
    medios, fuera = inv.medios_de_busqueda(), cuentas_fuera_del_nicho(inv)
    reels = [c for c in cuentas_por_likes(medios, TIPO_VIDEO, inv.desde, inv.config['min_likes_video']) if c not in fuera]
    carruseles = [c for c in cuentas_por_likes(medios, TIPO_CARRUSEL, inv.desde, inv.config['min_likes_carrusel'])
                  if c not in fuera]
    partir_en_dos(inv, reels, 'cuentas')
    partir_en_dos(inv, carruseles, 'carruseles')
    print(f'{len(medios)} publicaciones; {len(reels)} cuentas de reels y {len(carruseles)} de carruseles a escanear')


def paso_candidatos(inv):
    escaneos_reels = list(inv.escaneos(['cuentas_a.json', 'cuentas_b.json'], ''))
    vistas_por_like, muestra = mediana_vistas_por_like(escaneos_reels, inv.desde)
    captions = {m['code']: m['caption'] for m in inv.medios_de_busqueda() if m.get('caption')}
    reels = [r for e in escaneos_reels for r in reels_virales(e, inv.desde, captions)]
    carruseles = [c for e in inv.escaneos(['carruseles_a.json', 'carruseles_b.json'], '.feed')
                  for c in carruseles_virales(e, inv.desde, vistas_por_like)]
    inv.guardar('medicion.json', {'vistas_por_like': vistas_por_like, 'reels_medidos': muestra,
                                  'cuentas_reels': len(escaneos_reels)})
    inv.guardar('candidatos.json', sorted(reels + carruseles, key=lambda p: -p['alcance']))
    print(f'{vistas_por_like} vistas por like ({muestra} reels); {len(reels)} reels virales de '
          f'{len({r["cuenta"] for r in reels})} cuentas; {len(carruseles)} carruseles virales de '
          f'{len({c["cuenta"] for c in carruseles})} cuentas')


def paso_cuentas(inv):
    candidatos = inv.leer('candidatos.json')
    captions = collections.defaultdict(list)
    for m in inv.medios_de_busqueda():
        if m.get('caption'):
            captions[m['user']].append(m['caption'][:220].replace('\n', ' '))
    salida = []
    for cuenta in sorted({c['cuenta'] for c in candidatos}):
        propias = [c for c in candidatos if c['cuenta'] == cuenta]
        muestra = captions[cuenta] + [(c['caption'] or '')[:220] for c in propias if c['caption']]
        salida.append({'cuenta': cuenta, 'seguidores': propias[0]['seguidores'], 'piezas_virales': len(propias),
                       'bio': inv.bio_de(cuenta), 'captions_de_muestra': muestra[:5]})
    inv.guardar('cuentas_para_clasificar.json', salida)
    print(f'{len(salida)} cuentas para clasificar')


def cuentas_aceptadas(inv):
    """Idioma de cada cuenta del nicho sin exclusiones."""
    return {c['cuenta']: c['idioma'] for c in inv.leer('clasificacion_cuentas.json')
            if c['nicho'] in ('si', 'mixto') and not c['excluir_por']}


def piezas_del_pool(inv):
    """Por idioma de la cuenta, las de más alcance (tope por cuenta) hasta MARGEN_POOL veces el cupo,
    más los carruseles con más likes de cada idioma para la sección aparte. Lo demás no puede entrar en la lista final.
    El idioma de la cuenta se copia a 'idioma' para agrupar; la clasificación de cada pieza lo reemplaza después."""
    idioma_de = cuentas_aceptadas(inv)
    candidatos = [{**c, 'idioma_cuenta': idioma_de[c['cuenta']], 'idioma': idioma_de[c['cuenta']]}
                  for c in inv.leer('candidatos.json') if c['cuenta'] in idioma_de]
    pool = []
    for idioma, cupo in inv.config['cuotas'].items():
        del_idioma = [c for c in candidatos if c['idioma_cuenta'] == idioma]
        pool += tope_por_cuenta(del_idioma, inv.config['max_por_cuenta'])[:MARGEN_POOL * cupo]
    cupo_aparte, orden = inv.carruseles_aparte()
    for _, carruseles in carruseles_por_idioma(candidatos, orden, round(MARGEN_CARRUSELES_EN_POOL * cupo_aparte),
                                               CARRUSELES_POR_CUENTA_APARTE):
        pool += carruseles
    return sin_repetidos(pool)


def sin_repetidos(piezas):
    unicas = {}
    for pieza in piezas:
        unicas.setdefault(pieza['code'], pieza)
    return list(unicas.values())


def paso_faltantes(inv):
    sin_caption = [p['pk'] for p in piezas_del_pool(inv) if not p['caption']]
    inv.guardar('pks_sin_caption.json', sin_caption)
    print(f'{len(sin_caption)} piezas sin caption: correr minfo.mjs con pks_sin_caption.json -> fichas.json')


def fichas_por_codigo(inv):
    if not os.path.exists(inv.ruta('fichas.json')):
        return {}
    return {f['code']: f for f in inv.leer('fichas.json').values() if 'code' in f}


def bajar_portada(inv, pieza):
    os.makedirs(inv.ruta('portadas'), exist_ok=True)
    destino = inv.ruta(f"portadas/{pieza['code']}.jpg")
    if not os.path.exists(destino) and pieza.get('miniatura'):
        subprocess.run(['curl', '-s', '--max-time', '20', '-o', destino, pieza['miniatura']], check=False)
    return f"portadas/{pieza['code']}.jpg"


def paso_pool(inv):
    fichas = fichas_por_codigo(inv)
    pool = []
    for i, pieza in enumerate(piezas_del_pool(inv), 1):
        ficha = fichas.get(pieza['code'], {})
        pool.append({**pieza, 'id': i, 'caption': pieza['caption'] or ficha.get('caption') or '',
                     'duracion_s': round(ficha['dur']) if ficha.get('dur') else None,
                     'portada': bajar_portada(inv, pieza)})
    inv.guardar('pool.json', pool)
    tamano = -(-len(pool) // LOTES)
    for n in range(LOTES):
        inv.guardar(f'lote_{n + 1}.json', [{k: v for k, v in p.items() if k != 'miniatura'}
                                           for p in pool[n * tamano:(n + 1) * tamano]])
    print(f'{len(pool)} piezas en {LOTES} lotes; sin caption: {sum(1 for p in pool if not p["caption"])}')


def fechas_reales(inv):
    fechas = {m['code']: m['taken_at'] for m in inv.medios_de_busqueda() if m.get('taken_at')}
    for escaneo in inv.escaneos(['carruseles_a.json', 'carruseles_b.json'], '.feed'):
        fechas.update({i['code']: int(i['taken_at']) for i in escaneo['items'] if i.get('taken_at')})
    fechas.update({c: f['taken_at'] for c, f in fichas_por_codigo(inv).items() if f.get('taken_at')})
    return fechas


def paso_elegibles(inv):
    # Los agentes a veces devuelven el id como texto: se normaliza a entero para cruzarlo con el pool.
    clasificacion = {int(c['id']): {**c, 'id': int(c['id'])}
                     for n in range(LOTES) for c in inv.leer(f'clasificacion_lote_{n + 1}.json')}
    a_mano = inv.config.get('excluidas_a_mano', {'cuentas': [], 'codes': []})
    fechas, elegibles, sin_fecha = fechas_reales(inv), [], []
    for pieza in inv.leer('pool.json'):
        clase = clasificacion.get(pieza['id'])
        if not clase or not clase['en_nicho'] or clase['excluir']:
            continue
        if pieza['cuenta'] in a_mano['cuentas'] or pieza['code'] in a_mano['codes']:
            continue
        marca = fechas.get(pieza['code'])
        fecha = fecha_de_publicacion({'taken_at': marca, 'pk': pieza['pk']})
        if not marca:
            sin_fecha.append(pieza['code'])
        if fecha < inv.desde:
            continue
        elegibles.append({**pieza, **clase, 'fecha_real': fecha.date().isoformat(), 'fecha_confirmada': bool(marca)})
    inv.guardar('elegibles.json', elegibles)
    print(f'{len(elegibles)} elegibles {dict(collections.Counter(p["idioma"] for p in elegibles))}; '
          f'sin fecha real confirmada: {len(sin_fecha)}')


def paso_final(inv):
    final = elegir_por_cuota(inv.leer('elegibles.json'), inv.config['cuotas'], inv.config['max_por_cuenta'])
    inv.guardar('final.json', final)
    for p in final:
        print(p['n'], p['idioma'], p['formato'], p['cuenta'], p['seguidores'], p['vistas'] or p['likes'],
              p['fecha_real'], p['tema'])


def grupo_de(tema, grupos):
    for nombre, patron in grupos:
        if re.search(patron, tema, re.I):
            return nombre
    return 'Otros'


def paso_tendencias(inv):
    for nombre in ('elegibles.json', 'final.json'):
        conteo, alcance, idiomas = collections.Counter(), collections.Counter(), collections.defaultdict(collections.Counter)
        for p in inv.leer(nombre):
            grupo = grupo_de(p['tema'], inv.config['grupos'])
            conteo[grupo] += 1
            alcance[grupo] += p['alcance']
            idiomas[grupo][p['idioma']] += 1
        print(nombre)
        for grupo, n in conteo.most_common():
            print(f'  {grupo}: {n} piezas, {alcance[grupo] / 1e6:.1f} M de alcance, {dict(idiomas[grupo])}')


def celda(texto):
    return (texto or '').replace('|', '/').replace('\n', ' ').strip()


def numero(n):
    return f'{n:,}'


def medida(pieza):
    if pieza['formato'] == 'reel':
        nivel = f" (nivel {pieza['nivel']}{', relleno' if pieza.get('relleno_nivel_b') else ''})" if pieza.get('nivel') else ''
        return f"{numero(pieza['vistas'])} vistas", f"{pieza['veces_seguidores']}x{nivel}"
    return f"{numero(pieza['likes'])} likes", f"likes = {int(pieza['likes_entre_seguidores'] * 100)}% de seguidores"


def fila(p):
    alcance, relacion = medida(p)
    return (f"| {p['n']} | @{p['cuenta']} | {numero(p['seguidores'])} | {celda(p.get('mercado')) or 'no visible'} | "
            f"{IDIOMA[p['idioma']]} | {p['formato']} | "
            f"{alcance} | {relacion} | {p['fecha_real']} | {celda(p['tema'])} | {celda(p['gancho_portada'])} | "
            f"[abrir]({p['enlace']}) |")


def ficha_markdown(p, carpeta_portadas):
    alcance, relacion = medida(p)
    caption = (p['caption'] or '').strip()
    caption = caption if len(caption) <= LARGO_CAPTION else caption[:LARGO_CAPTION].rstrip() + ' [...]'
    citado = '\n'.join('> ' + linea for linea in (caption or '_sin caption_').split('\n'))
    duracion = f" · {p['duracion_s']} s" if p.get('duracion_s') else ''
    return '\n'.join([
        f"### {p['n']}. @{p['cuenta']} · {IDIOMA[p['idioma']]} · {p['formato']}{duracion}",
        f"- **Alcance:** {alcance} ({relacion}), {numero(p['seguidores'])} seguidores, publicado el {p['fecha_real']}. [Abrir]({p['enlace']})",
        f"- **Gancho de portada:** {celda(p['gancho_portada'])}",
        f"- **Qué se ve:** {celda(p['formato_visual'])}",
        f"- **De qué trata:** {celda(p['de_que_trata'])}",
        f"- **Portada:** `{os.path.basename(carpeta_portadas)}/{p['n']:02d}-{p['cuenta']}.jpg`",
        '- **Caption:**', '', citado, ''])


def seccion_carruseles(inv):
    cupo, orden = inv.carruseles_aparte()
    lineas = [f'## Aparte: los {cupo} carruseles con más likes de cada idioma\n',
              f'_Solo carruseles que pasaron todos los filtros. Máximo {CARRUSELES_POR_CUENTA_APARTE} por cuenta._\n']
    for idioma, carruseles in carruseles_por_idioma(inv.leer('elegibles.json'), orden, cupo,
                                                    CARRUSELES_POR_CUENTA_APARTE):
        lineas.append(f'### {IDIOMA[idioma]} ({len(carruseles)})\n')
        if not carruseles:
            lineas += ['_Ningún carrusel en este idioma pasó el criterio y los filtros._', '']
            continue
        lineas += ['| Cuenta | Seguidores | Likes | Láminas | Fecha | Gancho de portada | De qué trata | Enlace |',
                   '|---|---|---|---|---|---|---|---|']
        lineas += [fila_carrusel(c) for c in carruseles] + ['']
    return '\n'.join(lineas) + '\n'


def fila_carrusel(c):
    return (f"| @{c['cuenta']} | {numero(c['seguidores'])} | {numero(c['likes'])} | {c.get('laminas') or ''} | "
            f"{c['fecha_real']} | {celda(c['gancho_portada'])} | {celda(c['de_que_trata'])} | [abrir]({c['enlace']}) |")


def paso_documento(inv):
    final, config = inv.leer('final.json'), inv.config
    partes = [f"# {config['titulo']}", f"_{config['subtitulo']}_\n", inv.texto('tendencias_texto.md') + '\n',
              f'## Los {len(final)}\n',
              '| # | Cuenta | Seguidores | Mercado | Idioma | Formato | Alcance | Relación | Fecha | Tema | Gancho de portada | Enlace |',
              '|---|---|---|---|---|---|---|---|---|---|---|---|']
    partes += [fila(p) for p in final]
    partes += ['', seccion_carruseles(inv), '## Ficha de cada uno (con su caption)\n']
    partes += [ficha_markdown(p, config['carpeta_portadas']) for p in final]
    partes.append(inv.texto('metodo.md') + '\n')
    salida_md, portadas = inv.ruta(config['salida_md']), inv.ruta(config['carpeta_portadas'])
    os.makedirs(os.path.dirname(salida_md) or '.', exist_ok=True)
    with open(salida_md, 'w', encoding='utf-8') as archivo:
        archivo.write('\n'.join(partes))
    os.makedirs(portadas, exist_ok=True)
    for p in final:
        if os.path.exists(inv.ruta(p['portada'])):
            shutil.copy(inv.ruta(p['portada']), os.path.join(portadas, f"{p['n']:02d}-{p['cuenta']}.jpg"))
    print('ok', len(final), salida_md)


PASOS = {'precuentas': paso_precuentas, 'listas': paso_listas, 'candidatos': paso_candidatos, 'cuentas': paso_cuentas, 'faltantes': paso_faltantes,
         'pool': paso_pool, 'elegibles': paso_elegibles, 'final': paso_final, 'tendencias': paso_tendencias,
         'documento': paso_documento}


def main():
    if len(sys.argv) != 3 or sys.argv[2] not in PASOS:
        sys.exit(f'uso: python3 pasos.py <carpeta> <{"|".join(PASOS)}>')
    PASOS[sys.argv[2]](Investigacion(sys.argv[1]))


if __name__ == '__main__':
    main()
