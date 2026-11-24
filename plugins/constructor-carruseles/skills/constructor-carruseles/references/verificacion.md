# Verificación y errores comunes

## Antes de entregar
1. Corre `python3 "<carpeta de la skill>/scripts/revisar.py" "carruseles/AAAA-MM-DD_tema"` (agrega
   `--plataforma tiktok` para esa versión). Mide lo que se puede medir: campos sin llenar, flecha o número
   de slide, etiquetas encima del título, negritas en el formato tuit, cierre con palabra que no enseña el
   recurso, pie distinto, @ repetido, palabras por lámina interior (título 14, cuerpo 30), total de slides,
   palabra del cierre contra `marca/palabras-activas.txt` (una por renglón) y que cada PNG mida 2160x2700.
   Con errores no se entrega.
2. Si una portada viene hecha de un generador, recórtala a 4:5 con
   `python3 "<carpeta de la skill>/scripts/recortar_45.py" portada.png png/slide-01.png` (con
   `--centro-y` para subir o bajar el encuadre). Si viene en otra resolución 4:5 (por ejemplo 1122x1402),
   avisa que en Instagram se ve igual.
3. Mira los PNG, no el HTML. Para muchos a la vez, usa el `preview.html` o arma una hoja de contactos.
4. Nada se sale, nada se encima, sin palabras sueltas al final de un renglón («ven.», «una.», «día.»), se
   leen todos los números de las capturas.
5. El copy es idéntico al aprobado, palabra por palabra: no se puede perder ni una frase.
6. `preview.html` en cuadrícula que muestre todos los slides, portada incluida, sin scroll horizontal.
7. Sin procesos de navegador huérfanos.

## Trucos de maquetación
- `text-wrap: balance` en títulos y `text-wrap: pretty` en párrafos evitan palabras sueltas.
- Auto-ajuste para texto largo: un contenedor que se escala con `zoom = alto disponible / scrollHeight`
  (ya viene en la plantilla `limpio`) para que nunca se salga, en vez de achicar márgenes. Para títulos de
  varias líneas con `nowrap`, el mismo ajuste por grupo para que todas las líneas queden del mismo tamaño.
- Usa un `div` con `background-image` en lugar de `<img>` cuando la imagen todavía no llega: no sale el
  ícono de imagen rota y basta con dejar el archivo en la carpeta.
- Si falta una captura, pinta un recuadro punteado que diga qué captura va ahí (bloque `HUECO` de la
  plantilla `limpio`).
- Migas de navegación para explicar dónde tocar: «Más opciones › Traducir reel › Traducir al».

## Fotos y capturas
- «La última imagen que descargué» es la más reciente por fecha en Descargas (`ls -t`). Para nombres con
  caracteres raros (capturas de macOS): `f=$(ls -t ~/Desktop/Captura*.png | head -1); cp "$f" destino`.
- **Fotos del iPhone (HEIC):** conviértelas respetando la rotación guardada. En Mac, `qlmanage -t -s 4032`
  la respeta (y luego `sips` si hace falta); `sips` solo ignora la rotación y `sips -r 90` la aplica dos
  veces.
- Portada de un PDF como imagen (para enseñar el recurso en el cierre): `qlmanage -t -s 1400 -o <dir> "<pdf>"`.
- **Capturas con datos de terceros:** recorta caras y nombres de contactos.
- **Imágenes de ejemplo reales:** Wikimedia Commons (búsqueda por API con `list=search&srnamespace=6` e
  `imageinfo` con `extmetadata` para la licencia; anótala en `CREDITOS.md`), catálogo oficial del
  fabricante cuando se muestra un producto (anotado como no libre), íconos de librerías abiertas (por
  ejemplo Lucide) o capturas de la persona. Si un PNG de un ícono sale chico (256 px), busca la versión
  vectorial. Los diagramas sí se diseñan.

## Editor de portada
Cuando la persona quiere encuadrar ella la foto y el texto, copia `assets/editor-portada.html` a la carpeta
del carrusel y ábreselo. Ella arrastra la foto y ajusta zoom (1 a 2.6), tamaño del texto y altura del
bloque, y te pasa `{x, y, zoom, font, bottom}`. En la portada la foto va en `<img id="foto">` con
`transform: translate(Xpx, Ypx) scale(Z)` y esos valores se hornean tal cual. Con zoom 1.00 y un
desplazamiento grande salen barras negras: sube el zoom al mínimo que cubra (1.10 a 1.20).

## Errores ya vistos y su arreglo
- **Choque de nombres de clase CSS:** una clase genérica (`.photo`, `.follow`) hereda estilos de otro
  componente y lo desacomoda (un encabezado cayó a media slide, un ícono se deformó). Usa prefijos únicos.
- **Anillo de historia descentrado:** falta `display:flex` en el contenedor del anillo.
- **Palomita de verificado partida:** el SVG está mal formado; usa el sello de 8 puntas limpio.
- **Cinta o bloque cortado** por un `height:100%`: usa `flex:1`.
- **Título con la coma pegada a la línea de abajo:** `line-height` muy bajo (0.9); súbelo a ~0.98 y fuerza
  el salto con `<br>`.
- **Pie de página a media slide:** un espaciador `flex:1` antes del pie, y el título en `nowrap` si hace
  falta.
- **Documento borroso del cierre que desborda y tapa el texto:** recorta el contenedor a una tarjeta que se
  desvanece abajo, con el sello nítido.
- **X de «tachado» separada del ícono y con brazos desiguales:** métela dentro del ícono para que comparta
  la misma inclinación, sin perspectiva propia, y mide los cuatro brazos.
- **Rayado de barras incompleto:** `clipPath` con líneas que empiezan en `i = -h`.
- **Barras negras al encuadrar una foto con desplazamiento:** sube el zoom al mínimo que cubra.
- **Preview que muestra solo algunos slides:** cuadrícula que haga wrap.
- **`ERR_MODULE_NOT_FOUND` al renderizar:** corre el render desde la carpeta donde está
  `node_modules/playwright`.
- **«Executable doesn't exist» de Chromium:** el Chromium de Playwright no está instalado; corre
  `npx playwright install chromium` o pon la ruta de tu navegador en `BRAVE_PATH` (Brave) o `BROWSER_PATH`
  (Chrome u otro). Los dos scripts que abren navegador (`render.mjs` y `bajar_referencia.mjs`) aceptan las dos.
- En macOS no existe el comando `timeout`: no lo uses en los comandos.
