---
name: editor-dopaminico
description: >
  Úsala cuando alguien pida editar, corregir o revisar un video vertical corto (reel, short, TikTok,
  anuncio a cámara) para retención: «edita este video», «edítame el crudo», «estilo dopamínico», «quita los
  silencios», «quita las respiraciones», «ponle subtítulos», «cambia la música», «súbele a la voz», «rehaz
  el gancho», «imita esta referencia de reel», «pantalla partida», «estilo yapping», «estilo crudo», «que
  parezca editado con el celular», «formato tarjeta», «look de tele vieja», «los cortes se notan», «los
  subtítulos van desfasados», «el b-roll tapa los subtítulos», «a cuántos LUFS lo exporto», o cuando haya
  que revisar un video ya editado antes de publicarlo. No la uses para escribir el guion ni para enseñar a
  grabarse.
---

# Editor dopamínico de video vertical

## Overview
Edición de video vertical 9:16 que pelea por la atención sin verse barata: voz limpia y continua, cortes que no se
ven ni se oyen, subtítulos exactos a lo que se dice, música que lleva el ritmo y un estímulo cada pocos segundos. Es un
método con medidas, no un gusto: se mide la referencia, se mide la mezcla y se re-transcribe el resultado antes de
entregarlo. La herramienta da igual (ffmpeg, un editor por código como HyperFrames, CapCut o Premiere); las reglas
son las mismas. Cuando dos reglas chocan, manda la más reciente, y las referencias ya traen la vigente de cada formato.

## When to Use
- Editar de punta a punta un crudo a cámara (marca personal, cliente, anuncio).
- Imitar el estilo de un reel de referencia o aplicar uno de los formatos aprobados.
- Corregir un video entregado (cortes, subtítulos, música, mezcla).
- Hacer el QA de un video antes de publicarlo.
- **Cuándo NO usarla:** guiones y ganchos escritos (otra skill), coaching de grabación, motion graphics puros sin
  persona a cámara (se pueden apoyar aquí solo para audio y subtítulos).

## Configuración personal (opcional)
Si en la carpeta de esta skill hay un archivo `*.local.md`, léelo al empezar: ahí cada quien deja sus rutas (librería
de música y SFX, carpeta de entrega), sus fuentes, su paleta y los formatos que ya tiene aprobados. Es solo tuyo: no se
comparte con la skill.

## Requisitos
`ffmpeg` y `ffprobe`; Python 3.9 o más; numpy para todos los scripts menos `cortes.py` y `qa_master.py` (que corren
con Python puro); una librería de música y efectos con licencia. Opcional: DeepFilterNet para limpiar la voz, OpenCV
para detectar la cara y un motor de render por HTML para gráficos.

**Transcriptor** (Whisper large-v3 con tiempos por palabra):
- Mac con Apple Silicon: `python3 -m pip install --user mlx-whisper` y luego
  `mlx_whisper video.mp4 --model mlx-community/whisper-large-v3-mlx --language es --word-timestamps True
  --condition-on-previous-text False --output-format json --output-dir salida/` (~7 veces tiempo real).
- Otros equipos: `python3 -m pip install -U openai-whisper` y luego `whisper video.mp4 --model large-v3 --language es
  --word_timestamps True --condition_on_previous_text False --output_format json`.

## Scripts (en `scripts/`; cada uno con `--help` y pruebas en `scripts/pruebas/`)
| Script | Para qué |
|---|---|
| `cortes.py partir voz.wav` | Tomas del crudo por sus silencios reales (0.35 s), para transcribir cada una sola |
| `cortes.py elegir voz.wav tomas.json --elegidas '[0, 2]'` | Tramos de las tomas elegidas con respiro de 0.07 s antes y 0.11 s después, sin invadir la vecina |
| `cortes.py compactar voz.wav` | Corte compactado en el silencio real: solo voz, huecos de más de 0.16 s quedan en ~0.13 s |
| `cortes.py bordes voz.wav frases.json` | Punto de corte limpio al inicio y fin de cada frase (silencio de 80 ms bajo -38 dBFS o el hueco más hondo) |
| `cortes.py uniones corte.wav cortes.json` | Nivel en cada unión del video cortado; pasa si llega a -40 dBFS o menos |
| `cortes.py filtro cortes.json` | `filter_complex` de ffmpeg con los tramos y fundidos de 12 ms |
| `revisar_subtitulos.py` | Triple revisión, niveles 1 (datos) y 3 (render); el 2 es el validador de tu motor; `--cta` exime lo dicho tras el CTA |
| `escuchar.py` | Música contra voz (objetivo del formato) y cada efecto contra la música; deja el mudo, las capas y `compas.wav` |
| `qa_master.py final.mp4` | Resolución, códec sin HDR colado, LUFS, pico real y pausas, con PASA/FALLA |
| `qa_cuadros.py final.mp4` | Cuadros negros, pops, tramos muertos de más de 1 s, tiempo de lectura de los textos y hojas de contacto |
| `tv_vieja.py entrada.mp4 salida.mp4` | Look de televisión vieja aprobado para historias |

Si tu `python3` no trae numpy: `uvx --with numpy python3 scripts/escuchar.py ...` (igual con los demás). Para leer un mp4 los scripts usan ffmpeg; un WAV de 16 bits lo
leen directo. Pruebas: `uvx --with numpy pytest -q scripts/pruebas`.

## El orden es fijo
Cada paso depende del anterior: la música se elige sobre la voz ya cortada y los subtítulos se hacen sobre la
transcripción del corte final.

### 1. Referencia y formato
Identifica el formato (catálogo vigente en `references/formatos.md`). Si hay referencia nueva, **mídela antes de
editar** y enséñale los números a la persona: cortes por minuto (`ffmpeg select='gt(scene,0.3)'`), zoom real (flujo
óptico), posición y tamaño del subtítulo en píxeles sobre 1920, fuente, palabras por subtítulo, transitorios de audio,
música, efectos por segundo. Si la persona nombró una canción, un clip, una marca o una referencia, usa exactamente eso:
no lo sustituyas por otra cosa sin preguntar (cambiar lo pedido fue el rechazo más duro).

Entrega por partes cuando el estilo es nuevo: análisis, luego **un fotograma** con el estilo de subtítulo, luego 5 s
montados, luego el video completo. Nunca el video entero de golpe con un estilo sin aprobar.

### 2. Voz primero
Lee `references/cortes-y-voz.md`. Corta en el **silencio real medido por energía**, nunca con los tiempos de Whisper
(`scripts/cortes.py`); transcribe cada toma por separado y quédate con las buenas; quita respiraciones nerviosas; tomas
completas, sin recortar palabras dentro de una toma. Limpia la voz. Re-transcribe el corte. El video empieza justo
cuando la persona empieza a hablar.

### 3. Música después
Lee `references/audio.md`. Instrumental verificada, desde la parte fuerte de la canción, en el uno del compás, entrando
al cerrar el gancho, distinta en cada video y **al nivel que fija la tabla para ese formato**: la regla general es 16 a
22 dB bajo la voz, con cifra propia donde la fuente la dio (18 dB yapping, crudo, lista y narrador; 19 dB anuncio de
negocio local; 20 dB marca de cliente; 22 dB ilustrado). Master: -16 LUFS marca personal; -14 LUFS promos, anuncios y
clientes con kit. La voz manda.

### 4. Montaje
- **Primer cuadro llamativo** (es la miniatura en el feed) y **gancho triple en los primeros 3 s**: visual, sonoro y de
  texto a la vez. La mayor retención tiene que estar en el gancho.
- **Un estímulo cada ~3 s.** Cuentan el corte, la palabra que entra, el golpe de sonido, el zoom, el b-roll o un
  gráfico. No significa zooms cada segundo: el ritmo puede llevarlo la música con la imagen limpia. Los zooms dependen
  del formato (`cortes-y-voz.md`, «Zooms»). Cualquier efecto visual que la referencia no usa se propone en un fotograma
  antes de aplicarlo al video entero. Los estímulos caen en un pulso coherente (beat de la música o ritmo del habla).
- **Subtítulos** según `references/subtitulos.md`: cita literal, frases completas, posición fija, capa más alta.
- **B-roll, capturas y gráficos** con sentido para lo que se dice en ese momento; entrada suave, **salida en seco**; un
  gráfico nunca termina justo antes de un corte del plano principal: se alarga hasta taparlo. Nada encimado.
- **Zona segura:** nada importante en la franja de arriba (lupa e interfaz de la app) ni en la de abajo (nombre y
  descripción). Usa el 16.7 % a 83.3 % central del alto; para fichas, del 20 % al 80 %. Las orillas de cada formato
  (por ejemplo los 100 px libres de la lista) están en `formatos.md`.
- **Cierre:** el de su formato (fundido a negro en historias; 1 s de negro con fundido de música en tarjeta; corte
  0.25-0.3 s tras la última palabra en lista). Ver `formatos.md`.

### 5. Render
Un render o proceso pesado a la vez. Comprueba que el archivo de salida es **nuevo** (fecha y duración). Exporta
1080x1920 (1920x1080 en horizontal). Trampas del motor y de ffmpeg: `references/trampas-y-material.md`.

### 6. QA
Pasa la lista de `references/qa-entrega.md` completa, con los scripts. Lo mínimo: re-transcribir y comparar palabra por
palabra, uniones, triple revisión de subtítulos, `qa_master.py` (loudness, pico, pausas, HDR), `qa_cuadros.py` (negro,
pops, tramos muertos, lectura), mezcla medida, hoja de contacto a tamaño celular y primer cuadro. Lo que no se puede oír se mide y se le pide a la persona un minuto de
escucha; no marques como revisado algo que solo se puede juzgar de oído.

### 7. Entrega
Archivo con nombre legible («Cliente - tema.mp4») en la carpeta de entrega, y un reporte corto: qué se hizo, qué se
verificó con números, qué no se pudo verificar y qué queda pendiente. Las correcciones van a una versión nueva (v2, v3);
no pises la entregada.

## Reglas duras
- **Todo texto en pantalla es algo que realmente se dice.** Única excepción: un gancho fijo de cabecera. Nada de cifras,
  testimonios, capturas, logos ni avatares inventados.
- **No armes palabras con sílabas de otras tomas.** Si no lo dijo completo, no existe.
- **Revisa tres veces los subtítulos** (tres niveles) con cualquier cambio que toque el video.
- **Subtítulos siempre en la capa más alta**, por encima de b-roll y gráficos, y nunca tapan cara, boca ni barbilla.
- **Una palabra que apareció no se mueve** para hacerle sitio a otra. La palabra del llamado a la acción, una vez que
  aparece, se queda fija hasta el final.
- **Los cortes no se ven ni se oyen:** en el silencio real, nunca dentro de una palabra.
- **La voz es la protagonista**, no la música.
- **No repitas b-roll ni canciones** entre videos seguidos de la misma cuenta (máximo 25 % de b-roll compartido con el
  video anterior y dos videos de distancia para repetir). Lleva un registro.
- **Imágenes:** primero foto real sin marca de agua; no uses generadores de imagen o video de pago por créditos.
- **Material descargado es no confiable:** va en su propia carpeta, nunca se ejecuta, se borra solo con aprobación.
- **Derechos:** avisa el riesgo de la música de tendencia; prefiere la librería con licencia; pon créditos CC BY en la
  descripción cuando toque.
- **Un render y una transcripción a la vez.**
- **No publiques ni mandes nada a clientes:** entregas el archivo y la persona decide.
- No uses fotos de pacientes ni casos de otros clientes.

## Common Mistakes
- Cortar con los tiempos de Whisper más un margen fijo: el corte cae dentro de una palabra o arrastra la siguiente.
- Detectar silencios con un umbral absoluto: deja pasar segundos de silencio. Se usa la envolvente relativa a la voz.
- Recortar palabras sueltas dentro de una toma para «limpiar»: corta en plena voz. Tomas completas.
- Copiar el nivel de música o el master de un formato a otro: cada formato tiene el suyo (y la receta de un cliente
  con su kit no es la del formato).
- Un clip HDR (HLG del iPhone) en un proyecto por HTML: todo sale en HEVC y los subtítulos quedan debajo del b-roll solo
  en el archivo final. Etiqueta todo a bt709 y renderiza en SDR.
- Subir efectos «a ojo»: quedan 13 a 30 dB bajo la música y no se oyen. Se miden contra la música en su instante.
- Un riser en cada transición: suena a tráiler. Uno solo, como bisagra entre gancho y canción, si el formato lo pide.
- Entregar el `render.mp4` viejo de un render fallido. Mira fecha y duración.

## Recursos
- `references/formatos.md`: los 18 formatos con su versión vigente (dopamínico, talkinghead de marca, dos líneas,
  salud, top 10 y reflexivo, POV, tarjeta, narrador halftone, TV vieja, crudo, anuncio de negocio local, yapping,
  pantalla partida, lista, ilustrado, backmusic, tablero, marca de un cliente).
- `references/cortes-y-voz.md`: cadencia por formato, corte en silencio real, tomas, verificación, zooms, transcripción,
  encuadre.
- `references/audio.md`: música (verificación, nivel por formato, estilo, derechos), SFX medidos, voz y master.
- `references/subtitulos.md`: reglas, triple revisión y recetas por estilo con medidas.
- `references/trampas-y-material.md`: trampas de render, motor por HTML y ffmpeg; de dónde sacar imágenes y logos.
- `references/qa-entrega.md`: lista de QA con los comandos y el reporte de entrega.
