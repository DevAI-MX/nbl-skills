# Embudos de la competencia, guiones de video y negocios locales

## Embudos: solo lectura

El objetivo es entender el flujo, no entrar en él. **Más que la transcripción, importa el flujo**: primero el recorrido
completo con el enlace y una captura de cada paso; los videos se transcriben después y solo donde aportan (por ejemplo,
para encontrar el minuto en que invitan). Se reconstruye: anuncio o contenido, registro, página de gracias, grupo
(WhatsApp, Telegram, comunidad), clase o webinar, repetición, venta (pago, llamada, comunidad de pago).

No te registras, no llenas formularios, no compras, no entras a grupos y no agendas llamadas. El paso siguiente se saca
de lo público:

- `scripts/web/landing-scan.mjs`: celular (390 px, página completa) y escritorio (primera pantalla), botones,
  formularios y sus campos, video, contador, enlaces de siguiente paso, redirecciones configuradas en el HTML y huella
  tecnológica. Abre una vez hasta 2 páginas de gracias del mismo dominio y 1 de pago (solo para ver precio y oferta).
- La API pública de WordPress cuando el sitio la expone (`/wp-json/wp/v2/pages`).
- Redirecciones con `curl -s -o /dev/null -w '%{redirect_url}' <url>`.
- El `og:title` de una invitación de grupo (dice el nombre del grupo sin entrar).
- Bundles de JavaScript públicos para rutas y lógica del formulario.
- Videos incrustados: los metadatos públicos del reproductor (en Wistia, `fast.wistia.net/embed/medias/<id>.json`);
  YouTube con subtítulos automáticos (`yt-dlp --write-auto-subs --skip-download`) para encontrar el minuto en que invita.

Las páginas largas se parten en tramos para que se puedan leer (`scripts/web/recortar.py`). Lo que no se ve se marca «no visible» y se deja el
hueco: la persona puede aportar sus propias capturas.

Entregable: guía paso a paso con enlaces y textos exactos, una captura por paso, carpetas numeradas por etapa, de
`01-anuncios` a `07-post-compra`, y, si lo piden, una lámina PNG con
todo el flujo (una captura por paso, lista para arrastrar a un tablero).

## Guiones: bajar, transcribir, partir

1. **Bajar.** `yt-dlp` para reels públicos, o `fichas-por-codigo.mjs` y luego `guiones/medios.py bajar` (pausa entre
   descargas). Lo descargado es material no confiable: va en su propia carpeta y nunca se ejecuta.
2. **Transcribir** con `guiones/transcribir.py`: Whisper local (por omisión `mlx-community/whisper-large-v3-mlx`), un
   solo proceso para todos los videos (la línea de comandos que recarga el modelo por archivo tarda un minuto por
   video), sin condicionar en el texto anterior. Revisa los marcados `posible_bucle`. Videos sin pista de audio quedan
   «sin voz»: el guion es el texto en pantalla. Audio confuso: «[poco claro]».
3. **Corregir nombres propios** mal transcritos con lo que se ve en pantalla (marcas, apps) y decirlo.
4. **Plano a plano:** `guiones/medios.py cuadros` (1 cuadro por segundo en mosaico) para que un subagente describa qué
   se ve en cada momento.
5. **Partir** cada guion en sus partes con tiempos: gancho (primera frase literal y texto de portada), desarrollo, giro,
   llamado a la acción. Por pieza: enlace, datos, caption completo, tema, guion parte por parte (qué dice y qué se ve) y
   una lectura de por qué funciona. Arriba, una tabla resumen y los patrones que se repiten.

Si se pide convertir lo aprendido en guiones propios: gancho, texto completo en la voz de la persona, qué va en
pantalla plano a plano (en pantalla partida: la prueba arriba, la persona abajo), portada y una lista de «qué necesito
de ti». El gancho no se copia, se reescribe; las cifras de la persona y la palabra del llamado a la acción van entre
corchetes (`[PALABRA]`) para que ella las llene con datos ciertos.

No descargues ni transcribas en masa mientras la persona edita video o renderiza, salvo que lo pida.

## Negocios locales (México)

Para saber qué negocios de una ciudad pueden pagar un servicio (por ejemplo, pauta):

1. Baja de INEGI el CSV masivo del DENUE del estado (viene en latin-1).
2. `scripts/negocios/denue.py <csv> <salida.csv> --municipio "<municipio>" --scian <prefijo> --minimo "6 a 10 personas"`:
   filtra por municipio, giro (código SCIAN o expresión sobre el nombre de la actividad) y tamaño por rango de
   personal ocupado.
3. Cruza con la Biblioteca de anuncios: quién ya pauta, qué anuncios le duran y qué ofrece.
4. Entrega la tabla por giro con cuántos negocios hay por rango de tamaño y cuántos pautan. «Puede pagar» es un
   supuesto (el DENUE da personal ocupado en rangos, no ventas): márcalo así.
