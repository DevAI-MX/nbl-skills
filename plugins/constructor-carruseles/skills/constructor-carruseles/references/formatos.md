# Los 6 formatos

Cada formato tiene su portada, su slide de contenido y su cierre en `assets/plantillas/<formato>/`. En `assets/muestras/` hay una imagen de cada portada y una hoja con los 18 slides juntos (`assets/muestras/todos-los-formatos.jpg`). Enséñale a la persona las muestras antes de que elija.

| Formato | Cómo se ve | Funciona para | Necesita |
|---|---|---|---|
| **tipografico** | Solo texto grande sobre color. Portada en el color de acento, contenido alternando fondo oscuro y claro. | Listas, errores, pasos, ideas que se explican con palabras. Es el más rápido de hacer. | Nada más que el texto. |
| **tuit** | Parece una publicación de X: foto de perfil, nombre, @ y el texto. En blanco o en negro (`slide noche`). | Opiniones, frases fuertes, historias cortas en primera persona. Se siente como algo que alguien dijo, no como un anuncio. | Foto de perfil (si no hay, sale la inicial en un círculo). Todo tiene que parecer publicado en X: la misma letra y el mismo peso que X, sin negritas que X no tiene, en la portada y en el cierre. |
| **noticia** | Estilo «último momento»: portada con foto a sangre que se funde a negro, píldora roja centrada y titular centrado en frase normal; por dentro, fondo oscuro con tinte y retícula de puntos, y la prueba en una tarjeta de vidrio. | Noticias de IA o de tu industria: una empresa más una herramienta que hace sola un trabajo. El formato de noticia hace que la gente se detenga. | Una imagen para la portada, el tinte (`TINTE`) y el acento de la herramienta de la que habla. Solo para algo real, de pocos días atrás y con fuente verificable. |
| **limpio** | Técnica «limpio v2»: papel claro con grano, todo centrado, marcatexto en la mitad de abajo de la palabra, subrayado de crayón, capturas en tarjeta con sombra fuerte y «Paso N» con el número marcado. | Tutoriales, paso a paso, enseñar una herramienta con capturas. | Capturas reales o puntos cortos. |
| **foto** | Una foto a todo el slide con el texto abajo sobre un degradado oscuro. | Historias personales, temas emocionales, "lo que haría si...". | Una foto distinta por slide. Si no hay fotos suficientes, elige otro formato. |
| **partida** | El slide partido en dos mitades de 675 px: arriba una cosa y abajo la otra, con una línea fina en medio. | Comparar: antes y después, lo que haces y lo que funciona, mito y realidad. | Dos imágenes por slide de contenido. El cierre es el del tipográfico. |

Ninguna plantilla lleva flecha de «desliza», número de slide ni etiquetas encima del título, el pie es el mismo en las tres láminas de cada formato y todos los cierres traen el bloque `RECURSO` (la hoja borrosa del recurso con su sello).

## Formatos sin plantilla
`formatos-extra.md` trae la técnica exacta de otros formatos que ya se probaron (chat de mensajes,
editorial de revista, marcador, texto de editor de Instagram, lista de comandos, documento de prompt oscuro,
libreta a mano, encabezado de perfil de Instagram), los estilos para rehacer referencias (portada con
personaje, escena oscura, cómic, foto real + gag, pixel art), los 7 moldes interiores de los virales y la
portada de módulo. Se arman en HTML con `scripts/build.py` y un molde
propio, o con prompts de imagen.

## Cómo recomendar

- Si el tema es una lista o un paso a paso sin imágenes: tipografico o limpio.
- Si es una opinión o algo que la persona diría en voz alta: tuit.
- Si hay algo nuevo o sorprendente con fuente: noticia.
- Si compara dos cosas: partida.
- Si la persona tiene buenas fotos suyas: foto.
- Si es un tema de IA que se puede enseñar con el resultado: galería de resultados (ver `referencias.md`).
- Si es una pregunta de dolor con un comando: nota a mano sobre su libreta (`formatos-extra.md`).
- Si viene de una referencia: el formato que conserve su mecánica (ver `referencias.md`).

Un carrusel usa un solo formato de principio a fin. Cada carrusel tiene su propio mundo visual: lo que se
repite entre carruseles de una cuenta es el molde, no el mismo fondo con el mismo acento.
