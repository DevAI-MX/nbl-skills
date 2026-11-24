# QA antes de entregar

Ningún punto se marca como hecho sin la medición. Lo que solo se puede juzgar de oído se le pide a la persona con un
archivo concreto para escuchar.

## Lista

| # | Qué | Cómo | Pasa si |
|---|---|---|---|
| 1 | El archivo es el nuevo | `ffprobe -v error -show_entries format=duration -of csv=p=0 final.mp4` y la fecha del archivo | Duración esperada y fecha de este render |
| 2 | Resolución, códec, loudness, pico y pausas | `python3 scripts/qa_master.py final.mp4 --lufs -16` (o `-14`; `--pausa-max` del formato; `--resolucion 1920x1080` en horizontal) | Todo PASA: 1080x1920, H.264 sin HDR (HEVC o `arib-std-b67` = clip HDR colado), loudness a ±0.5 LU del objetivo, pico real <= -1.5 dBTP, ninguna pausa bajo -40 dB más larga que 0.22-0.25 s (o la del formato) |
| 3 | Palabra por palabra | Re-transcribir el mp4 final y comparar contra la transcripción del corte | Ninguna palabra cortada, perdida, de más ni «alucinada» al final |
| 4 | Uniones | `python3 scripts/cortes.py uniones corte.wav cortes.json` | Cada unión pasa por <= -40 dBFS |
| 5 | Subtítulos, niveles 1 y 3 | `python3 scripts/revisar_subtitulos.py --cues ... --transcript ... --cta <PALABRA> --video final.mp4 --y <posición>` | REVISION OK (lo que se dice después de la palabra del CTA no tiene que salir escrito) |
| 6 | Subtítulos, nivel 2 | Validador del motor o revisión de la línea de tiempo | Cada subtítulo montado donde toca, nada encimado |
| 7 | Mezcla | `python3 scripts/escuchar.py --musica musica.wav --efectos sfx.wav --voz voz.wav --objetivo <dB del formato> --video final.mp4 [--compas compas.json]` | Música a ±1 dB del nivel del formato; cada efecto entre -10 y +3 dB de la música (sutiles -12 a -3); la capa de efectos no recorta |
| 7b | Cuadros | `python3 scripts/qa_cuadros.py final.mp4 --bloques graficos.json --hojas qa/` (`--cierre 1` si el formato cierra a negro) | Sin negro, sin tramos muertos de más de 1 s, cada texto de gráfico visible letras/15 + 1.5 s (frase) o + 0.6 s (1-2 palabras); cada pop confirmado mirando la tira |
| 8 | Primer cuadro | `ffmpeg -nostdin -ss 0 -i final.mp4 -frames:v 1 primero.png` | Llamativo, sin cara neutra ni cuadro negro |
| 9 | Hoja de contacto | `ffmpeg -nostdin -i final.mp4 -vf "fps=1,scale=270:-1,tile=6x5" hoja.png`, mirada a tamaño celular | Cero cuadros negros, repetidos o tramos quietos de más de 1 s; nada importante en las zonas de interfaz; subtítulos sin tapar cara ni animaciones; nada encimado |
| 10 | Material | Cada captura, logo, cifra y nombre en pantalla existe y es real | Nada inventado; créditos CC BY anotados |
| 11 | Repetición | Registro de b-roll y canciones de los videos anteriores | Máximo 25 % de b-roll compartido con el anterior, 2 videos de distancia para repetir; canción distinta |
| 12 | Final | Últimos 2 s | El cierre de su formato (`formatos.md`), sin audio sobrante |

## Para la persona (lo que no se puede medir)
- El mudo (`revision/mudo.mp4` que deja `escuchar.py --video`): ¿se entiende sin sonido?, como lo ve quien no sube el
  volumen.
- 10 s de `revision/compas.wav` (con `--compas`): ¿el clic cae con la batería? Si camina, la rejilla está mal y todo lo
  que se alineó a ella también.
- `qa/hoja.jpg` y `qa/celular.jpg`: ¿se lee en un teléfono?
- La mezcla final una vez y, si hay dudas, las capas (voz, música, efectos) por separado: ¿algún efecto suena a
  caricatura, a clic de mouse o a brillo?, ¿la música cierra o se corta?
- Pídele ese minuto de escucha y que confirme el volumen de efectos y música.

## Reporte de entrega
1. Ruta del archivo (nombre legible, «Cliente - tema.mp4») y versión (v1, v2...). Las correcciones van a una versión
   nueva; la entregada no se pisa hasta que la persona lo diga.
2. Qué se hizo (cortes, música elegida y por qué, estilo de subtítulos).
3. Qué se verificó, con números (LUFS, pico, pausa máxima, uniones, palabras comparadas, resultado de la triple
   revisión).
4. Qué no se pudo verificar (lo que es de oído) y qué falta (material que debe aportar la persona).
5. Si conviene verlo en el celular, ofrécelo comprimido o en tramos.
