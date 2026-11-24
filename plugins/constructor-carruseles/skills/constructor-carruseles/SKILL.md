---
name: constructor-carruseles
description: >
  Úsala cuando alguien quiera un carrusel orgánico de Instagram listo para subir, para su marca o la de un
  cliente: «hazme un carrusel», «carrusel para Instagram sobre…», «convierte este transcript o este reel en
  slides», «carrusel viral de…», «quiero uno como este carrusel de @cuenta», «adapta este carrusel a mi
  marca», «transcribe este carrusel», «dame los prompts de cada slide para ChatGPT», «cambia la portada»,
  «hazlo en estilo tuit, noticia, limpio o pantalla partida», «haz la versión para TikTok», o cuando pase el
  enlace o las capturas de un carrusel ajeno para hacer su versión. No la uses para tarjetas de anuncio
  pagado que van a Ads Manager ni para escribir solo el guion de un reel.
---

# Constructor de carruseles

## Overview
Carruseles de Instagram de principio a fin: se entiende a la persona y su marca, se elige el formato, se
escribe el texto con reglas de retención, se genera el HTML con `scripts/build.py` desde plantillas propias
y se exportan PNG 1080x1350 (4:5) al doble de resolución. Cuando el carrusel nace de una referencia viral,
primero se baja y se entiende **por qué funciona** (ficha de concepto) y luego se rehace en la marca de la
persona con el gancho tal cual. Un carrusel funciona cuando la portada detiene el dedo, cada slide empuja al
siguiente y el último dice qué hacer.

En este documento, «la carpeta de la skill» es donde está este SKILL.md y «la carpeta de trabajo» es donde
la persona abrió Claude Code.

## When to Use
- Carrusel nuevo desde un tema, una idea, un transcript o un video.
- Versión propia de un carrusel de otra cuenta (referencia), o solo su transcript.
- Prompts para que la persona genere las imágenes en un generador (ChatGPT, Codex u otro).
- Cambios sobre un carrusel ya hecho (portada, un slide, colores) o su versión para TikTok.
- **Cuándo NO usarla:** creativos para anuncios pagados (otra skill arma esas tarjetas con su flujo de
  anuncio), investigar qué carruseles son virales (eso es investigación) o escribir guiones de video.

## Configuración personal (opcional)
Si en la carpeta de esta skill hay un archivo `*.local.md`, léelo al empezar: ahí cada quien guarda su
marca, sus rutas y sus formatos aprobados. Si en la carpeta de trabajo existe `marca/perfil.md`, también.
Los dos son solo tuyos: no se comparten con la skill.

## El orden es fijo
1. Conocer a la persona y su marca (solo la primera vez).
2. Tema, referencia y formato.
3. Escribir el texto y que la persona lo apruebe.
4. Generar los slides con `build.py` (o escribir los prompts de imagen).
5. Sacar las imágenes.
6. Revisar con `revisar.py`, mirar cada PNG y entregar.

No saltes pasos. Si la persona da todo de golpe, igual confirma el texto antes de diseñar: rehacer texto
sobre slides ya diseñados cuesta el doble.

## Paso 1. Conocer a la persona (solo la primera vez)
Si existe `marca/perfil.md` en la carpeta de trabajo, léelo y pasa al paso 2. Si no, pregunta en una sola
tanda: qué contenido hace y de qué tema; a quién le habla (situación, qué le preocupa, qué quiere); a
quién le vende y qué; su @ y nombre de perfil (y si tiene verificado; si tiene otro @ en TikTok); colores y
fuentes de su marca (si no tiene, le propones dos opciones); foto de perfil si quiere el formato tuit; y si
regala algo al final y con qué palabra se lo piden.

Con las respuestas escribe `marca/perfil.md` siguiendo `references/perfil-ejemplo.md` y `marca/marca.css`
con las mismas variables de `assets/plantillas/base.css.txt` (y en un comentario arriba, la URL de Google
Fonts). Crea `marca/palabras-activas.txt` con las palabras de los carruseles que ya tiene publicados (una
por renglón). Haz una portada de prueba en formato tipográfico, sácale la imagen y enséñasela antes de
seguir.

## Paso 2. Tema, referencia y formato
El tema llega como idea, transcript (saca 5 a 8 ideas y quédate con las más fuertes) o **referencia**: el
enlace o las capturas de un carrusel de otra cuenta. Con referencia, lee `references/referencias.md` y
sigue su flujo:
1. Baja las láminas y el caption con `scripts/bajar_referencia.mjs` (uno o varios enlaces; ficha con sesión
   con `--cdp` si hay un navegador de investigación con sesión, si no el lector sin sesión) y entrega el
   transcript slide por slide. A veces no baja nada: prueba la otra vía o pide capturas.
2. Escribe `CONCEPTO.md`: por qué funciona el gancho, la mecánica, por qué se ve de buen gusto, el molde
   interior y, lámina por lámina, texto literal, texto adaptado, concepto de imagen y captura a sacar.
3. Solo entonces escribe.

Si la persona no trae referencia y quiere una, se eligen por **comentarios**, no por likes. Las noticias,
solo de pocos días atrás y con fuente verificable: sin fuente no se construye.

Enséñale los formatos de `references/formatos.md` con las muestras de `assets/muestras/` y recomienda uno
según el tema (`references/formatos-extra.md` trae la técnica de otros formatos probados). Ella elige. Un
carrusel usa un solo formato de principio a fin y cada carrusel tiene su propio mundo visual.

## Paso 3. Escribir el texto
Sigue `references/reglas-del-carrusel.md`. Escribe slide por slide en una tabla (número, rol del slide,
texto) y enséñasela. No diseñes nada hasta que la apruebe.

Las reglas que más se rompen:
- **Gancho de una referencia: tal cual.** Palabra por palabra; solo el voseo o los regionalismos pasan a
  español neutro («Dejá» a «Deja») o se traduce si viene en otro idioma. No se mejora ni se acorta.
- **El resto, para que lo entienda un niño de 10 años:** mismo contenido y mismo orden que la referencia,
  en español neutro, humanizado como platicado, frases cortas y comparaciones cotidianas.
- **Pocas palabras por lámina interior:** título de 14 como máximo y cuerpo de 30; unas 9 cuando la lámina
  enseña un resultado visual.
- **Cero cifras, resultados, testimonios o capturas inventados.** Los números salen de lo que la persona
  te dio o de sus capturas. Las cifras de la cuenta de referencia no pasan a su carrusel.
- **El regalo del cierre resuelve exactamente lo que promete el gancho** y tiene que existir. Si el gancho
  habla de que nadie te escribe, el regalo son los mensajes listos, no «una asesoría». Si el recurso no
  existe, dilo y ofrece armarlo; no prometas guías, clases ni plantillas que no hay.
- **La palabra del cierre es única** entre los carruseles activos (revísala contra
  `marca/palabras-activas.txt`).

## Paso 4. Generar los slides
Crea `carruseles/AAAA-MM-DD_tema/` con `imagenes/` y `mis-capturas/`. Escribe ahí `carrusel.json` con el
formato, los campos comunes (el @) y cada slide con su plantilla y sus campos, siguiendo
`references/build.md`. Después, siempre:

```bash
python3 "<carpeta de la skill>/scripts/build.py" "carruseles/AAAA-MM-DD_tema"
```

Escribe `slides/slide-01.html`, `slide-02.html`, etc., todos con el mismo CSS (`base.css.txt` más
`marca/marca.css`, pegados dentro del archivo), la misma cabecera y el mismo pie. Si queda un `{{...}}`
sin llenar, no escribe nada y dice cuál falta. Para formatos sin plantilla, o para copiar el molde interior
de una referencia, usa un `"molde"` propio: nunca se maqueta slide por slide a mano.

Resalta una o dos palabras por título con `<span class="acento-txt">`, `<span class="serif">` o, en el
limpio, `mk-*` (marcatexto) y `cr-*` (crayón). Las plantillas no llevan flecha de «desliza», número de
slide ni etiquetas encima del título, y el @ va una sola vez por slide. El cierre con regalo lleva siempre
el bloque `RECURSO`, que enseña la hoja borrosa del recurso con su título y su sello.

**Imágenes de contexto** (una persona en su trabajo, una escena, un objeto, un estilo) no se maquetan con
HTML: se generan con prompts siguiendo `references/prompts-de-imagen.md` y el HTML pone encima el texto
exacto. Si la persona prefiere generar todos los slides ella (letra a mano sobre su libreta, estilos que
no se hacen en HTML), en lugar de slides entrega `PROMPTS.md` (y `CODEX.md` si usa un agente que lee
archivos).

## Paso 5. Sacar las imágenes
La primera vez, en la carpeta de trabajo: `npm init -y && npm install playwright && npx playwright install chromium`.
Si prefiere usar un navegador instalado, sáltate la última línea y pon su ruta en `BRAVE_PATH` (Brave) o
`BROWSER_PATH` (Chrome u otro).
Corre el render desde la carpeta donde quedó `node_modules/playwright`.

```bash
node "<carpeta de la skill>/scripts/render.mjs" --slides "carruseles/AAAA-MM-DD_tema/slides" --out "carruseles/AAAA-MM-DD_tema/png" --preview "carruseles/AAAA-MM-DD_tema/preview.html"
```

Sale un PNG de 2160x2700 por slide en `png/` y un `preview.html` en la carpeta del carrusel con todos en
cuadrícula, portada incluida.

## Paso 6. Revisar y entregar

```bash
python3 "<carpeta de la skill>/scripts/revisar.py" "carruseles/AAAA-MM-DD_tema"
```

Con errores no se entrega. Después mira cada PNG (no solo el HTML) y pasa la lista final de
`references/reglas-del-carrusel.md`: nada se sale ni se encima, sin palabras sueltas al final de un
renglón, números de las capturas legibles, copy idéntico al aprobado palabra por palabra. Lee
`references/verificacion.md` para los errores comunes, el recorte 4:5 de portadas hechas en un generador
(`scripts/recortar_45.py`) y el editor de portada.

Entrega la ruta de la carpeta con los PNG en orden y ábrele el `preview.html` y la carpeta. Di cuántas
slides, qué formato y por qué, qué cambió en esta ronda y un texto para la descripción del post (la primera
línea repite la promesa del gancho y al final va la misma palabra del cierre). Di qué no pudiste verificar
y qué falta para publicar: el recurso del cierre, la palabra configurada en la herramienta de mensajes
automáticos (también sin acento, por ejemplo «CÓDIGOS» y «CODIGOS»), cifras sin respaldo.

**Versión para TikTok** (si la pide): agrega el bloque `tiktok` a `carrusel.json` (su @ de TikTok y un
cierre de «guarda y sígueme», sin regalo) y corre `build.py` y `render.mjs` con la carpeta `tiktok/`
(`--plataforma tiktok`). Las variantes de portada o de cierre van en `alt-portadas/` y `alt-cta/`.

**Si quiere encuadrar ella la portada**, copia `assets/editor-portada.html` a la carpeta del carrusel y
ábreselo; ella te pasa `{x, y, zoom, font, bottom}` y tú los horneas en la portada.

Si piden cambios, cambia **solo lo que pidieron y donde lo pidieron** (si dice «solo la primera slide», no
toques las demás); las versiones nuevas van en carpeta o archivo aparte y las anteriores no se borran.

## Lo que nunca haces
- Inventar cifras, testimonios, resultados, capturas ni interfaces.
- Cambiar el gancho de una referencia o cortar las frases importantes de su copy.
- Copiar el diseño de la referencia tal cual (la misma imagen recoloreada, el mismo encuadre).
- Usar colores o fuentes fuera de la marca de la persona, aunque la referencia o el prompt usen otros.
- Simular letra a mano con una fuente: se ve de plantilla. La letra a mano es la real de la persona (foto
  de su libreta) o no va.
- Usar cuadros recortados al azar de videos de la persona, o su cara generada por IA.
- Poner flecha de «desliza», número de slide, etiquetas encima del título o el @ repetido (salvo que la
  referencia los traiga en ese lugar).
- Achicar el margen para que quepa el texto: se quitan palabras o se baja un poco la letra.
- Repetir la misma imagen en dos slides, o la foto de la portada en el cierre.
- Publicar, mandar mensajes o configurar la herramienta de respuestas automáticas: solo recuerdas la palabra.
- Poner fotos fotorrealistas generadas de personas reales en escenas que no pasaron.

## Recursos
- `references/formatos.md`: los 6 formatos con plantilla y cómo recomendar.
- `references/formatos-extra.md`: técnica exacta de otros formatos probados (limpio v2, noticia, texto de
  editor de Instagram, chat, editorial, marcador, lista de comandos, libreta, encabezado de perfil, cierres).
- `references/reglas-del-carrusel.md`: reglas de texto y diseño, lo que los virales no hacen y la lista final.
- `references/referencias.md`: bajar una referencia, ficha de concepto, gancho tal cual y diseño.
- `references/prompts-de-imagen.md`: prompts copiar y pegar para generar slides o imágenes, y `CODEX.md`.
- `references/build.md`: el formato de `carrusel.json`.
- `references/verificacion.md`: revisión, recorte 4:5, fotos, editor de portada y errores ya resueltos.
- `references/perfil-ejemplo.md`: plantilla de `marca/perfil.md`.
- `assets/plantillas/`: base.css.txt y portada, contenido y cierre de cada formato. `assets/muestras/`: una
  muestra por formato. `assets/editor-portada.html`: editor de encuadre de la portada.
- `scripts/build.py`: genera las slides desde `carrusel.json` (Python 3.9+, sin dependencias).
- `scripts/render.mjs`: HTML a PNG 2160x2700 más `preview.html` (Node 18+ y Playwright).
- `scripts/revisar.py`: revisión medible antes de entregar (Python 3.9+, sin dependencias).
- `scripts/bajar_referencia.mjs`: láminas, caption y datos de uno o varios carruseles de Instagram (Node 18+ y Playwright).
- `scripts/recortar_45.py`: recorte a 4:5 en 2160x2700 (Pillow).
- Pruebas, desde la carpeta de la skill: `python3 -m unittest discover -s scripts/tests` y
  `node --test "scripts/tests/*.test.mjs"` (con comillas, así lo expande Node; funciona de Node 21 a 26).
