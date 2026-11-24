# Biblioteca de anuncios de Meta

## Qué se puede leer

Se lee sin iniciar sesión en Facebook, desde el navegador de investigación, con `scripts/web/adlib.mjs`: la respuesta
GraphQL de la búsqueda (`search_results_connection`) y, cuando hay pocos resultados, la primera tanda que Meta manda
incrustada en el HTML (el script lee las dos).

Consultas: por palabra clave, por frase exacta o por página (`view_all_page_id`), con país y estado (activos o todos).
El orden de la página es por impresiones totales: la posición (`rank`) es una señal. Con 40 por consulta tarda menos de
1 minuto; con 120, unos 5.

Por anuncio existen: fecha de inicio y de fin, si está activo, `collation_count` (versiones del mismo contenido
corriendo a la vez), plataformas, formato, texto, título, botón, enlace de destino, página y sus seguidores, y URLs del
video y la portada.

## Qué NO existe

Para anuncios comerciales entregados fuera de la Unión Europea no hay gasto, impresiones exactas, alcance, clics, CTR,
costo por resultado ni ROAS. No existen públicamente: no los estimes como si fueran datos. El alcance aproximado solo
aparece en anuncios entregados en la UE (`web/adlib-alcance.mjs`).

El Ads Manager de otra cuenta tampoco se ve: haría falta acceso de solo lectura dado por su dueño.

## Cómo se define un «ganador»

Ninguna señal prueba que un anuncio vende; juntas sugieren que el anunciante lo mantiene porque le funciona. Dilo
siempre así. El criterio está en `scripts/anuncios/ganadores.py`:

Señales, de la más fuerte a la más débil: **días activo** (la más fuerte que existe desde fuera), **versiones
simultáneas** (si lo duplica en varios conjuntos le está metiendo más dinero), **relanzamiento** del mismo copy en
fechas distintas (nadie relanza un anuncio que perdió), **posición por impresiones** en la búsqueda y
**multiplataforma**.

Calificación de 0 a 100 que usa el script:

| Señal | Puntos |
|---|---|
| Días activo | 40, el máximo a los 60 días |
| Versiones simultáneas | 25, en escala logarítmica, el máximo con 16 versiones |
| Lugar en el orden por impresiones dentro de su búsqueda | 20 |
| Reuso del mismo copy en anuncios del mismo anunciante | 10, el máximo con 5 |
| Corre en más de una plataforma | 5 |

Niveles:

- **Ganador fuerte:** 30 días o más activo, y además 3 versiones o más o el copy lanzado en 2 fechas o más.
- **Ganador de lanzamiento:** menos de 30 días, pero 5 versiones o más o el copy lanzado en 3 fechas o más.
- **Probable:** el resto de los que entraron a la lista.

Un anuncio por anunciante y copy (el de mejor calificación). `--filtro` deja solo los que cumplen todas las expresiones
(por ejemplo, que invite a una clase y que sea del nicho), para no mezclar giros.

Ajustes por tipo de giro:

- **Eventos (webinar, clase, reto):** el anuncio corre de 7 a 21 días y se apaga al pasar el evento, gane o no. Pesa más
  el relanzamiento que los días; 30 días o más solo es señal clara en clases siempre disponibles (grabadas o VSL).
- **Inventario (autos, maquinaria, inmuebles):** los anuncios de una unidad con precio rotan al venderse y duran menos
  de 30 días; los longevos son de presencia. Gana **la página que mantiene muchos anuncios activos a la vez**, no el
  anuncio más viejo (`paginas` en la salida de `ganadores.py`).
- **Servicios locales:** los que duran suelen ser de presencia: diagnóstico gratis o barato, garantía por escrito,
  mensaje directo.

## Trampas

- La búsqueda lee el texto del anuncio, no la ubicación: «no aparece» no es «no pauta», y Meta no filtra por ciudad.
- Filtra falsos significados de la palabra clave («taller» también es curso; exige el contexto del giro).
- Los anuncios de webinar casi nunca dicen «webinar»: busca también clase, masterclass, taller, reto.
- Una búsqueda por página necesita el id de anunciante. El autocompletado sin sesión da 404; el id se saca del HTML
  público de la página de Facebook con `web/pagefb.mjs` (`fb://page/ID`, `pageID`). Los ids de perfil personal pueden
  no ser el de anunciante.
- Si `adlib-captura.mjs` recorta otra tarjeta (la página a veces mezcla un anuncio de terceros), usa
  `captura-simple.mjs <url> <png> 1280 1600` y queda la página completa.
- Nunca corras dos búsquedas de la Biblioteca en paralelo en el mismo navegador: una tumba a la otra. Al relanzar,
  `adlib.mjs` salta lo ya guardado.
- Código 3: Facebook pide sesión o bloqueó temporalmente. Detente.
- Para sacar cuadros de un video embebido (Vimeo) que el headless no logra adelantar:
  `yt-dlp --referer <página que lo incrusta> -g -f <formato hls>` da la URL y
  `ffmpeg -headers "Referer: <página>" -ss <segundo> -i <url> -frames:v 1 cuadro.jpg` saca el cuadro.

## Ficha por anuncio (entregable)

A quién le habla, gancho de copy y de portada, a qué invita, promesa, ángulo, copy completo, enlace a la Biblioteca,
días activo, versiones, en cuántas fechas se lanzó, nivel, por qué parece ganador (qué señales) y cómo adaptarlo sin
copiarlo. Además una tabla de ángulos con su propósito y los días activos de sus anuncios, y, cuando lo piden, un CSV
con todas las filas (`ganadores.py --csv`). Si el encargo termina en escribir anuncios, entrega un brief en archivo con
las estadísticas de los mejores contra todos, las estructuras de los más longevos y las tablas con enlaces, para quien
los escriba.
