#!/usr/bin/env python3
"""Genera slides/slide-NN.html de un carrusel a partir de su carrusel.json.

Uso:
  python3 build.py <carpeta-del-carrusel> [--marca marca/marca.css] [--plataforma instagram|tiktok]

Todas las slides salen del mismo CSS, cabecera y pie, así nada varía entre ellas y cada cambio se hace en
un solo lugar. Si queda un {{CAMPO}} sin llenar no escribe nada y dice cuál falta. El formato de
carrusel.json está en references/build.md.
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

PLANTILLAS = Path(__file__).resolve().parent.parent / "assets" / "plantillas"
MAX_SLIDES = 20
CAMPO = re.compile(r"\{\{([A-Z0-9_]+)\}\}")
BLOQUE = re.compile(r"<!--\?([A-Z0-9_]+)-->(.*?)<!--/\?\1-->", re.S)
FUENTES = re.compile(r"https://fonts\.googleapis\.com/\S+?(?=\s|\*/|$)")
RUTA_LOCAL = re.compile(r"""(?:src=["']|url\(['"]?)(?!https?:|data:|file:|#|%23)([^"')]+)""")
CARPETA_SALIDA = {"instagram": Path("slides"), "tiktok": Path("tiktok") / "slides"}


class ErrorDeCarrusel(Exception):
    """El carrusel no se puede construir; el mensaje dice qué arreglar."""


def quitar_bloques(html, conservar):
    """Borra los bloques <!--?NOMBRE-->...<!--/?NOMBRE--> que no se piden y deja el contenido de los pedidos."""
    return BLOQUE.sub(lambda m: m.group(2) if m.group(1) in conservar else "", html)


def poner_clase(html, clase):
    return html.replace('<div class="slide"', f'<div class="{clase}"', 1)


def llenar(html, campos, pasadas=3):
    """Reemplaza los {{CAMPO}}. Varias pasadas porque un valor puede traer otro campo, como {{RAIZ}}."""
    for _ in range(pasadas):
        nuevo = CAMPO.sub(lambda m: str(campos[m.group(1)]) if m.group(1) in campos else m.group(0), html)
        if nuevo == html:
            break
        html = nuevo
    return html


def pendientes(html):
    return sorted(set(CAMPO.findall(html)))


def fuentes_de_marca(marca_css):
    encontrada = FUENTES.search(marca_css)
    return encontrada.group(0) if encontrada else ""


def leer(ruta, que):
    try:
        return Path(ruta).read_text(encoding="utf-8")
    except FileNotFoundError:
        raise ErrorDeCarrusel(f"no encuentro {que}: {ruta}") from None


def cargar_spec(carpeta):
    try:
        return json.loads(leer(carpeta / "carrusel.json", "carrusel.json"))
    except json.JSONDecodeError as e:
        raise ErrorDeCarrusel(f"carrusel.json no es JSON válido: {e}") from None


def slides_de_plataforma(spec, plataforma):
    """Las slides y los campos comunes de esa plataforma. TikTok cambia el handle y el cierre."""
    slides, comunes = list(spec.get("slides", [])), dict(spec.get("campos_comunes", {}))
    if plataforma == "instagram":
        return slides, comunes
    tiktok = spec.get("tiktok")
    if not tiktok or "cierre" not in tiktok:
        raise ErrorDeCarrusel('para --plataforma tiktok, carrusel.json necesita "tiktok": {"campos_comunes", "cierre"}')
    comunes.update(tiktok.get("campos_comunes", {}))
    return slides[:-1] + [tiktok["cierre"]], comunes


def molde_de(slide, spec, carpeta, plantillas):
    if "molde" in slide:
        return leer(carpeta / slide["molde"], "el molde")
    if not spec.get("formato") or "plantilla" not in slide:
        raise ErrorDeCarrusel('cada slide necesita "plantilla" (con "formato" arriba) o "molde"')
    return leer(plantillas / spec["formato"] / f"{slide['plantilla']}.html", "la plantilla")


def armar(molde, slide, campos, css):
    html = quitar_bloques(molde, slide.get("bloques", []))
    html = html.replace("/*==BASE==*/", css["base"]).replace("/*==MARCA==*/", css["marca"])
    if slide.get("clase"):
        html = poner_clase(html, slide["clase"])
    return llenar(html, campos)


def imagenes_faltantes(html, carpeta_slides):
    # normpath: la carpeta de slides puede no existir todavía y «slides/../imagenes» no resolvería
    return [r for r in RUTA_LOCAL.findall(html)
            if r.strip() and not Path(os.path.normpath(carpeta_slides / r)).exists()]


def css_de(molde_usa_marca, marca, plantillas):
    marca_css = ""
    if molde_usa_marca:
        marca_css = leer(marca, "el archivo de marca (marca/marca.css; pásalo con --marca)")
    return {"base": leer(plantillas / "base.css.txt", "base.css.txt"), "marca": marca_css}


def construir(carpeta, marca, plataforma, plantillas=PLANTILLAS):
    """Valida todo el carrusel y, solo si no hay errores, escribe las slides. Devuelve (archivos, avisos)."""
    carpeta = Path(carpeta)
    spec = cargar_spec(carpeta)
    slides, comunes = slides_de_plataforma(spec, plataforma)
    if not 1 <= len(slides) <= MAX_SLIDES:
        raise ErrorDeCarrusel(f"un carrusel lleva de 1 a {MAX_SLIDES} slides; este trae {len(slides)}")
    moldes = [molde_de(s, spec, carpeta, plantillas) for s in slides]
    css = css_de(any("/*==MARCA==*/" in m for m in moldes), marca, plantillas)
    salida = carpeta / CARPETA_SALIDA[plataforma]
    raiz = "/".join([".."] * len(CARPETA_SALIDA[plataforma].parts))
    base = {"FUENTES_URL": spec.get("fuentes_url") or fuentes_de_marca(css["marca"]), "RAIZ": raiz,
            "TOTAL": len(slides), **comunes}
    htmls, errores, avisos = [], [], []
    for n, (slide, molde) in enumerate(zip(slides, moldes), 1):
        html = armar(molde, slide, {**base, "N": n, **slide.get("campos", {})}, css)
        faltan = pendientes(html)
        if faltan:
            errores.append(f"slide {n:02d}: falta llenar {', '.join(faltan)}")
        avisos += [f"slide {n:02d}: no está la imagen {r}" for r in imagenes_faltantes(html, salida)]
        htmls.append(html)
    if errores:
        raise ErrorDeCarrusel("\n".join(errores))
    salida.mkdir(parents=True, exist_ok=True)
    archivos = []
    for n, html in enumerate(htmls, 1):
        archivo = salida / f"slide-{n:02d}.html"
        archivo.write_text(html, encoding="utf-8")
        archivos.append(archivo)
    return archivos, avisos


def main(argv=None):
    p = argparse.ArgumentParser(description="Genera las slides HTML de un carrusel desde carrusel.json.")
    p.add_argument("carpeta", help="carpeta del carrusel (la que tiene carrusel.json)")
    p.add_argument("--marca", default="marca/marca.css", help="CSS de la marca (por defecto marca/marca.css)")
    p.add_argument("--plataforma", choices=sorted(CARPETA_SALIDA), default="instagram")
    args = p.parse_args(argv)
    try:
        archivos, avisos = construir(Path(args.carpeta), Path(args.marca), args.plataforma)
    except ErrorDeCarrusel as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    for aviso in avisos:
        print(f"AVISO: {aviso}")
    print(f"OK: {len(archivos)} slides en {archivos[0].parent}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
