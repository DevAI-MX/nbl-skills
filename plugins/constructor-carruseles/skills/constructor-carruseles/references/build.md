# carrusel.json y scripts/build.py

Todas las slides de un carrusel se generan con `scripts/build.py`, aunque sean pocas: así todas comparten
el mismo CSS, cabecera y pie, nada varía entre slides y un cambio se hace en un solo lugar. Nada de
copiar plantillas a mano ni de teclear recortes o SVG en cada slide.

```bash
python3 "<carpeta de la skill>/scripts/build.py" "carruseles/AAAA-MM-DD_tema" [--marca marca/marca.css] [--plataforma tiktok]
```

Lee `carrusel.json` de la carpeta del carrusel y escribe `slides/slide-NN.html` (o `tiktok/slides/` con
`--plataforma tiktok`). Si falta llenar un `{{CAMPO}}`, no escribe nada y dice cuál y en qué slide. Avisa si
una imagen enlazada todavía no está en la carpeta.

## Formato

```json
{
  "formato": "limpio",
  "fuentes_url": "https://fonts.googleapis.com/css2?family=Inter+Tight:wght@500;700&display=swap",
  "campos_comunes": {"HANDLE": "@tu_marca"},
  "slides": [
    {"plantilla": "portada", "bloques": ["VERIFICADO"], "campos": {"GANCHO": "Cómo escribir un <span class=\"mk-lima\">gancho</span>"}},
    {"plantilla": "contenido", "bloques": ["PASO", "CAPTURA"],
     "campos": {"PASO": "1", "CAPTURA": "{{RAIZ}}/mis-capturas/busqueda.png", "TITULO": "Busca tu tema en la lupa."}},
    {"plantilla": "cierre", "campos": {"TITULO": "Te mando los 30 ganchos", "ACCION": "Comenta:", "PALABRA": "GANCHOS", "QUE_RECIBE": "y te los envío por mensaje."}}
  ],
  "tiktok": {
    "campos_comunes": {"HANDLE": "@tu_marca_tiktok"},
    "cierre": {"plantilla": "cierre", "campos": {"TITULO": "Guárdalo para tu próximo post", "ACCION": "Y", "PALABRA": "SÍGUEME", "QUE_RECIBE": "para más como este."}}
  }
}
```

- `formato`: carpeta de `assets/plantillas/`. Cada slide usa `"plantilla"`: `portada`, `contenido` o `cierre`.
- `"molde"` en lugar de `"plantilla"`: un HTML propio, relativo a la carpeta del carrusel (por ejemplo
  `moldes/interior.html`), para formatos sin plantilla o para copiar el molde interior de una referencia.
  Puede usar `/*==BASE==*/`, `/*==MARCA==*/` y los mismos campos.
- `campos_comunes`: valen para todas las slides; los `campos` de cada slide mandan sobre ellos. Los
  valores pueden llevar HTML (para resaltar una o dos palabras).
- Campos automáticos: `{{FUENTES_URL}}` (de `fuentes_url` o del comentario de `marca/marca.css`),
  `{{RAIZ}}` (la ruta de la carpeta de slides a la del carrusel; úsala para las imágenes:
  `{{RAIZ}}/imagenes/foto.jpg`), `{{N}}` y `{{TOTAL}}`. Ninguna plantilla los usa para numerar slides.
- `bloques`: los bloques opcionales `<!--?NOMBRE-->...<!--/?NOMBRE-->` que se quedan; los que no se piden se
  borran. Cada plantilla dice en un comentario cuáles tiene.
- `clase`: cambia la clase del slide (por ejemplo `"slide claro"` en el tipográfico, `"slide noche"` en el tuit).
- `tiktok`: la versión para TikTok usa el mismo carrusel con su handle y su propio cierre (guardar y
  seguir, sin regalo; ese cierre va sin el bloque `RECURSO`).
- Cierre con regalo: pide `"bloques": ["RECURSO"]` y llena `RECURSO_TITULO` (el título del recurso, lo único
  legible), `RECURSO_SELLO` («PDF», «PLANTILLA») y `RECURSO_IMG` (la portada del recurso; si aún no existe,
  `""` y quedan renglones borrosos). `revisar.py` marca un cierre con palabra que no enseña el recurso.
- Formato `noticia`: pide `TINTE` (el color de arriba del degradado, de la herramienta de la que habla) en
  `campos_comunes`, y define el acento en `marca/marca.css` o en el `<style>` del molde.
- `"copia_paginacion_de_referencia": true`: solo cuando la referencia trae paginación o flecha y se copian
  en el mismo lugar; `revisar.py` entonces no lo marca como error.

## Datos en constantes
Si el carrusel lleva cifras reales de la persona (vistas, comentarios), van una vez en `carrusel.json` o en
un `datos.json` aparte, y los porcentajes se calculan, no se escriben a mano.

## Respaldo antes de rehacer un estilo
Antes de rehacer un carrusel en otro estilo, copia `carrusel.json` a `carrusel_v1.json` y `png/` a
`png_v1/`. Las versiones nuevas van en carpeta o archivo aparte; las anteriores no se borran.
