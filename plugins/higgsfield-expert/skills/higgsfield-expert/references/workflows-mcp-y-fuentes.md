# Higgsfield — Workflows oficiales, pipeline y anti-patrones

## Usa los workflows del MCP
`get_workflow_instructions` sin argumento lista los workflows vigentes y cuándo aplica cada uno; con su nombre carga las instrucciones completas. Síguelas: están al día con los modelos y herramientas. En nov-2026 había, entre otros:

| Quieres… | Workflow |
|---|---|
| Video UGC (reseña, unboxing, try-on, tutorial) con voz nativa del modelo | `ugc-video` |
| Anuncios estáticos con copy (Meta, etc.) | `ads-studio` |
| Fotos de producto, packshots, lifestyle | `product-photoshoot` |
| Variantes de un anuncio que ya tienes | `ad-multiplier` |
| Unir clips, música, subtítulos | `video-montage` |
| Doblar tu video a otros idiomas | `creator-dub` |

Esta skill agrega lo que esos workflows no traen: guion y voz en español mexicano, trucos anti-IA, aprobación de costo y ética. Si el usuario quiere su propia voz (o ElevenLabs), usa **ugc-ad-pipeline**.

## Pipeline genérico (cuando no hay workflow)
```
1. BRIEF    → marca, audiencia, ángulo, formato, qué NO decir
2. STILL    → modelo de imagen + JSON con ColorRestriction; aprobar
3. COTIZAR  → estimate_*_cost; aprobar total
4. ANIMAR   → still como start_image + un movimiento de cámara acorde al tono
5. ENSAMBLE → video-montage o editor externo (ffmpeg/CapCut): cortes, subtítulos, música, llamado, 9:16
6. REVISAR  → mira cada clip: identidad, manos, texto, labios; opcional virality_predictor (cobra)
```
**Brand brain:** antes de generar, junta en un archivo la voz de la marca, personas, ganadores previos, colores HEX y qué no decir, y léelo en el chat. Cada prompt lo hereda.

## Detalles del MCP que confunden
- Los medios se pasan por ID (súbelos o impórtalos con las herramientas de media), no por URL suelta.
- Cada modelo define sus roles de medios; revisa con `models_explore get`.
- Video es asíncrono: espera con la herramienta de espera que indica el MCP. Un timeout no es un fallo; no reenvíes.
- Para varias generaciones independientes usa las herramientas batch y una sola espera.

## Anti-patrones
- Generar sin cotizar o lanzar un lote sin una prueba.
- Creer que "ilimitado" en la web también lo es por MCP.
- Pedir un video largo en vez de ensamblar clips cortos.
- Usar un modelo que inventa la voz cuando el usuario quiere su locución.
- Copiar IDs de modelos de un tutorial viejo sin verificarlos en `models_explore`.
- Usar MCPs no oficiales que piden la cookie de tu sesión del navegador: riesgo para tu cuenta y fuera de los términos.
- En salud: plano holandés, antes/después falsos, claims inventados, animar al profesional real diciendo lo que no dijo.
