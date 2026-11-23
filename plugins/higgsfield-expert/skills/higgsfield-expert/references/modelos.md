# Higgsfield — Criterio para elegir modelo

> El catálogo cambia casi cada semana. La lista real, con IDs, parámetros, duraciones y qué medios acepta cada modelo, sale de `models_explore` (`recommend` con tu objetivo y tus insumos; `get` para los límites). Los nombres de abajo son ejemplos de nov-2026: confírmalos antes de usarlos y nunca uses un ID que no devuelva el MCP.

## Qué preguntar a `models_explore`
Describe objetivo + insumos, por ejemplo: "persona realista para UGC, solo texto", "animar esta foto 9:16, sin voz", "video desde foto + mi audio, persona hablando", "logo vectorial". Luego `get` del elegido para ver duración máxima, resoluciones, roles de medios (`start_image`, `audio_references`…) y si genera su propio audio.

## Imagen — qué buscar según la tarea
| Tarea | Busca un modelo que… | Ejemplos nov-2026 |
|---|---|---|
| Persona realista / UGC | sea de retrato realista y acepte personaje guardado | familia Soul (`soul_2`) |
| Texto legible dentro de la imagen (empaque, póster) | destaque en texto | GPT Image, Nano Banana Pro, Ideogram |
| Producto sin texto, volumen barato | sea rápido y económico | Nano Banana, Seedream |
| Color de marca exacto (HEX) | respete instrucciones de color precisas | FLUX |
| Logo, icono, vector | exporte SVG | Recraft (`recraft_v4_1`), Ideogram Vector |
| Editar una foto existente | acepte referencias y edición por instrucción | Seedream, FLUX Kontext, GPT Image |

## Video — qué buscar según la tarea
| Tarea | Busca un modelo que… | Ejemplos nov-2026 |
|---|---|---|
| Animar un still, barato | acepte `start_image` y tenga versión rápida | Kling (turbo/flash), Veo 3.1 Lite |
| Máxima fidelidad visual | sea el tope de calidad (genera su propia voz) | Veo 3.1 |
| Misma persona en varias tomas | acepte referencias de identidad | Seedance |
| Transferir movimiento de un video de referencia | haga motion control / motion transfer | Kling Motion Control, Genjutsu |
| Persona hablando con **tu** audio | acepte audio de referencia o haga lip-sync | ver `lipsync-y-movimiento.md` |
| Física y microexpresiones | destaque en física y emoción | Minimax Hailuo |

## Reglas de decisión
- **Si quieres tu propia locución, no uses un modelo que inventa la voz** (como Veo) para la toma hablada: o apaga su audio y haz lip-sync después, o usa un modelo que reciba tu audio.
- **Un modelo retirado no se sustituye solo:** si un tutorial menciona un ID que `models_explore` ya no devuelve (por ejemplo `veo3`), busca su reemplazo con `recommend` y avisa al usuario del cambio.
- **Router automático** (`image_auto`): sirve para explorar, no para producción repetible; fija el modelo cuando ya te gustó un resultado.
