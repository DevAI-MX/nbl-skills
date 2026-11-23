# ElevenLabs — Elegir modelo y ajustes

> El catálogo cambia. Antes de elegir, abre `elevenlabs.io/docs/overview/models` (o pide la lista de modelos al MCP oficial). Lo de abajo es criterio, no catálogo.

## Cómo elegir modelo (criterio)
| Necesitas… | Busca en la doc el modelo que… | Referencia nov-2026 |
|---|---|---|
| Máxima expresión, audio tags, una voz en varios idiomas | sea el insignia actual | `eleven_v4` |
| La misma voz idéntica en muchos anuncios, guiones largos, números y monedas bien leídos | sea "estable / long-form" | `eleven_multilingual_v2` (también es el default de la API) |
| Tiempo real (agentes, llamadas) | tenga latencia baja | `eleven_v4_turbo`, `eleven_flash_v2_5` |

- Si un modelo aparece como **deprecated** en la doc (hoy: `eleven_turbo_v2_5`, `eleven_turbo_v2`), no lo uses; la doc dice cuál lo reemplaza.
- Cambiar de modelo cambia cómo suena la misma voz. Si un cliente ya aprobó una voz, no cambies de modelo a mitad de campaña sin una prueba A/B.
- Un clon profesional (PVC) se comporta distinto según el modelo. Revisa en la doc con qué modelos está optimizado antes de prometer calidad.

## Ajustes: qué hace cada uno (durable)
Los rangos y qué ajustes existen en cada modelo están en la doc; en los modelos nuevos hay menos perillas (por ejemplo, Eleven v4 expone stability y similarity, y no todos los sliders de v2). Usa esto como dirección:

| Ajuste | Más bajo | Más alto | Punto de partida para anuncio |
|---|---|---|---|
| **Stability** | más vivo, cambia entre tomas; muy bajo se vuelve errático | parejo, tiende a monótono | un poco por debajo del default (~0.40) |
| **Similarity** | se aleja de la voz original | más fiel; muy alto puede meter artefactos | dejar el default (~0.75) |
| **Style** (si existe) | neutro | exagera el estilo de la voz y sube latencia | empezar en 0, subir poco |
| **Speed** (si existe) | más lento, cálido | más rápido, energético | ~0.95 para "amiga"; los extremos degradan |
| **Speaker boost** (si existe) | — | más presencia | encendido |

**Más expresiva sin sonar robot:** baja stability un paso · frases cortas · MAYÚSCULA en la palabra clave (`ESTE producto`) · puntos suspensivos para pausa (`Y la verdad...`) · en v3/v4, audio tags.

## Audio tags (v3 y v4)
Dirección inline entre corchetes. La lista oficial vive en la doc y en el blog de ElevenLabs; los tags experimentales varían por voz.
- **Confiables:** acciones (`[whispers]`, `[laughs]`, `[sighs]`, `[pause]`).
- **Menos confiables:** emociones sueltas (`[excited]`, `[nervously]`). Si un tag se lee como efecto de sonido, descríbelo como cualidad de voz (`[low, warm voice]`).
- **Reglas de oficio:** acción > adjetivo · máximo 2-3 tags en 30 s · si no jala, cambia una palabra antes que el tag · prueba cada tag con la voz elegida.
- En v3/v4 no funcionan las etiquetas `<break>`; usa puntuación y estructura del texto.
