"""Reglas puras de la investigación de virales: fechas, criterio de viralidad, niveles, equivalencia likes-vistas,
cascada de comentarios y cuotas.

Criterio (references/criterios-viralidad.md): cuenta < 50 mil seguidores -> vistas >= 10x seguidores;
cuenta >= 50 mil -> más de 1 millón de vistas. Los carruseles no muestran vistas: sus likes se pasan a
vistas con la mediana vistas/like de los reels de la misma investigación.
"""
import collections
import datetime
import statistics

EPOCA_INSTAGRAM_MS = 1314220021721
CUENTA_GRANDE = 50_000
MULTIPLO_CUENTA_CHICA = 10
VISTAS_CUENTA_GRANDE = 1_000_000
ESCALONES_COMENTARIOS = (1000, 700, 500, 300, 100)
PRIORIDAD_NIVEL = {'S': 0, 'A': 1, 'B': 2}  # el nivel B solo entra si S y A no llenan la cuota


def fecha_de_pk(pk):
    """Fecha de SUBIDA codificada en el identificador; puede adelantarse días a la publicación."""
    milisegundos = (int(pk) >> 23) + EPOCA_INSTAGRAM_MS
    return datetime.datetime.fromtimestamp(milisegundos / 1000, tz=datetime.timezone.utc)


def fecha_de_publicacion(publicacion):
    if publicacion.get('taken_at'):
        return datetime.datetime.fromtimestamp(int(publicacion['taken_at']), tz=datetime.timezone.utc)
    return fecha_de_pk(publicacion['pk'])


def es_viral(vistas, seguidores):
    if seguidores >= CUENTA_GRANDE:
        return vistas > VISTAS_CUENTA_GRANDE
    return vistas >= MULTIPLO_CUENTA_CHICA * seguidores


def nivel(vistas, seguidores):
    """S: más de 1 M y >= 10x a la vez; A: más de 1 M sin importar el tamaño; B: >= 10x sin llegar al millón."""
    millon = vistas > VISTAS_CUENTA_GRANDE
    diez_veces = vistas >= MULTIPLO_CUENTA_CHICA * seguidores
    if millon and diez_veces:
        return 'S'
    if millon:
        return 'A'
    return 'B' if diez_veces else None


def es_viral_nivel_2(vistas, seguidores):
    """Rescate con el umbral a la mitad. Solo si no se llega a la cifra, y siempre etiquetado como Nivel 2."""
    if seguidores >= CUENTA_GRANDE:
        return vistas > VISTAS_CUENTA_GRANDE / 2
    return vistas >= MULTIPLO_CUENTA_CHICA / 2 * seguidores


def vistas_de(reel):
    """Las vistas del payload mandan; si no llegaron, el contador visible de /reels/ (redondeado)."""
    return reel.get('play_count') or reel.get('vistas_visibles')


def cascada_comentarios(piezas, cantidad=None, escalones=ESCALONES_COMENTARIOS):
    """Más de 1,000 comentarios, luego más de 700, 500, 300 y 100, hasta juntar `cantidad` (None = el máximo posible).
    Cada pieza sale con el escalón en que entró."""
    elegidas, usados = [], set()
    for escalon in escalones:
        nuevas = sorted((p for p in piezas if (p.get('comentarios') or 0) > escalon and p['code'] not in usados),
                        key=lambda p: -p['comentarios'])
        for pieza in nuevas:
            if cantidad is not None and len(elegidas) >= cantidad:
                return elegidas
            elegidas.append({**pieza, 'escalon': escalon})
            usados.add(pieza['code'])
    return elegidas


def carrusel_es_viral(likes, seguidores, vistas_por_like):
    return es_viral(likes * vistas_por_like, seguidores)


def mediana_vistas_por_like(escaneos, desde):
    proporciones = [
        reel['play_count'] / reel['like_count']
        for escaneo in escaneos for reel in escaneo['items']
        if reel.get('type') == 'clips' and reel.get('play_count') and reel.get('like_count') and reel.get('pk')
        and fecha_de_publicacion(reel) >= desde
    ]
    if not proporciones:
        raise ValueError('no hay reels recientes con vistas y likes para medir la equivalencia')
    return round(statistics.median(proporciones), 1), len(proporciones)


def reels_virales(escaneo, desde, captions):
    seguidores = escaneo.get('followers')
    if not seguidores:
        return []
    virales = []
    for reel in escaneo['items']:
        vistas = vistas_de(reel)
        if reel.get('type') != 'clips' or not vistas or not reel.get('pk'):
            continue
        fecha = fecha_de_publicacion(reel)
        if fecha < desde or not es_viral(vistas, seguidores):
            continue
        virales.append({
            'formato': 'reel', 'cuenta': escaneo['handle'], 'seguidores': seguidores, 'code': reel['code'],
            'pk': reel['pk'], 'enlace': f"https://www.instagram.com/reel/{reel['code']}/", 'vistas': vistas,
            'veces_seguidores': round(vistas / seguidores, 1), 'likes': reel.get('like_count'),
            'comentarios': reel.get('comment_count'), 'caption': captions.get(reel['code']),
            'miniatura': reel.get('thumb'), 'alcance': vistas, 'nivel': nivel(vistas, seguidores),
        })
    return virales


def carruseles_virales(escaneo, desde, vistas_por_like):
    seguidores = escaneo.get('followers')
    if not seguidores:
        return []
    virales = []
    for post in escaneo['items']:
        likes = post.get('like_count')
        if post.get('type') != 'carousel_container' or not likes or not post.get('pk'):
            continue
        fecha = fecha_de_publicacion(post)
        if fecha < desde or not carrusel_es_viral(likes, seguidores, vistas_por_like):
            continue
        virales.append({
            'formato': 'carrusel', 'cuenta': escaneo['handle'], 'seguidores': seguidores, 'code': post['code'],
            'pk': post['pk'], 'enlace': f"https://www.instagram.com/p/{post['code']}/", 'vistas': None,
            'likes': likes, 'likes_entre_seguidores': round(likes / seguidores, 2), 'laminas': post.get('slides'),
            'comentarios': post.get('comment_count'), 'caption': post.get('caption'),
            'miniatura': post.get('thumb'), 'alcance': round(likes * vistas_por_like),
            'nivel': nivel(likes * vistas_por_like, seguidores),
        })
    return virales


def prioridad(pieza):
    """S y A antes que B (sin importar el alcance); dentro del mismo nivel, de más a menos alcance."""
    return PRIORIDAD_NIVEL.get(pieza.get('nivel'), len(PRIORIDAD_NIVEL)), -pieza['alcance']


def tope_por_cuenta(piezas, maximo):
    piezas_por_cuenta, elegidas = collections.Counter(), []
    for pieza in sorted(piezas, key=prioridad):
        if piezas_por_cuenta[pieza['cuenta']] < maximo:
            piezas_por_cuenta[pieza['cuenta']] += 1
            elegidas.append(pieza)
    return elegidas


def carruseles_por_idioma(piezas, orden, cupo, maximo_por_cuenta):
    """[(idioma, carruseles)] en el orden dado; en cada idioma, los de más likes hasta el cupo, con tope por cuenta."""
    carruseles = [p for p in piezas if p['formato'] == 'carrusel']
    return [(idioma, sorted(tope_por_cuenta([c for c in carruseles if c['idioma'] == idioma], maximo_por_cuenta),
                            key=lambda c: -c['likes'])[:cupo])
            for idioma in orden]


def elegir_por_cuota(piezas, cuotas, maximo_por_cuenta):
    """Llena cada idioma en el orden de `cuotas`; si uno no alcanza, lo que falta lo completa SOLO el primer idioma
    (no el segundo ni el tercero). Si el primero tampoco alcanza, la lista sale corta: no se rellena.
    Dentro de cada idioma, el nivel B solo entra si S y A no llenan su cupo, y sale marcado como relleno."""
    por_idioma = {idioma: tope_por_cuenta([p for p in piezas if p['idioma'] == idioma], maximo_por_cuenta)
                  for idioma in cuotas}
    elegidas = {idioma: por_idioma[idioma][:cupo] for idioma, cupo in cuotas.items()}
    faltan = sum(cuotas.values()) - sum(len(v) for v in elegidas.values())
    primero = next(iter(cuotas))
    if faltan > 0:
        elegidas[primero] += por_idioma[primero][cuotas[primero]:cuotas[primero] + faltan]
    final = [p for idioma in cuotas for p in elegidas[idioma]]
    return [{**p, 'n': i, 'relleno_nivel_b': p.get('nivel') == 'B'} for i, p in enumerate(final, 1)]
