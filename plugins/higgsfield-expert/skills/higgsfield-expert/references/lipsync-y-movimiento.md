# Higgsfield — Persona hablando, lip-sync y movimiento

## Rutas (confirma modelos y límites con `models_explore`)
Pregunta a `models_explore` con `recommend`: "talking head desde una foto + mi audio" o "lip-sync de un video existente con audio nuevo". Revisa con `get` la duración máxima y los roles de medios. En nov-2026 el MCP devolvía, por ejemplo:
- **Foto + tu audio → persona hablando:** `intone` (una o dos personas, varias tomas, audio corto por clip).
- **Video existente + audio nuevo → solo cambia la boca:** `sync_so` (Sync Lipsync).
- **Modelos de video con audio de referencia** (Seedance, Wan): sirven para guiar, pero revisa en `get` si clavan los labios o solo siguen el ritmo.

En la web, **Lipsync Studio** junta más modelos de avatar parlante (algunos no salen por MCP). Si el usuario prefiere la web, dale el prompt y los archivos listos.

Para un anuncio UGC completo, el MCP trae el workflow oficial `ugc-video` (genera voz nativa del modelo). Si el usuario quiere **su** voz o una de ElevenLabs, sigue el flujo de abajo.

## Flujo para UGC con tu voz
**Ruta A (rápida):** foto frontal con **dientes visibles** → modelo foto + audio → tu MP3 normalizado (−16 LUFS, sin silencios largos al inicio ni al final) → prompt de movimiento → la resolución final solo cuando la toma de prueba esté aprobada.

**Ruta B (más cuerpo, dos pasadas):**
1. **Movimiento:** genera el plano con cuerpo y gestos, o transfiere movimiento de un video de referencia de alguien hablando natural (motion control). Sin importar los labios.
2. **Lip-sync video→video** encima con tu MP3: solo cambia la boca y conserva cuerpo y cámara.

## Movimiento + cámara + labios a la vez
El error es pedirlo en un solo paso. Desacopla:
1. Pasada de movimiento (caminar, cámara en movimiento, cuerpo completo), con presets de cámara suaves.
2. Pasada de lip-sync video→video sobre ese clip.

**Límites:** la cara debe seguir visible y casi frontal (perfil u oclusión rompen el sync) · el motion blur de cámara rápida borra los labios: movimientos fluidos · clips de 15 s o menos y ensambla.

## Cómo matar los dos defectos clásicos
**Labios sintéticos:**
- Foto base con **dientes visibles** (le da a la IA la anatomía de la boca).
- Incluye "the person is talking" en el prompt.
- Frases de 15 a 20 s máximo, no párrafos.
- Audio a −16 LUFS (audio bajito = boca tímida), limpio, con 0.2 s de cola.
- Cara frontal o ¾ máximo.

**Cuerpo estático (cabeza flotante):**
- Dos pasadas (movimiento → lip-sync).
- Si solo animas la foto: `"subtle torso sway, natural breathing, gestural hand movement near chest"`.
- Foto base con la persona **a medio gesto**, no parada tiesa.
- `"handheld micro-shake"` disimula la rigidez con movimiento de cámara.

## Cortar el audio en tomas
1. Transcribe el VO con Whisper a nivel de palabra (`-l es`).
2. Detecta pausas reales (`ffmpeg -af silencedetect`) y corta **solo en pausas**, nunca a media palabra.
3. Cada toma dentro de la duración máxima del modelo (dato de `get`). Normaliza cada una (`loudnorm`) y verifica re-transcribiendo el corte.
