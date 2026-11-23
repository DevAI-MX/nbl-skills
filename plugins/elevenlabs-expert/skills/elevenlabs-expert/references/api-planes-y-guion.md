# ElevenLabs — Licencia, guion en español y entrega

## Licencia (revísala primero)
- **Free:** sin licencia comercial y con atribución obligatoria. No sirve para anuncios, contenido de marca ni trabajo para clientes.
- **Plan pagado:** el audio que generas mientras pagas se puede usar comercialmente, también después de cancelar. Lo que generes ya en Free vuelve a tener las restricciones de Free.
- Qué plan es el mínimo con licencia comercial, cuál incluye clonación y cuántos créditos trae cada uno: **consúltalo en `elevenlabs.io/pricing`** el día que lo necesites. Los precios y créditos cambian varias veces al año.
- **Cálculo de costo:** el cobro va por caracteres y depende del modelo. Cuenta los caracteres del guion, multiplica por las tomas que esperas (de 3 a 5 por anuncio es normal) y dile al usuario el total antes de generar.

## Guion expresivo en español
- **Regla de oro:** si suena raro leído en voz alta, sonará raro en la IA. Léelo en voz alta antes de generar.
- Oraciones de 10 a 18 palabras, una idea por oración.
- Tono "amiga": tú, aperturas coloquiales (`Mira,` `Oye,` `¿Sabes qué?`). Nada de lenguaje de blog ni de folleto.
- **Puntuación = dirección:** `.` pausa · `,` transición suave · `—` énfasis · `...` suspenso · `!` emoción (poco) · MAYÚSCULA = acento en esa palabra.
- 30 s ≈ 75 a 90 palabras en español.
- Guiones largos: en trozos de un párrafo con la misma voz, el mismo modelo y los mismos ajustes (y el mismo `seed` si usas la API) para que suene parejo; ensambla en el editor.

### Estructura UGC de 30 s
```
Gancho (4 s): pregunta con la que la audiencia se identifica
Empatía (3 s): "yo estaba igual…"
Revelación (5 s): el producto o la solución
Prueba (8 s): resultado concreto y verdadero, detalle sensorial
Llamado (5 s): acción clara ("el link está aquí abajo")
```
No inventes resultados, cifras ni testimonios. Si el producto es de salud, que el guion hable de experiencia, no de curas.

## API y entrega
- La referencia de text-to-speech en la doc oficial dice qué campos acepta cada modelo. Dos trampas comunes: `language_code` no fija acento y en Multilingual v2 se ignora; `apply_language_text_normalization` es solo para japonés.
- Formatos: el MP3 128 kbps es el default; la doc indica qué plan desbloquea 192 kbps y WAV/PCM.
- **Si el editor o una IA de video rechaza el MP3** (duración rara, desfase), re-encodea a algo limpio:
  - WAV: `ffmpeg -i in.mp3 out.wav`
  - MP3 CBR: `ffmpeg -i in.mp3 -c:a libmp3lame -b:a 192k -ar 44100 -ac 2 out.mp3`
- Si unes varias tomas, que todas tengan el mismo formato y frecuencia; mezclar provoca desfase.

## Post (para redes)
Compresión ligera, un poco de brillo en 3 a 5 kHz para presencia, normaliza a −14 LUFS para redes (−16 LUFS si el audio va a una IA de lip-sync). No pidas reverb en el prompt.
