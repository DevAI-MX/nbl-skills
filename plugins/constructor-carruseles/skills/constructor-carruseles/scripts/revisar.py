#!/usr/bin/env python3
"""Revisa un carrusel antes de entregarlo, con las reglas que se pueden medir.

Uso:
  python3 revisar.py <carpeta-del-carrusel> [--palabra PALABRA] [--activas marca/palabras-activas.txt]
                     [--handle @usuario] [--plataforma instagram|tiktok] [--png DIR] [--sin-png]

Mide: campos {{...}} sin llenar, flecha o número de slide (salvo que la referencia los traiga), etiquetas
encima del título, negritas en el formato tuit, pie distinto entre slides, el @ repetido en una slide,
palabras por lámina interior (título 14, cuerpo 30), total de slides, que el cierre con palabra enseñe el
recurso, que la palabra no choque con otra activa (también sin acento) y que cada PNG mida 2160x2700. Lo que no se mide (que se lea,
que nada se encime) se revisa mirando los PNG. Sale con 1 si hay errores.
"""
import argparse
import html as html_lib
import json
import re
import struct
import sys
import unicodedata
from pathlib import Path

ANCHO, ALTO = 2160, 2700
MAX_TITULO, MAX_CUERPO = 14, 30
MIN_IDEAL, MAX_IDEAL, MAX_SLIDES = 7, 10, 20
INVISIBLE = re.compile(r"<(style|script)\b.*?</\1>|<!--.*?-->", re.S | re.I)
ETIQUETA = re.compile(r"<[^>]+>")
PIE = re.compile(r'<div class="pie">.*?</div>', re.S)
CLASE_PAGINACION = re.compile(r'class="[^"]*\b(pag|desliza)\b')
PALABRA_DESLIZA = re.compile(r"\bdesliza\w*", re.I)
CONTADOR = re.compile(r"(?<![\d/])\d{1,2}\s*/\s*\d{1,2}(?![\d/])")
FIRMA_PNG = b"\x89PNG\r\n\x1a\n"
CLASE_KICKER = re.compile(r'class="[^"]*\b(etiqueta|antes|kicker|meta)\b')
ANTES_DEL_TITULO = re.compile(r"<(span|div|p|small)([^>]*)>([^<]{1,40})</\1>\s*<h[12]\b", re.I)
NO_ES_KICKER = re.compile(r"pastilla|urgente")
NEGRITA = re.compile(r"<(b|strong)\b", re.I)


def texto_visible(html):
    sin_codigo = INVISIBLE.sub(" ", html)
    return " ".join(html_lib.unescape(ETIQUETA.sub(" ", sin_codigo)).split())


def contar_palabras(texto_html):
    return len(texto_visible(str(texto_html)).split())


def sin_acento(texto):
    return "".join(c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn")


def revisar_pendientes(htmls):
    return [f"slide {n:02d}: quedó {', '.join(sorted(set(re.findall(r'{{[A-Z0-9_]+}}', h))))} sin llenar"
            for n, h in enumerate(htmls, 1) if "{{" in h]


def revisar_paginacion(htmls):
    errores, avisos = [], []
    for n, h in enumerate(htmls, 1):
        if CLASE_PAGINACION.search(h) or PALABRA_DESLIZA.search(texto_visible(h)):
            errores.append(f"slide {n:02d}: lleva flecha de «desliza» o número de slide; van sin ellos")
        elif CONTADOR.search(texto_visible(h)):
            avisos.append(f"slide {n:02d}: hay algo como «N / M»; si es un contador de slides, quítalo")
    return errores, avisos


def revisar_kickers(htmls):
    """Etiquetas encima del título: por clase es error; texto corto en mayúsculas justo antes del título, aviso."""
    errores, avisos = [], []
    for n, h in enumerate(htmls, 1):
        sin_codigo = INVISIBLE.sub(" ", h)
        if CLASE_KICKER.search(sin_codigo):
            errores.append(f"slide {n:02d}: lleva una etiqueta encima del título (kicker); va sin ella")
            continue
        for _, atributos, texto in ANTES_DEL_TITULO.findall(sin_codigo):
            texto = texto.strip()
            if texto and texto == texto.upper() and any(c.isalpha() for c in texto) and not NO_ES_KICKER.search(atributos):
                avisos.append(f"slide {n:02d}: «{texto}» parece una etiqueta encima del título; si lo es, quítala")
    return errores, avisos


def revisar_negritas_tuit(htmls):
    return [f"slide {n:02d}: el formato tuit va sin negritas (X no las tiene)"
            for n, h in enumerate(htmls, 1) if NEGRITA.search(INVISIBLE.sub(" ", h))]


def revisar_recurso(htmls, palabra):
    if not palabra or 'class="recurso' in htmls[-1]:
        return []
    return ["el cierre pide la palabra pero no enseña el recurso (bloque RECURSO: la hoja borrosa con su título y sello)"]


def revisar_pies(htmls):
    pies = {p for h in htmls for p in PIE.findall(h)}
    return [f"el pie no es idéntico en todas las slides ({len(pies)} versiones distintas)"] if len(pies) > 1 else []


def revisar_handle(htmls, handle):
    if not handle:
        return []
    return [f"slide {n:02d}: el {handle} aparece {veces} veces; va una sola"
            for n, h in enumerate(htmls, 1) if (veces := texto_visible(h).count(handle)) > 1]


def revisar_palabras(spec):
    """Errores por láminas interiores que pasan el tope, e info del largo del gancho."""
    slides = spec.get("slides", [])
    errores, info = [], []
    if slides:
        gancho = slides[0].get("campos", {}).get("GANCHO", "")
        info.append(f"gancho: {contar_palabras(gancho)} palabras (propio: de 6 a 10; de referencia: tal cual)")
    for n, s in enumerate(slides[1:-1], 2):
        campos = s.get("campos", {})
        for campo, tope in (("TITULO", MAX_TITULO), ("TEXTO", MAX_CUERPO)):
            cuenta = contar_palabras(campos.get(campo, ""))
            if cuenta > tope:
                errores.append(f"slide {n:02d}: {campo} tiene {cuenta} palabras; el tope es {tope}")
    return errores, info


def revisar_total(total):
    if total > MAX_SLIDES:
        return [f"{total} slides: Instagram permite hasta {MAX_SLIDES}"], []
    if not MIN_IDEAL <= total <= MAX_IDEAL:
        return [], [f"{total} slides: lo usual es de {MIN_IDEAL} a {MAX_IDEAL}"]
    return [], []


def leer_activas(ruta):
    if not ruta or not Path(ruta).exists():
        return set()
    lineas = Path(ruta).read_text(encoding="utf-8").splitlines()
    return {sin_acento(l.split("#", 1)[0].strip()).upper() for l in lineas if l.split("#", 1)[0].strip()}


def revisar_palabra_clave(palabra, activas):
    clave = sin_acento(palabra).upper()
    info = [f"palabra del cierre: {palabra.upper()}; configúrala también sin acento: {clave}"]
    errores = [f"la palabra {clave} ya está activa en otro carrusel; elige otra"] if clave in leer_activas(activas) else []
    return errores, info


def medidas_png(ruta):
    cabecera = Path(ruta).read_bytes()[:24]
    if len(cabecera) < 24 or not cabecera.startswith(FIRMA_PNG):
        raise ValueError("no es un PNG")
    return struct.unpack(">II", cabecera[16:24])


def revisar_pngs(carpeta_png, total):
    errores = []
    for n in range(1, total + 1):
        ruta = Path(carpeta_png) / f"slide-{n:02d}.png"
        if not ruta.exists():
            errores.append(f"falta {ruta.name} en {carpeta_png}")
            continue
        try:
            ancho, alto = medidas_png(ruta)
        except ValueError:
            errores.append(f"{ruta.name} no es un PNG válido")
            continue
        if (ancho, alto) != (ANCHO, ALTO):
            errores.append(f"{ruta.name} mide {ancho}x{alto}; debe medir {ANCHO}x{ALTO}")
    return errores


def leer_spec(carpeta):
    ruta = carpeta / "carrusel.json"
    return json.loads(ruta.read_text(encoding="utf-8")) if ruta.exists() else {}


def revisar_todo(carpeta, args):
    base = carpeta / "tiktok" if args.plataforma == "tiktok" else carpeta
    htmls = [p.read_text(encoding="utf-8") for p in sorted((base / "slides").glob("slide-*.html"))]
    if not htmls:
        return [f"no hay slides en {base / 'slides'}"], [], []
    spec = leer_spec(carpeta)
    handle = args.handle or spec.get("campos_comunes", {}).get("HANDLE", "")
    errores, avisos, info = revisar_pendientes(htmls) + revisar_pies(htmls) + revisar_handle(htmls, handle), [], []
    paginacion = revisar_paginacion(htmls)
    if spec.get("copia_paginacion_de_referencia"):
        paginacion = ([], [f"la referencia lleva paginación o flecha y se copió: {e}" for e in paginacion[0]])
    for e, a in (paginacion, revisar_kickers(htmls), revisar_total(len(htmls))):
        errores += e
        avisos += a
    if spec.get("formato") == "tuit":
        errores += revisar_negritas_tuit(htmls)
    e, i = revisar_palabras(spec)
    errores, info = errores + e, info + i
    palabra = args.palabra or (spec.get("slides") or [{}])[-1].get("campos", {}).get("PALABRA", "")
    if palabra:
        e, i = revisar_palabra_clave(texto_visible(palabra), args.activas)
        errores, info = errores + e, info + i
        if args.plataforma == "instagram":
            errores += revisar_recurso(htmls, palabra)
    if not args.sin_png:
        errores += revisar_pngs(Path(args.png) if args.png else base / "png", len(htmls))
    return errores, avisos, info


def main(argv=None):
    p = argparse.ArgumentParser(description="Revisa un carrusel con las reglas medibles.")
    p.add_argument("carpeta")
    p.add_argument("--palabra", help="palabra del cierre (si no, la toma de carrusel.json)")
    p.add_argument("--activas", default="marca/palabras-activas.txt", help="una palabra activa por renglón")
    p.add_argument("--handle", help="el @ (si no, el HANDLE de carrusel.json)")
    p.add_argument("--plataforma", choices=["instagram", "tiktok"], default="instagram")
    p.add_argument("--png", help="carpeta de los PNG (por defecto <carpeta>/png)")
    p.add_argument("--sin-png", action="store_true", help="no revisa los PNG (antes del render)")
    args = p.parse_args(argv)
    errores, avisos, info = revisar_todo(Path(args.carpeta), args)
    for etiqueta, lista in (("INFO", info), ("AVISO", avisos), ("ERROR", errores)):
        for linea in lista:
            print(f"{etiqueta}: {linea}")
    print("RESULTADO:", "con errores" if errores else "sin errores medibles; ahora mira cada PNG")
    return 1 if errores else 0


if __name__ == "__main__":
    sys.exit(main())
