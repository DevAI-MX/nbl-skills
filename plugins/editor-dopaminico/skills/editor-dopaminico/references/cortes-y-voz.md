# Cortes, transcripción y encuadre

## La cadencia
El guion tiene que sonar dicho de corrido, sin respiraciones nerviosas: más de medio segundo de silencio rompe la
retención. Desde el 2-nov **todo corte nuevo se compacta** (y el 4-nov se reafirmó: siempre con los valores por
defecto, tomas completas, sin recortar dentro de la frase).

| Caso | Cómo se corta | Pausa que queda |
|---|---|---|
| Por defecto (yapping, crudo, pantalla partida, lista y todo corte nuevo) | Corte compactado: solo queda la voz (envolvente por encima de -24 dB del nivel alto de la voz); todo hueco de más de 0.16 s se quita | ~0.13 s (0.08 s de cola + 0.05 s de arranque), fundido de 12 ms en cada tramo |
| Talkinghead por JSON (dopamínico, dos líneas, salud, marca) | Cadencia con umbral relativo (abajo) | La que fije el formato: pausa máxima 0.28 s que se deja en 0.22 s (salud 0.40 / 0.30; lenta 0.55; jazz 0.42) |
| Tarjeta sobre negro | Umbral -32 dB y pausa de 1.2 s, luego recorte por energía escondido en b-roll | Entre frases ~0.3 s, a mitad de frase ~0.12 s; las pausas dramáticas se quedan |
| Anuncio hablado de otra persona que pide «no le hagas cortes» | Sin cortes | Las suyas |

`scripts/cortes.py compactar voz.wav` aplica el corte compactado y devuelve los tramos y la pausa más larga que queda;
`scripts/cortes.py filtro cortes.json` da el `filter_complex` de ffmpeg con los fundidos de 12 ms.

## Por qué nunca se corta con los tiempos de Whisper
Whisper marca inicios y finales corridos entre 0.1 y 0.6 s: alarga el final de cada palabra hasta bien entrado el
silencio (un hueco real de 0.9 s lo mide como 0.2 s), adelanta la primera palabra de cada segmento y alucina palabras
en los silencios («gracias», «¿vale?»). Un corte con sus tiempos más un margen fijo cae dentro de una palabra o arrastra
el arranque de la siguiente. Ejemplo real: «Y yo sí sentí» empezaba en 109.60 y no en 109.50 (lo de 109.50 era la cola
de la palabra anterior). Tampoco sirve un umbral **absoluto** de silencio: en un video de dos minutos dejó pasar 14 s de
silencio (29 pausas de más de 0.3 s, con picos de 0.88 s) sin quejarse. Se mide la energía del audio.

## Cómo se corta en el silencio real

### Bordes de cada frase o toma elegida (`scripts/cortes.py bordes`)
1. Envolvente RMS del audio original cada 10 ms.
2. **Fin de frase:** hacia adelante, el primer silencio real (al menos **80 ms seguidos bajo -38 dBFS**, con el piso de
   la sala en ~-50) antes de la palabra siguiente, sin cruzarla. Si no hay (habla de corrido), el corte va en el hueco
   más hondo entre las dos palabras: casi siempre existe uno de ~30 ms.
3. **Inicio de frase:** lo mismo hacia atrás.
4. Si dos frases del guion van seguidas en el original, déjalas juntas en un solo tramo: un corte menos.
5. Si algo raro suena al final de un tramo, transcribe ese trozo solo para decidir si es palabra o respiración.

### Cadencia con umbral relativo (pipeline de talkinghead por JSON)
- El nivel de la voz es el **percentil 92** de la envolvente (ventana de 20 ms); es silencio lo que baja de
  **0.09 veces** ese nivel (~-21 dB). Así da igual si se grabó bajo o alto, o en otra habitación.
- De cada silencio más largo que la pausa máxima del formato se quita el **centro** y se deja la pausa del formato;
  nunca los bordes, para no comerse la consonante final ni el ataque de la palabra siguiente.
- **Islas:** dentro de un silencio, cualquier repunte por encima de 0.045 veces el nivel de voz (~-27 dB) que dure
  80 ms o más es una palabra dicha flojito («sí», «ya», «mira»): el hueco se parte ahí y la palabra se respeta.
- **Guarda de borde:** el empalme se encoge (de 20 en 20 ms) hasta que los dos bordes estén por debajo de 0.14 veces el
  nivel de voz.
- Un sonido sostenido tras una palabra puede ser la palabra alargada («mierdaaa»): no se corta.

### Tomas y retomas
- **Transcribe cada toma por separado**, partiendo el audio por sus silencios reales (silencio de al menos 0.35 s, voz
  de al menos 0.25 s, umbral 9 dB sobre el piso de la sala, que es el percentil 10 de la envolvente):
  `scripts/cortes.py partir voz.wav`. Whisper sobre el archivo entero se come las repeticiones y junta dos intentos en
  una sola frase. Transcribe cada tramo con 0.08 s de margen a cada lado.
- **Márgenes de cada toma elegida** (`scripts/cortes.py elegir voz.wav tomas.json --elegidas '[0, 2]'`): se conservan
  **0.07 s de silencio real antes y 0.11 s después** de la toma, sin pasar nunca de la mitad del hueco con la toma vecina
  del original. Si se toma solo un trozo (`[indice, palabra_ini, palabra_fin]`), el corte cae en el instante más callado
  entre las dos palabras (buscado de 30 ms antes del fin de una a 30 ms después del inicio de la otra).
- Elige tomas contra el guion; de las tomas repetidas se queda la buena. Un fragmento de menos de 1.2 s que se parece
  al siguiente (similitud de texto de 0.6 o más) es un arranque fallido y se descarta. Nunca armes una palabra con
  sílabas de otra toma.
- **Tomas completas: no recortes palabras dentro de una toma** (cortaba en plena voz).

### Verificación de cada corte
- Mide el nivel en cada unión del video cortado: tiene que pasar por **-40 dBFS o menos**
  (`scripts/cortes.py uniones corte.wav cortes.json`). Es la regla que quedó escrita el 25-oct; ese mismo día, en el
  video que la originó, las 11 uniones midieron -44 dB o menos: -44 es lo que salió en esa medición, -40 es el umbral
  para aprobar. Una unión por encima de -30 dB es un corte sobre la voz.
- Re-transcribe el corte completo y compara palabra por palabra: ninguna palabra a medias.
- Corte cuadro-exacto para clips a 29.97: `trim` + `fps=30` + `trim end_frame` y `atrim` a la misma duración.
- Tras muchos recortes, comprueba con `ffprobe` que audio y video duran lo mismo (cuadros enteros contra audio exacto
  dieron 0.2 s de desfase de labios).

## Inicio y final del video
- **El video empieza justo cuando la persona empieza a hablar.**
- El final lo marca la cola de la voz medida (Whisper da la frase por terminada antes y se come la última palabra), con
  un desvanecido de ~0.15 s. Cuánto aire queda después y cómo cierra (fundido a negro, negro con fundido de música o
  corte seco) lo dice cada formato en `formatos.md`.
- Recorta los restos de cuando la persona se sienta o se levanta: nunca debe verse ese cuadro.

## Cortes que no se ven
- En formatos con b-roll, cada corte del plano principal va **dentro** de un b-roll o en un cambio de clip, y la frase
  arranca en el corte. Si no se puede tapar, no recortes esa pausa.
- Si un b-roll o un gráfico termina a 1-2 s de un corte, alárgalo hasta el corte.
- El cambio de clip cae al inicio de un subtítulo nuevo, nunca a media línea visible.

## Zooms (cuál manda)
Las versiones fueron cambiando; manda la del formato:
- **Dopamínico y dos líneas:** zooms ligeros y lentos, «premium» (25/26-ago; reemplaza a los punches secos de 10-12 %
  que se rechazaron con la primera edición y a los de 12 %/5 % del 17-ago). Golpe de 4.5 % en rampa de 1.2 s; variante
  lenta 2.8 % en 3.4 s; jazz 3.6 % en 3 s. El gancho abre con zoom out (1.55 a 1.0 en 0.62 s, o 1.75 en 0.55 s).
- **Receta dopamínica con kit de cliente:** un solo movimiento en todo el video, zoom out de 155 % a 100 % en 0.3 s.
- **Salud:** punch de 1.00 a 1.08 en los cortes.
- **Tarjeta:** zoom in lento solo en el primer plano de cara, anclado en la cara.
- **Sin zooms:** reflexivo, crudo, yapping, narrador halftone (si el plano ya está bien encuadrado).
- En cualquier formato, un efecto visual que la referencia no usa se propone en un cuadro antes de aplicarlo: al medir
  una referencia que «tenía estímulos» había 6 cortes en 28.8 s y cero zooms; el ritmo lo llevaba la música.
- En motores por HTML no se anima el `<video>`: se hace zoom sobre un envoltorio.

## Transcripción
- Whisper large-v3 en español con tiempos por palabra y `condition_on_previous_text` desactivado, más un prompt inicial
  con los nombres propios. Un solo proceso de transcripción a la vez. Cómo instalarlo: «Requisitos» en `SKILL.md`.
- Sin `condition_on_previous_text` desactivado, Whisper entra en bucles con música, silencios o aplausos (una frase
  repetida cientos de veces). Compruébalo: la línea no vacía más repetida del texto no debe pasar de ~5
  (`grep -v '^$' salida.txt | sort | uniq -c | sort -rn | head`).
- Corrige el texto sin mover los tiempos (por ejemplo, un término médico que Whisper oye mal). Pega a la palabra
  anterior los signos que Whisper deja sueltos («80» «%» → «80%»).
- Si la voz viene muy baja, súbela antes de transcribir: con -57 dB alucina.

## Encuadre
- La cabeza siempre completa, con aire arriba y un poco de torso; la banda centrada. Si hay que recortar o meter el plano
  en un marco, colócalo por la cara detectada (YuNet u otro detector), no por el centro geométrico, que corta la cabeza.
- La iluminación de la grabación se deja tal cual.
- Fuentes 4K/60 o 1440x2560 se precortan a 1080x1920 con lanczos, CRF 16, preset slow.
