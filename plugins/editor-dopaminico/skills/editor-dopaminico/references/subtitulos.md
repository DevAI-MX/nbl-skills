# Subtítulos

## Reglas que valen para todos los estilos
1. **Cita literal** de lo que se dice, verificada contra la transcripción del corte final.
2. **Sincronía exacta:** el subtítulo nunca entra antes de la voz (el inicio de palabra es el arranque real medido por
   energía, no el que da Whisper) y no se «acomoda donde quepa».
3. **Frases completas:** un subtítulo nunca queda a medias ni termina en preposición, conjunción ni artículo.
4. **Posición fija:** cada palabra se revela en su sitio definitivo; una palabra que ya apareció no se mueve para
   hacerle sitio a otra (el bloque que «baila» se rechazó). Al terminar la frase se van todas juntas. Dentro de la misma
   frase los subtítulos no cambian de lugar.
5. **Legibilidad primero:** si no cabe, baja el cuerpo hasta que la frase entera quepa. Nada encimado: «cuídalos al
   milímetro».
6. **La palabra del gráfico no se gasta antes:** si un gráfico o una frase animada va a mostrar una palabra, esa palabra
   se quita del subtítulo de ese momento y de los anteriores; se ve una sola vez, nunca duplicada en subtítulo y
   gráfico a la vez.
7. **Capa más alta:** por encima de b-roll y gráficos; un tramo de b-roll sin subtítulo es un tramo perdido para quien
   ve sin sonido. En motores por HTML el orden del DOM no basta: fija el `z-index` a mano (por ejemplo b-roll 1,
   subtítulos 5, frases 6, palabra clave 8). Un solo clip HDR en el proyecto deja los subtítulos debajo solo en el
   archivo final (ver `trampas-y-material.md`).
8. **Nunca tapan cara, boca ni barbilla**, ni las animaciones. Si tapan la cara, bájalos.
9. **Nunca cruzan un corte entre tomas** (Whisper a veces no pone el punto).
10. **Color:** como mucho dos. Blanco para ~90 % del texto y un acento para ~10 % (la palabra de énfasis). Ningún tercer
    color. Dos fuentes de subtítulo como máximo.
11. **Mayúsculas:** el subtítulo normal no usa mayúsculas forzadas (lo que distingue a la palabra clave es el tamaño y a
    veces el color). Excepciones vigentes: la línea central del bloque dopamínico va siempre en MAYÚSCULAS; la palabra
    del CTA en mayúsculas; las siglas («IA»). Yapping y crudo van en minúsculas (yapping además sin signos).
12. **Sin contorno en los estilos limpios** (dopamínico): solo un glow negro muy suave. Los estilos «Classic» de app de
    celular sí llevan contorno: ahí lo que se ajusta es el contorno, nunca el grosor de la letra.
13. **El CTA:** la palabra clave, una vez aparece, se queda fija hasta el final; los subtítulos terminan en ella y lo que
    se dice después solo se oye.

## La triple revisión (con cualquier cambio que toque el video)
Las cuatro fallas, todas vistas en producción una y otra vez:
1. **Palabras repetidas:** un bloque muestra una frase y el subtítulo siguiente la repite.
2. **Cues duplicados:** el mismo texto dos veces seguidas.
3. **Texto que no aparece** cuando se dice, o aparece antes o después de su momento.
4. **Bloques solapados:** dos textos en pantalla a la vez.

Cada falla se ve en un nivel distinto, por eso son tres niveles y no tres veces lo mismo:
- **Nivel 1, datos:** duplicados consecutivos; solapes entre cues; un cue encima de un gráfico con texto (tocarse en el
  borde, hasta 0.06 s, no cuenta); repeticiones cercanas (dos o más palabras de contenido en común y dentro de 4 s:
  «en la» repetido no es falla, ni que el hablante repita una palabra suelta); palabras que se dicen y no aparecen.
- **Nivel 2, composición:** lo que el motor monta de verdad (en un editor por HTML, su validador; en un editor de
  escritorio, revisar la línea de tiempo).
- **Nivel 3, render:** cuadros muestreados del mp4 final en la franja del subtítulo: hay texto cuando se habla.

`scripts/revisar_subtitulos.py --cues subs.srt --transcript whisper.json [--bloques graficos.json] [--video final.mp4
--y 69]` hace los niveles 1 y 3 (más frases que terminan en conector y cues que entran antes de la voz) y sale con
código 1 si algo falla. El nivel 2 lo pone tu motor. Si algo falla, casi siempre la causa es una frase mal escrita o mal
colocada, no los tiempos.

## Recetas por estilo (medidas sobre 1080x1920)

| Estilo | Fuente | Tamaño | Posición vertical | Tratamiento |
|---|---|---|---|---|
| Talkinghead continuo | Inter SemiBold 600, interletraje -0.042em | 68 px | 62 % | continuos, sin animación, 2 a 4 palabras, nunca termina en conector, sin puntos |
| Bloque animado de 3 registros (dopamínico) | Inter Bold chica / Inter Black MAYÚSCULAS grande / Playfair Display Italic | grande 99-168, chica 56, serif 84 | según el hueco (26 / 50 / 72 %) | palabra por palabra, glow del color al 35 % + halo oscuro leve, acento `#FFDE21` al 10 % |
| Revelado palabra a palabra (receta con kit) | sans blanca con sombra sutil, sin halo difuso | cap height ~55 px | base ~1473 px (76.7 %) | las palabras entran una a una con fade corto sobre un bloque ya centrado por la frase completa |
| Dos líneas | Inter (entradilla + clave) | 83 / 108 px | ~55-60 % | pegadas (hueco 0.22 s), ~1/3 de líneas solas, acento amarillo |
| Salud bajo la barbilla | Inter 600 | 78 px | bajo la barbilla (63-80 %) | máximo 3 palabras o 20 caracteres, en seco |
| Tarjeta sobre negro | Inter SemiBold opsz 14 + Snell Roundhand Bold amarilla `#F6DD3B` | 81 / 211 px | dentro de la tarjeta | blanca entera al empezar su tramo, cursiva entera al decir su palabra |
| POV | negrita blanca, contorno 4 px | ~58-64 px | 63-71.5 % | 3 a 5 palabras, minúsculas |
| Crudo («Classic») | Proxima Nova Semibold | 60 px CSS | 69 % | minúsculas, contorno negro 7 px (no engrosar la letra), 3-4 palabras, ~23 caracteres |
| Yapping | Proxima Nova Semibold | 72 px CSS (88 en ASS), Outline 4.8 | y=1325 (pecho) | una palabra a la vez, minúsculas, sin signos, sin encimar |
| Pregunta viral (sobre una edición hecha en el celular) | Inter Bold | 92 px, contorno 7 | 69 %, `\pos(540,1330)` | 3-4 palabras estilo Instagram Edits |
| Lista de herramientas | Inter 28pt SemiBold, espaciado -2 | 56 | X 740, Y 1340 | 2-3 palabras, `\blur3` |
| Costura de pantalla partida | Inter SemiBold, espaciado -2 | 60, contorno 5 | en la línea del medio | palabra por palabra seca, sin animación ni color |
| Costura con panel de revelación | Inter SemiBold, espaciado -4 | 90 | costura | grandes y pegados, fijos, sin moverse |
| Narrador halftone | dos pesos de Inter, color claro + un acento | | karaoke 1 línea al 68-69 % | «una delgada y otra para resaltar, no uses más» |
| Marca de un cliente | la fuente de su marca (ejemplo medido: Poppins Bold mayúsculas blancas con sombra, 98 px, -5) | | la de sus reels | una palabra |
| Ilustrado | la fuente de la marca | | abajo | en pastilla oscura si la ropa es clara |

## Notas técnicas de libass (subtítulos ASS quemados con ffmpeg)
- El tamaño no es el de CSS: libass mide la fuente por (winAscent + winDescent) / unidades por em. Para Proxima Nova
  Semibold el factor es 1.218: 60 px CSS = Fontsize 73; 72 px CSS = Fontsize 88. Calcula el factor de cada fuente.
- Un contorno de 7 px hecho con `paint-order` en CSS equivale a `Outline 3.5` en ASS.
- Las fuentes variables no eligen peso en libass: crea instancias estáticas con
  `uvx fonttools varLib.instancer --update-name-table Inter-variable.ttf wght=900 opsz=28` (opsz=32 falla) y pasa la
  carpeta con `fontsdir`.
- Si el motor por HTML se traba por RAM y el video solo lleva subtítulos, quémalos con ffmpeg + libass.
- Para identificar la fuente de una referencia, compárala píxel a píxel contra el catálogo (Google Fonts y las del
  sistema) antes de proponer: las apps de edición del celular usan fuentes del sistema o la suya propia.
