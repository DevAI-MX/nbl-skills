# Datos de Instagram: qué existe, de dónde sale y qué trampas tiene

## De dónde sale cada dato

| Dato | Fuente | Ojo con |
|---|---|---|
| Seguidores | Cabecera del perfil (atributo `title` exacto; `batchscan.mjs`) | Son los de hoy |
| Vistas de reels | Respuesta de la pestaña `/reels/` (`clips_connection`): su `play_count` coincide con el contador que pinta la miniatura | En el feed y en el buscador las vistas llegan en `null`; si faltan, se usa el contador visible («1,2 M», redondeado) |
| Likes, comentarios, fecha, caption, número de láminas | Respuesta del feed (`user_timeline_graphql_connection`) | Los carruseles no tienen vistas |
| Lista completa de reels | Pestaña `/reels/` | El feed esconde muchos reels |
| Caption completo, duración, fecha real, coautores | Ficha de la publicación (`/api/v1/media/{pk}/info/`: `minfo.mjs`, `fichas-por-codigo.mjs`) | El código de la URL se convierte a pk con aritmética de enteros grandes |
| Láminas de un carrusel y video de un reel | Con sesión (vía principal): `fichas-por-codigo.mjs` y luego `guiones/medios.py bajar`. Sin sesión o de respaldo: `web/carrusel-publico.mjs`, que lee el JSON incrustado en el HTML del post | El lector público a veces no baja nada (post privado, restringido por edad o un carrusel que llega vacío): sale en `failed` y se prueba la otra vía. En una corrida de noviembre la ficha bajó 1,708 láminas y el lector público rescató 3 carruseles que la ficha no trajo |
| Sugeridos del perfil | `chained` en cada escaneo | Sirven para descubrir cuentas |

No uses `web_profile_info`: responde 429.

## Reglas de recolección

1. **Reels desde `/reels/`, carruseles desde el feed.** Se unen por shortcode, se deduplican y luego se ordena o se
   recorta («últimos N», «top N»). Reporta cuántos reels aparecieron solo en `/reels/`: en cuentas grandes pueden ser
   la mayoría (se han visto cuentas con más de mil reels y un contador de 135 publicaciones; en otra, 180 de 200 reels
   no estaban en el feed).
2. **El buscador de Instagram solo lee captions.** Frases de 3 o más palabras devuelven 0; las de 2 palabras sí
   devuelven. Historias contadas solo en el video con caption vacío no aparecen (busca variantes cortas; en Brasil
   funcionó «conta reserva» o «perfil reserva» para historias de cuentas de respaldo tras perder la principal). El idioma de la búsqueda no es el idioma del video: clasifica con portada, caption y
   transcripción.
3. **No hagas clic en miniaturas de hashtags ni adivines handles.** Las miniaturas de `/explore/tags/` llevan a `/p/`,
   donde no se leen bien dueño ni vistas. Un handle se saca del buscador, de una página donde ya estás o de un escaneo;
   adivinar variantes (con o sin punto, con o sin prefijo) gasta 2 a 4 navegaciones por intento.
4. **Una URL de reel contiene `/reel/`.** Las de `/p/` son publicaciones (carruseles o fotos); las de `/explore/` no
   son piezas. `progreso.py revisar` lo comprueba.
5. **El escaneo automático toma los reels más vistos de una cuenta sin filtrar tema.** Siempre hay revisión de
   contenido después: el hashtag-hijacking (fútbol, moda, curiosidades, recetas, contenido religioso, «dark
   psychology») mete falsos positivos.
6. **Progreso persistente y sin repetidos.** Los recolectores retoman solos (saltan lo guardado); el pipeline guarda
   cada paso en la carpeta de la corrida; a mano, `progreso.py`. Fuerza un reescaneo (`FORCE=1`) cuando el anterior es
   viejo.
7. **Muestra tu trabajo.** Después de cada extracción pega en la conversación la salida cruda (la línea que imprime el
   script o un extracto del JSON): así la investigación se puede auditar y no se desvía.

## Descubrir cuentas

1. **Búsquedas por capas** antes de abrir el navegador, 12 a 15 por idioma: núcleo del nicho, problema, solución,
   ángulo específico, audiencia, y sus equivalentes en los otros idiomas. Los hashtags son de una sola palabra
   (`#marcapersonal`, no `#marca personal`); en el buscador, 2 palabras. Guárdalas en el progreso para no repetirlas.
2. **El buscador por palabra clave** (`serp.mjs`) da cuentas con handle exacto.
3. **Colaboradores y coautores** de las piezas que ya calificaron (caption, etiquetas, `coauthors` de la ficha).
4. **Sugeridos** del perfil (`chained` del escaneo).

## Cortar pérdidas

- Una cuenta que no califica cuesta unas 3 llamadas (escanear, leer, anotar). Si tras bajar la cuadrícula dos veces
  no hay piezas que pasen el umbral, anótala como `no_califica` con el motivo y sigue; no recargues ni pruebes otra URL.
- Página «no está disponible» o cuenta privada: se salta sin reintentar.
- Mercado secundario: si tras 2 búsquedas en ese idioma no aparece ninguna pieza que califique, anótalo como hallazgo
  (océano azul en ese mercado) y no vuelvas a esas búsquedas.

## Trampas del navegador

- En headless, la cuadrícula de `/reels/` solo carga con emulación de foco activa
  (`Emulation.setFocusEmulationEnabled`) y con un user agent que no diga «HeadlessChrome» (`research-browser.sh` lo
  fija).
- Pestañas: `PUT` en `/json/new?<url>` (con `GET` devuelve vacío). Cada proceso en paralelo recibe su propia pestaña
  en `TARGET`; dos procesos en la misma pestaña se pisan.
- Tras unas 25 cuentas seguidas la conexión CDP puede morir (`Network.enable` con timeout): reinicia el navegador,
  abre pestañas nuevas y sigue con las que faltan.
- Si conectar por CDP se cuelga aunque `/json/version` responda: `stop` y `start`. Los recolectores de `ig/` ya
  conectan directo al websocket de la pestaña, que no se cuelga.
- Si un script de espera busca su propio nombre con `pgrep -f`, se encuentra a sí mismo y nunca termina: corre en serie.
- Un script que corre con otra carpeta de trabajo necesita rutas absolutas en sus listas (si no, `ENOENT` en cada tanda).

## Clasificación por lotes

Con muchas candidatas, clasifica por lotes con subagentes que lean portada, caption y transcripción (formato exacto
en `recolectores.md`), y pasa un segundo agente que verifique o critique mirando las portadas reales, no solo contando
palabras de las fichas. Normaliza los ids a número antes de unir (un lote puede devolverlos como texto y no sumarse;
`pasos.py elegibles` ya lo hace).
