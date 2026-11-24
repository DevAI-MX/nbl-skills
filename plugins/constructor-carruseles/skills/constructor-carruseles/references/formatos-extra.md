# Formatos sin plantilla y piezas sueltas

Técnicas exactas de formatos que ya se aprobaron en carruseles reales. No traen plantilla: se arman con
`scripts/build.py` usando un `"molde"` propio (un HTML que se repite en todas las láminas interiores, ver
`build.md`) o con prompts de imagen.
Los colores son los de la marca de la persona salvo cuando se dice que el color es parte de la técnica.

## Reglas que valen para todos
- Sin etiquetas encima del título («EL PATRÓN», «VERDAD INCÓMODA», «ANTES DE IRTE»): estorban más de lo que
  suman. Al quitarlas, el copy que vivía en ellas no se pierde: compara contra el original palabra por
  palabra. La píldora de una noticia y la pastilla de «dato clave» del estilo último momento sí van: son la
  mecánica.
- Sin viñetas de color antes del título: el título arranca directo.
- Íconos de línea en el color de acento, uno por slide, cuando la persona pide íconos; congruentes con el
  tema (si el público es masculino, la estrella se lee femenina: fuego funciona mejor).
- Juego visual coherente con el tema (línea de tiempo, burbujas tachadas «Así no / Así sí», cuenta
  regresiva 1, 2, 3, lista en tarjetas, tarjetas con X): se vale ser creativo en lo visual mientras sea
  congruente.

## Limpio v2 (lo que implementa la plantilla `limpio`)
- Papel `#EDEBE6` con grano: SVG `feTurbulence` (`fractalNoise`, `baseFrequency 0.85`, `numOctaves 3`) en
  data-URI, opacidad ~0.16. Es parte de la técnica; si la marca tiene otro claro, se usa su claro con el
  mismo grano.
- Títulos en una sans apretada 700 con tracking −0.045em; cuerpo 500 con −0.025em; todo centrado.
- Marcatexto solo en la mitad de abajo de la palabra: `linear-gradient(transparent 48%, color 48%, color
  94%, transparent 94%)`, con `box-decoration-break: clone`. Colores de la técnica: lima `#C6F36A`, amarillo
  `#F3EE2A`, menta `#AEE8E1`, lila `#E2CCF6`.
- Subrayado de crayón: un `path` con borde comido por ruido (`feTurbulence baseFrequency "1.6 0.5"`,
  `feColorMatrix` que convierte el ruido en alfa y `feComposite operator="in"`). **Sin `feDisplacementMap`.**
  Colores: azul `#4B6BF5`, naranja `#F26B1D`, verde `#1FA35B`, morado `#9B5BE3`.
- Capturas en tarjeta casi sin radio y sombra fuerte: `0 22px 40px rgba(0,0,0,.30), 0 4px 10px rgba(0,0,0,.18)`.
- «Paso N» como texto grande con el número marcado (sin chip negro).
- Auto-ajuste del bloque central para que el texto nunca se salga (ver `verificacion.md`).

## Último momento (lo que implementa la plantilla `noticia`)
Noticiero de IA para dueños de negocio: una empresa grande más una herramienta que hace sola un trabajo que
hoy se le paga a alguien. Solo para noticias **reales**, de pocos días atrás y con fuente; si la
integración no es oficial, no se dice «lanzó» ni «100 % oficial».
- **Fondo:** degradado vertical con un tinte arriba y casi negro abajo (`#0B0B10`), y encima una retícula de
  puntos muy tenue (puntos de 2 px cada 24 px, al 6 %). El tinte y el único acento del carrusel salen de la
  herramienta de la que se habla (por ejemplo, violeta oscuro `#2A2A4A` con lavanda `#A99CFF`, o petróleo
  `#123438` con turquesa `#4FD8D0`). Texto blanco `#F5F5F7` y secundario gris claro `#C9C9D1`.
- **Letra:** una sans geométrica semibold o bold con tracking cerrado (−0.03em), en frase normal; solo las
  pastillas y un golpe final («100 % OFICIAL») van en mayúsculas. Títulos de 64 a 80 px centrados, de 2 a
  3 renglones, con una sola frase en el acento; texto corrido de 34 a 40 px.
- **Portada:** foto a sangre que se funde a negro en la mitad de abajo, píldora roja redondeada y centrada
  («ÚLTIMO MOMENTO», «URGENTE») y el titular centrado encima. Si sale una persona real, foto real con
  licencia y crédito, o un collage con el elemento gráfico claramente dibujado; nunca una foto fotorrealista
  inventada.
- **Láminas, en este orden (5 a 6):** 1) la noticia; 2) la prueba: titular, captura **real** en una tarjeta
  de vidrio oscura (borde de 1 px, esquinas de 24 px) y un remate de una línea («Sí, leíste bien.»); 3) lista
  «X con IA puede:» de 5 a 6 renglones con círculos de contorno o flechas; 4) dato clave: una pastilla, un
  titular, la captura de la respuesta real y una línea que concluye; 5) antes y ahora (opcional): dos
  tarjetas de vidrio apiladas, «Antes:» en blanco con el dolor y «Ahora:» en el acento con la promesa;
  6) cierre con la palabra y el recurso.
- **Íconos 3D de las apps** de plástico blanco brillante, cortados por las orillas y a veces desenfocados por
  profundidad: dan volumen sin estorbar al texto. Los genera el generador de imágenes en 4:5.
- **Pie:** el @ chico abajo a la izquierda. Sin numeración de láminas ni flecha.
- **Caption:** el dolor como pregunta, una línea de solución, «Comenta X y te envío la guía» y de 3 a 5
  hashtags.

## Portada con foto y gancho encima
Texto abajo, centrado, máximo **2 renglones**, tapando lo menos posible la imagen. Si la imagen aún no
llega, igual el texto va abajo y el espacio de arriba queda reservado. Degradado inferior suave (negro a un
máximo de 0.62 a 0.74 de opacidad). Zoom y encuadre a pedido (se llegó a 1.24x); para que la persona lo
ajuste ella, usa el editor de portada (`assets/editor-portada.html`).

## Texto de editor de Instagram
Foto a sangre y una caja blanca recta y plana con texto negro, sin sombras:
`.txt { background:#fff; color:#000; padding:32px 50px 36px; max-width:920px; font-weight:600;
font-size:58px; line-height:1.36; letter-spacing:-0.015em; }`. La caja va donde no tape al sujeto. Si se
saca una segunda versión del mismo carrusel, cambia la fuente (por ejemplo de una sans SemiBold a la de
Instagram en Medium) para que se lea como pieza distinta.

## Tuit (formato de X)
La gracia es que todo parezca publicado en X, como texto: misma letra, mismo peso, sin negritas que X no
tiene, en la portada y en el cierre. No son capturas de posts.

## Chat de mensajes
Fondo oscuro `#0E0E11` con retícula de puntos y un halo del color de acento, encabezado de perfil completo,
burbujas tipo iMessage: entrante gris `#262629` con radio `36px 36px 36px 8px`, saliente en el acento con
radio `36px 36px 8px 36px`, y la barra «Escribe un mensaje…» abajo. La explicación va pegada a las burbujas
y la etiqueta de la respuesta no queda pegada al encabezado.

## Editorial de revista
Fondo hueso con grano (`feTurbulence`, opacidad 0.14, `mix-blend-mode: multiply`), títulos en serif display
700 con palabras clave en el acento, texto en sans gris cálido, cabecera con línea fina y el @ en
mayúsculas, número índice gigante del punto en contorno del acento (`-webkit-text-stroke`), capturas como
fotos de revista con marco de 1.5 px y pie de foto. El cierre lleva un botón sobrio, sin cursor: el estilo
es serio.

## Marcador
Fondo negro con trama diagonal, display condensada gigante con una palabra en bloque del acento tipo
marcador (`box-decoration-break: clone`). El texto gigante va **solo en la portada**; en contenido, titular
más párrafo (si todo es gigante, parecen puros títulos).

## Lista de comandos
Cápsulas negras, números e íconos en el acento, portada con la cifra grande con filo y relieve, y un cierre
con los renglones que faltan borrosos y un candado («¿Quieres los otros N?»).

## Documento de prompt oscuro
Fondo `#0A0A0A` con cuadrícula `#1C1C1C`, el @ centrado arriba sin foto ni palomita, títulos de sección en
mayúsculas con un emoji pequeño entre dos líneas blancas.

## Libreta o plumón a mano
Siempre sobre la foto real de la libreta de la persona con un generador de imágenes (ver
`prompts-de-imagen.md`, reglas 7 y 8). La versión en HTML con fuente manuscrita encima de la foto se
rechazó: tiene que parecer escrito con pluma de verdad. Variante plumón sobre blanco: fondo blanco liso sin
renglones ni texturas, mucho espacio en blanco, todo escrito a mano con plumón de punta media.

## Encabezado de perfil de Instagram (solo si la referencia lo lleva)
Foto de perfil circular, nombre, palomita de verificado y @, arriba a la izquierda en todas las slides; en
la portada, centrado arriba sobre un degradado negro ligero.
- Anillo de historia con el degradado de Instagram (amarillo, naranja, rosa, morado), no un borde de un
  color; el hueco del anillo toma el color del fondo. Marcado:
  `<span class="ig-avatar-ring"><span class="ig-avatar-gap"><img class="ig-avatar"></span></span>`, y
  **`.ig-avatar-ring` necesita `display:flex`** o la foto queda descentrada.
- Palomita: sello azul de 8 puntas (`#1D9BF0`) con la palomita de trazo encima. Si el SVG se ve partido,
  está mal formado.
- Como el @ ya va arriba, se quita del pie y del cierre.
- Si la persona no tiene verificado, sin palomita.

## Cierres
- **Comenta y recibe:** «COMENTA [PALABRA]» y debajo el recurso: la portada del documento borrosa con solo
  el título legible y un sello «PDF» (recorta el contenedor a una tarjeta que se desvanece abajo para que
  no tape el texto).
- **Seguir:** «SÍGUEME» más un botón «Seguir» como el de Instagram (azul `#0095F6`, ícono de persona con
  +) y un cursor haciendo clic; o la barra de acciones de Instagram (me gusta, comentar, compartir y
  guardar en el acento).
- **Editorial:** botón sobrio sin cursor.

## Pantalla partida (detalle de la plantilla `partida`)
Dos mitades de 675 px con la imagen en `cover` centrado, línea divisoria fina, texto en serif blanco con
sombra como cita al pie de cada mitad y un degradado oscuro al pie de cada mitad. La plantilla cierra con
el cierre del tipográfico; la variante de cierre que también se aprobó es fondo oscuro con la misma serif
y la llamada a seguir con la barra de acciones de Instagram.

## Estilos para rehacer referencias (21 y 22 de noviembre de 2026)
Cada referencia se manda a uno de estos estilos; se roba el gancho, la información, los pasos y la mecánica,
y el diseño se pasa al estilo. Si una referencia trae una mecánica que no está aquí y le funciona, se
propone como estilo nuevo antes de construirla.

| Estilo | Técnica | Para qué referencias |
|---|---|---|
| **Limpio v2 versión ícono** | Fondo claro, una sola frase con una palabra de color y dos íconos de apps unidos por una flecha dentro de una pastilla de vidrio. Sin persona. Es el más barato de producir. | «La IA X se conecta con la app Y». |
| **Limpio v2 + portada con personaje** | El mismo papel del limpio; en la portada, la persona haciendo algo absurdo que es la metáfora (con un objeto, con un gesto raro). Por dentro, «N. nombre de la idea + una frase + la muestra en mini láminas». Cierre con el recurso en 3D y la palabra. | Listas de «X ideas» o «X errores» con una muestra de cada una. |
| **Escena oscura** | Una escena a sangre hecha por el generador, fondo tinta y un solo acento de color. La persona en la situación absurda de la referencia con su recorte real pegado; no se falsifica a una persona real. | Noticias de IA (es donde se adapta el último momento) y casos de éxito. |
| **Cómic o manga** | Viñetas con la persona y un compañero o mascota fijos de la marca. Unas 5 páginas de diálogo: la queja, el compañero explica, la promesa, «pásame la guía» y la llamada a la acción. El texto de los globos es el literal adaptado. | Referencias de diálogo o con mascota. |
| **Foto real + gag** | Una foto que la persona se toma con un objeto que es la metáfora y el texto en caja blanca de editor de Instagram; después, láminas en limpio v2. Arranca con «tengo algo que contarles…», sigue la revelación, cómo funciona en viñetas y la llamada a la acción. | Anuncios sorpresa o «tengo algo que contarles». |
| **Pixel art o videojuego** | Un mundo ilustrado reconocible (pixel de los 90) que rompe con el feed; personajes con rasgos de su rol. | Listas de agentes o herramientas. |
| **Libreta, editorial o lista de comandos** | Ver arriba. | Solo si la referencia es de ese tipo. |

**Personaje que se repite** (portada con personaje, cómic, escena oscura): la cara de la persona sale de
fotos reales suyas; si la escena necesita generarse, se genera la escena y se pega su recorte real, o es
una ilustración claramente estilizada. Para un personaje ilustrado fijo: un bloque de identidad que se pega
idéntico en cada prompt, con vestuario, pose, escenario y luz en capas aparte; dos imágenes maestras
«aburridas» (retrato y cuerpo entero, fondo gris, ropa lisa, luz plana) que se adjuntan siempre, sin
encadenar desde el último resultado; y la edad anclada varias veces y hacia arriba (cifra, «adulto»,
líneas de expresión), porque el modelo rejuvenece solo.

**Variedad:** en una semana no se repite el mismo estilo dos días seguidos, y los casos de éxito no pasan
de 1 de cada 5 carruseles. Los casos de éxito pueden rotar «disfraces» de apps conocidas (reproductor de
música, ventana de sistema viejo, polaroid con cinta) con la misma estructura de caso.

## Los 7 moldes interiores que más se repiten en los 40 carruseles más fuertes
Fuente: el mismo entrenamiento con 200 virales del 22-nov-2026. Cada referencia se clasifica en uno y se
construye con ese molde:
1. **Galería de resultado con muestra fija, casi sin texto (0 a 15 palabras):** un efecto o estilo por
   lámina, con la miniatura de la original siempre en la misma esquina. El prompt no va en la lámina: se
   manda por el recurso.
2. **Una acción por lámina con su prueba real (8 a 55 palabras):** el paso arriba y la captura real debajo.
3. **Nota escrita a mano sobre papel (16 a 45 palabras):** pregunta de dolor y comando gigante subrayado.
4. **Una frase por lámina en tipografía gigante de tres voces (2 a 20 palabras):** mayúscula condensada,
   minúscula chica y cursiva de emoción, con 2 o 3 colores.
5. **Dos viñetas apiladas con la frase repetida (7 a 9 palabras):** el mismo personaje ilustrado; arriba y
   abajo cambian.
6. **Comparación de un vistazo:** VS, malo contra bueno o ranking, partida en dos o en barras de semáforo.
7. **Rejilla 3x3 de comandos sobre la misma foto (unas 9 palabras):** nueve versiones de una foto con el
   comando en una cápsula; la portada es una toma desde arriba.

La lista larga sobre negro (42 a 100 palabras por lámina) también aparece, pero rompe la regla de pocas
palabras: solo si la referencia es exactamente esa. Lo que se ve en los 40: portada con letra enorme (del 40
al 60 % de la lámina) muchas veces encima de la persona; la muestra grande y casi a sangre por dentro; el
cierre repite el mundo de la portada con la palabra gigante entre comillas.

## Portada de módulo (para cursos o productos)
Fondo oscuro con retícula de puntos en el acento y un brillo suave del mismo color; etiqueta en monoespaciada
tipo código (`// MÓDULO_01`); título en una sans Black en mayúsculas; íconos de línea fina en el acento; el
isotipo o logo de la marca **grande** (sobre foto, dentro de un círculo oscuro con aro del acento), nunca el
logo completo pequeño. Por dentro, un nivel o módulo por lámina con su texto completo, y una lámina de
entrada al proceso («Así es como se verá tu proceso»). La portada lleva solo el texto pedido, centrado.
