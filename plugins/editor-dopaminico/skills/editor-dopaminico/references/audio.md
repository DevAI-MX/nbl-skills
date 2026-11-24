# Audio: voz, música, efectos y master

Orden fijado: 1) limpiar la voz, 2) elegir la música, 3) lo demás. La voz es la protagonista, no la música.

## Música

### Verificar y colocar
- **Instrumental verificada:** prueba de centro contra lados (resta un canal al otro); si el centro sale bajo, no hay
  voz cantada. Lo que se anuncia como instrumental a veces trae coros.
- **Desde la parte fuerte de la canción**, no desde la intro. El drop real se busca por energía, no por la rejilla.
- **En el uno del compás:** la entrada y los cortes de música caen en tiempo fuerte.
- **Entra al terminar el gancho.** El gancho va con voz desnuda o con música de intriga y un riser que se corta en seco.
- **Distinta en cada video:** no repitas canción en dos videos seguidos de la misma cuenta.
- Si la música tiene que respirar entre frases: +4 dB en las pausas de al menos 0.35 s (no en los huecos entre palabras),
  con transiciones de 0.25 s.
- Si la persona nombró una canción, va esa. Si rechaza la música, no adivines otra: deja 8 previas de 30 s, en contexto
  sobre el video, en una carpeta para que elija.

### Nivel bajo la voz
Diferencia entre el RMS de la voz medido donde habla y el de la música (`scripts/escuchar.py --voz --objetivo`).
**Regla general: de 16 a 22 dB bajo la voz según el formato** (base de conocimiento y agente, vigente de agosto a
noviembre; reafirmada el 15-oct con «la voz debe ser la protagonista»). Donde la fuente dio una cifra propia, va esa:

| Formato | Música bajo la voz |
|---|---|
| Dopamínico (y cualquier formato sin cifra propia) | 16 a 22 dB; la fuente no le da una cifra propia |
| Yapping | 18 dB |
| Crudo | 18 dB |
| Lista de herramientas | 18 dB |
| Narrador con insertos halftone | 18 dB (a 25 dB no se escuchaba) |
| Crudo para anuncio de negocio local | 19 dB |
| Marca de un cliente | 20 dB |
| Ilustrado | 22 dB |
| Pantalla partida con la canción de la película de la que habla | 8 dB (la canción es parte del tema) |
| Backmusic (las canciones que se presentan) | 2 dB |

**Reel de un cliente con su kit de marca** (receta aprobada el 16-ago para ese cliente, no para el formato): voz a
-13.3 LUFS en los tramos hablados y música 13.4 dB por debajo (-26.7 LUFS), bus de efectos a -5 dB, master -14 LUFS con
techo -1 dBTP, al fps nativo del material.

En formatos donde la fuente fija el nivel de la pista y no la diferencia: POV con cama a -36 dB; tarjeta sobre negro
con la música a -14 dB; talkinghead de salud con la música a -11 dB en su mezcla («que esté ligeramente ahí»).

### Música por estilo
- Narrador e historias: ondas cerebrales (atmosférica) o música de storytelling; para nostalgia, storytelling.
- Yapping y crudos: «popular en TikTok» con intriga. Yapping de IA o tecnología: intriga tipo synthwave. Yapping de
  negocio serio: emocional.
- Nicho de citas: jazz sensual; la variante lenta, una pieza cinematográfica lenta. Reflexivo: piano o cuerdas.
- Talkinghead de marca: una por video, se confirma con la persona.
- Si el video habla de una película o marca y existe su canción en la librería, va esa.
- Si la cuenta de un cliente tiene una canción fija (por ejemplo, el instrumental de una canción de su marca), búscala
  primero en su material.

### Derechos
Avisa el riesgo con canciones de tendencia; prefiere la librería con licencia o un servicio de música con licencia;
anota los créditos CC BY para la descripción (autor de la música, fotos de Commons, Openverse). Las canciones con
derechos las baja la persona.

## Efectos (SFX)
- Siempre de una librería con licencia; nada sintetizado a mano. Los efectos que la persona ya aprobó no se rediseñan.
- **Cambio de escena o de encuadre:** obturador de cámara, de entrada y de salida.
- **Clic ligero** en las palabras animadas (nunca en el subtítulo normal); **whoosh en el cuadro 0** del gancho;
  **riser** al cierre del gancho solo como bisagra entre gancho y canción (en estilos suaves, un whoosh suave en su
  lugar: el riser «muy de ahí de más»); **golpe grave** para lo dramático, racionado.
- Lo cinematográfico es grave y sutil: un riser en cada transición suena a tráiler.
- Densidad medida en el estilo narrador: 0.9 a 1.2 sonidos por segundo, la mayoría ligados a cortes; lo que se
  transforma en grande va mudo.
- Ilustrado: barridos, clics y golpes graves, sin risers. Pantalla partida: sonidos de movimiento secos, sin clics de
  mouse, pops ni brillos. Crudo: un pop muy ligero a -29 dB del pico de la voz, cortado a 0.25 s.
- «Bájale un poco a los efectos» es la queja más repetida: mídelos.
- **Medidos, nunca a ojo:** sin voz, cada efecto entre **-10 y +3 dB** de la música en su instante (estilos sutiles:
  **-12 a -3 dB**). Subidos a ojo quedaron 13 a 30 dB por debajo y no se oían. `scripts/escuchar.py` lo mide.
- Bus de efectos normalizado por pico, no por RMS (por RMS saturaba).
- Entrega siempre el mudo y las capas para que la persona escuche un minuto; nada de oído se marca como revisado.

## Voz
- **Primero a mono:** extrae la voz a un WAV mono de 48 kHz (`ffmpeg -i crudo.mp4 -vn -ac 1 -ar 48000 voz.wav`) y
  pásala por DeepFilterNet3 con post-filtro `--pf` (ruido de fondo y eco del cuarto; baja el piso entre palabras unos
  4 dB sin tocar la inteligibilidad; una segunda pasada solo da 1.5 dB más y no compensa el riesgo de artefactos).
  Versiones que funcionan: `uvx --python 3.11 --from deepfilternet --with torch==2.0.1 --with torchaudio==2.0.2
  deepFilter voz.wav --pf -o dfn/` (con torchaudio 2.1 o más se rompe).
- **EQ y nivel del pipeline de talkinghead por JSON**, todo en un solo `-af` sobre la voz limpia:
  `highpass=f=95,equalizer=f=250:t=q:w=1.0:g=-2.5,equalizer=f=430:t=q:w=1.4:g=-2.0,equalizer=f=3200:t=q:w=1.2:g=4.0,
  equalizer=f=7500:t=q:w=1.0:g=3.0,deesser=i=0.45:m=0.5:f=0.5,acompressor=threshold=-18dB:ratio=2:attack=12:release=220:makeup=1,
  loudnorm=I=-15.5:TP=-1.5:LRA=8` (turbidez 250 Hz, caja 430 Hz, presencia 3.2 kHz, aire 7.5 kHz). Compresión 2:1 con
  casi nada de ganancia de compensación: con ratio 3 y makeup 2 la voz salía saturada y «apretada».
- **Acabado del pipeline de octubre-noviembre** (pantalla partida, yapping): tras DeepFilterNet3,
  `equalizer=f=250:t=q:w=1.2:g=-1.5,equalizer=f=3200:t=q:w=1.0:g=2.5,equalizer=f=9500:t=q:w=1.4:g=1.5,deesser=i=0.28`.
- «Voz de estudio» cuando se pide: EQ, de-esser, dos compresores, compuerta, limitador y una reverb corta por convolución.
- Si la voz viene muy baja (un audio exportado de una app a -57 dB), mide con `volumedetect` antes de cortar y sube la
  ganancia (+28 dB en ese caso): si no, el transcriptor alucina («Gracias.»).

## Master
| Uso | Loudness integrado | Pico real |
|---|---|---|
| Marca personal (dopamínico, talkinghead de marca, yapping, crudo, tarjeta...) y cliente de contenido orgánico | -16 LUFS | -1.5 dBTP |
| Promos, anuncios (ilustrado, anuncio de negocio local) y clientes con kit de marca | -14 LUFS | -1.5 dBTP (-1 dBTP en la receta del cliente con kit) |

- `loudnorm` en dos pasadas (la primera mide, la segunda aplica con `measured_*` y `linear=true`), y después
  `aresample=192000,alimiter=limit=0.7:level=0:attack=1:release=60,aresample=48000`, que deja el pico real en ~-2 dBTP
  tras el AAC. La suma de pistas sin limitador satura.
- Todos los filtros en un solo `-af`; `-nostdin` siempre en scripts y bucles (un proceso sin él se colgó días).
- Para Meta: recorta el audio que sobre al final del video, o congela el último cuadro.
- Verifica con `scripts/qa_master.py final.mp4 --lufs -16` (o `-14`).
