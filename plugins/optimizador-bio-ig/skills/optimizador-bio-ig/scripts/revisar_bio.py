#!/usr/bin/env python3
"""Revisa las reglas medibles de una bio de Instagram.

Uso: python3 revisar_bio.py ARCHIVO   (o "-" para leer la bio de la entrada estándar)
Sale con 0 si no hay fallas, 1 si las hay y 2 si no pudo leer el archivo.
"""
import argparse
import re
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path

LINEAS_DE_LA_BIO = 3
GENERAL = 0

LLAMADA = r"(llamada|videollamada|sesion|consulta|asesoria|diagnostico|valoracion|evaluacion)"
GRATIS = r"(gratuit[ao]|gratis|sin costo|sin cargo)"
VOCABULARIO_PROHIBIDO = [
    (r"\bingresos?\b", 'palabra prohibida: "ingresos"'),
    (r"\bprocesos?\b", 'palabra prohibida: "proceso"'),
    (r"\bacompan\w*", 'palabra prohibida: "acompaño"'),
    (r"\bdescubre\b", 'palabra prohibida: "descubre"'),
    (r"\bpotencia\b", 'palabra prohibida: "potencia"'),
    (r"transforma tu vida", 'frase prohibida: "transforma tu vida"'),
    (r"en el mundo digital actual", 'frase prohibida: "en el mundo digital actual"'),
    (r"desbloquea tu potencial", 'frase prohibida: "desbloquea tu potencial"'),
    (r"si te interesa escribeme", 'CTA prohibido: "si te interesa, escríbeme"'),
    (r"si quieres info escribeme", 'CTA prohibido: "si quieres info, escríbeme"'),
    (r"\bavisame\b", 'CTA prohibido: "avísame"'),
    (
        rf"\b{LLAMADA}\b(\s+\w+){{0,3}}?\s+{GRATIS}\b|\b{GRATIS}\b(\s+\w+){{0,2}}?\s+{LLAMADA}\b",
        'CTA prohibido: "llamada gratuita", "gratis" o "sin costo"',
    ),
]
EMOJI = re.compile(
    "[\U0001F000-\U0001FAFF☀-➿⌚⌛⏩-⏬⏰⏳◽◾⬛⬜⭐⭕]"  # se ven como emoji por sí solos
    "|[^\\w\\s]\uFE0F"  # símbolo con selector de variación: ⬇️ ▶️
    "|[0-9#*]\uFE0F?\u20E3"  # keycap: 1️⃣
)
SOLO_LINK = re.compile(r"(https?://)?[\w-]+(\.[\w-]+)+(/\S*)?", re.IGNORECASE)
LINK = re.compile(r"(https?://)?[\w-]+\.[a-z]{2,}(/\S*)?", re.IGNORECASE)
MARCAS_DE_CODIGO = re.compile(r"```|font-|color:|<[a-z]+>", re.IGNORECASE)
ALCANCE = r"(seguidores?|followers?|suscriptores?)"
REDES = r"(ig|instagram|tiktok|youtube|redes)"
CIFRA = r"\d+(\s\d{3})*\s*(k|m|mil|millon|millones)?\b"
GENERADOS = r"(generados|ganados|conseguidos|logrados|(para|a|de) (mis|sus|los) clientes)"
CLIENTES = r"(alumnos|clientes|estudiantes|pacientes|socios|negocios|empresas)"
SEGUIDORES_COMO_PRUEBA = [
    re.compile(rf"{CIFRA}\s*(de\s+)?{ALCANCE}\b(?!\s+{GENERADOS})"),
    re.compile(rf"\b{ALCANCE}\s*\d"),
    re.compile(rf"\b(comunidad|familia|tribu) de (mas de )?{CIFRA}(?!\s*{CLIENTES})"),
    re.compile(rf"{CIFRA}\s*((personas|gente)\s+)?(me|nos)\s+siguen?\b"),
    re.compile(rf"\b(me|nos)\s+siguen?\s+(mas de\s+)?\d"),
    re.compile(rf"{CIFRA}\s+en\s+{REDES}\b"),
]
SEGUIDORES_DE_OTROS = re.compile(
    rf"\b((sus|tus)|a (ganar|generar|conseguir|sumar|alcanzar)"
    rf"|{CLIENTES}\s+(\w+\s+){{0,2}}?(ganado|ganaron|generado|generaron|conseguido|consiguieron|sumado|sumaron))"
    rf"\s+(\w+\s+){{0,3}}?{ALCANCE}\b"
)
PROMESA = re.compile(r"^(te )?ayudo\b")
SEPARADORES = re.compile(r"[|•·;]")
OTRA_CUENTA = re.compile(r"(?<![\w.])@[A-Za-z0-9_.]+")


@dataclass(frozen=True)
class Falla:
    linea: int
    regla: str
    cita: str = ""


def revisar(texto):
    if not texto.strip():
        return [Falla(GENERAL, "la bio está vacía")]
    numeradas = list(enumerate(texto.splitlines(), 1))
    return (
        _vocabulario(numeradas)
        + _lineas_de_contenido(numeradas)
        + _bio_completa(texto)
    )


def _vocabulario(numeradas):
    return [
        Falla(numero, regla, linea)
        for numero, linea in numeradas
        for patron, regla in VOCABULARIO_PROHIBIDO
        if re.search(patron, _normalizar(linea))
    ]


def _lineas_de_contenido(numeradas):
    contenido = [(n, l.strip()) for n, l in numeradas if _es_contenido(l)]
    fallas = []
    if len(contenido) > LINEAS_DE_LA_BIO:
        numero, linea = contenido[LINEAS_DE_LA_BIO]
        fallas.append(Falla(numero, f"la bio tiene {len(contenido)} líneas (máximo {LINEAS_DE_LA_BIO})", linea))
    if 0 < len(contenido) < LINEAS_DE_LA_BIO:
        fallas.append(Falla(GENERAL, "faltan líneas: la bio lleva 3 (ayuda, prueba social e invitación)"))
    for numero, linea in contenido:
        if not EMOJI.match(linea):
            fallas.append(Falla(numero, "la línea no empieza con emoji", linea))
        if _usa_seguidores_como_prueba(linea):
            fallas.append(Falla(numero, "seguidores usados como prueba", linea))
        if OTRA_CUENTA.search(linea):
            fallas.append(Falla(numero, "menciona otra cuenta: la bio no manda a cuentas secundarias", linea))
    return fallas


def _es_contenido(linea):
    limpia = linea.strip()
    return bool(limpia) and not limpia.startswith("```") and not SOLO_LINK.fullmatch(limpia)


def _bio_completa(texto):
    fallas = []
    if not LINK.search(texto):
        fallas.append(Falla(GENERAL, "no hay link en la bio"))
    if MARCAS_DE_CODIGO.search(texto):
        fallas.append(Falla(GENERAL, "la bio viene como código: debe ser texto plano"))
    return fallas


def _usa_seguidores_como_prueba(linea):
    """Presumir los seguidores propios («15K seguidores», «Comunidad de +15K») es alcance, no prueba,
    aunque venga junto a otra métrica.

    Sí valen los seguidores generados para clientes («+2M de seguidores generados para mis clientes»,
    «llevé a 40 alumnos a sus primeros 10k seguidores») y la promesa de la línea 1
    («Te ayudo a llegar a 10 mil seguidores»): eso es resultado, no alcance propio.
    """
    for tramo in SEPARADORES.split(linea):
        normalizado = _normalizar(tramo)
        if PROMESA.match(normalizado):
            continue
        propio = SEGUIDORES_DE_OTROS.sub(" ", normalizado)
        if any(patron.search(propio) for patron in SEGUIDORES_COMO_PRUEBA):
            return True
    return False


def _normalizar(texto):
    descompuesto = unicodedata.normalize("NFD", texto.lower())
    sin_acentos = "".join(c for c in descompuesto if unicodedata.category(c) != "Mn")
    sin_puntuacion = re.sub(r"[^\w\s]", " ", sin_acentos)
    return re.sub(r"\s+", " ", sin_puntuacion).strip()


def _imprimir(fallas):
    if not fallas:
        print("La bio pasó: sin fallas medibles.")
        return
    for falla in sorted(fallas, key=lambda f: f.linea):
        lugar = f"Línea {falla.linea}" if falla.linea else "General"
        print(f"{lugar}: {falla.regla}")
        if falla.cita:
            print(f"  > {falla.cita}")
    print(f"{len(fallas)} falla(s) por corregir.")


def _leer(archivo):
    if archivo == "-":
        return sys.stdin.read()
    return Path(archivo).read_text(encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Revisa las reglas medibles de una bio de Instagram.")
    parser.add_argument("archivo", help="archivo de texto con la bio, o - para leerla de la entrada estándar")
    args = parser.parse_args()
    try:
        texto = _leer(args.archivo)
    except (OSError, UnicodeDecodeError) as error:
        print(f"No pude leer {args.archivo}: {error}", file=sys.stderr)
        return 2
    fallas = revisar(texto)
    _imprimir(fallas)
    return 1 if fallas else 0


if __name__ == "__main__":
    sys.exit(main())
