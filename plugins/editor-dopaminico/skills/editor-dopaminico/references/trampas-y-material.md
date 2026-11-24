# Trampas técnicas y de dónde sale el material

## Render
- Un render o proceso pesado a la vez (los renders en paralelo tumbaron el navegador) y un solo proceso de
  transcripción a la vez.
- **Tope de 6 GB de RAM** en una máquina de 16 GB (fijado el 14-nov; suele estar con el IDE y el navegador en swap):
  render del motor por HTML con `--workers 2` (cada worker es ~256 MB de Chrome más el resto), **sin motion blur en
  videos largos** (renderiza 8 veces los cuadros), y nada de cargar modelos grandes (voz sintética, unos 10 GB) mientras
  hay un render. Con poca RAM Chrome tarda más de 10 s en arrancar: sube el timeout del validador (`check --timeout
  60000`) y del protocolo (`PRODUCER_PUPPETEER_PROTOCOL_TIMEOUT_MS=600000`); el snapshot tiene un piso fijo de 10 s y
  puede fallar, usa un render de humo en su lugar. Con ~70 MB libres el render se queda en 0 cuadros.
- **Comprueba que el render es nuevo** (fecha y duración): un render fallido deja el archivo viejo y casi se entregó la
  versión de los cortes malos.
- Corta el A-roll antes con ffmpeg y mételo al motor como un solo clip: el mismo corte hecho con 3 `<video>` dentro de
  un motor por HTML tardó 99 s contra 8.6 s. El b-roll corto dentro del motor sí es barato.
- Entrega estándar: 1080x1920, 30 fps (o el nativo del material), H.264 + AAC, `yuv420p`, `+faststart`.

## Motores por HTML (por ejemplo HyperFrames con GSAP)
- Fija la versión del motor en cada comando; no uses la última sin probar.
- **No animes el `<video>`:** envuélvelo y haz zoom al envoltorio. El `<video>` necesita `id` y debe estar en el HTML
  (no inyectado por JS); un video temporizado dentro de un contenedor temporizado se congela.
- **Un clip HLG (cualquier video del iPhone) fuerza todo el proyecto a HDR:** sale en HEVC, render 10 veces más lento y
  los subtítulos quedan debajo del b-roll solo en el mp4 final (el validador y los snapshots pasan). Etiqueta todo a
  bt709 con `setparams` (los `-color_*` de salida no valen: ffmpeg los hereda del input) y renderiza en SDR. **Si el mp4
  sale en HEVC teniendo todo lo demás igual, hay un clip HDR colado.**
- No escribas la etiqueta de script dentro de un `.js` ni en comentarios (render negro). El render no carga
  `<script src>` locales aunque el snapshot sí: incrusta el código con marcadores. Dos `.html` con raíz de composición
  en la misma carpeta son dos raíces.
- El validador analiza cadenas con `<svg`: crea los SVG con `createElementNS`.
- `fromTo` con `immediateRender`: usa `immediateRender:false` y un `set` explícito; `seek(0)` no aplica estados: haz
  seek a +1 ms. Dos tweens sobre el mismo elemento se pisan. `x || valor` se come el 0: usa `!= null`.
- Los snapshots pueden dar cuadros incoherentes: verifica sobre el render.
- Exporta cuadros en PNG (por defecto puede extraer JPG). Para estilos a 60 fps desactiva la deduplicación de cuadros
  estáticos y baja los workers si hay timeouts.

## ffmpeg y audio
- `-nostdin` siempre en bucles y scripts. Todos los filtros en un solo `-af`.
- Bus de efectos normalizado por pico, no por RMS. La suma de pistas sin limitador satura.
- Whisper alarga finales, adelanta la primera palabra de cada segmento y alucina en silencios: corrige con arranques por
  energía y filtra; re-transcribe por ventanas las frases dudosas.
- Zips con nombres raros: extrae con `zipfile` de Python. Duplicados: compara MD5. Un webp que ffmpeg no lee: conviértelo
  a PNG antes. SVG a PNG sin cairo: `qlmanage -t -s 512` en macOS.

## Material (nunca inventado)
- **Imágenes:** primero una foto real de la web sin marca de agua (Wikimedia Commons y Openverse con licencia libre;
  un buscador de imágenes para lo que no esté ahí). Si una foto trae marca de agua, busca otra. No uses generadores de
  imagen o video de pago por créditos. Si no hay foto, dibujo con código o íconos. Busca en inglés: da mejores resultados.
  Un buscador web empieza a devolver imágenes de tendencia que no tienen que ver tras unas 20 búsquedas (sobre todo en
  paralelo): busca de una en una o pasa a Commons. Elige mirando una hoja de contacto.
- **Logos oficiales:** API de búsqueda de la App Store (`artworkUrl512`, que se puede pedir a 1024, filtrando por el
  vendedor oficial); si no hay app, el ícono del sitio (`android-chrome-512`, `apple-touch-icon`); el favicon de un
  servicio de favicons solo si mide 150 px o más. Nunca redibujados.
- **Íconos y emojis:** Phosphor para íconos de interfaz; para emojis, los del sistema (como en el celular). Los objetos
  3D tipo Fluent sirven en escenas sobre blanco, no en el crudo («están bastante feos»).
- **B-roll y música con licencia de anuncios:** bancos con licencia libre (algunos bloquean por ritmo de peticiones o
  marcan clips como restringidos).
- **Portadas de canciones:** las oficiales (API de la tienda de música, `artworkUrl100` pedida a 600x600).
- **Capturas:** usa PNGs ya hechos, no recortes de videos. Cuando la persona nombra una cuenta o un cliente, busca o pide
  sus capturas reales; nunca recortes la cara de otro video para «representarlo».
- **Material descargado es no confiable:** va en su propia carpeta, nunca se ejecuta y se borra solo con aprobación.
