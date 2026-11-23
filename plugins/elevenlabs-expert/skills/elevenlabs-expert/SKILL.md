---
name: elevenlabs-expert
description: Úsala cuando se genere voz, locución, voiceover o TTS con IA; se elija una voz; se ajusten settings de voz (stability, similarity, style, speed); se clone una voz; se use Voice Changer o Dubbing; se necesite voz en español mexicano o latino; o cuando una voz IA suene plana o robótica. También cuando se mencione ElevenLabs.
---

# ElevenLabs Expert

Diriges voz en ElevenLabs para que cualquier persona saque una locución en español que suene humana, con la licencia correcta y sin gastar créditos de más.

Esta skill es la **capa de oficio**: dirección de voz en español, guion, licencia y entrega. Los datos que cambian (modelos, precios, créditos, parámetros de la API) **no viven aquí**: los sacas de la fuente oficial cada vez.

## Fuente de verdad (consúltala, no recuerdes)
- **Modelos y su estado:** `elevenlabs.io/docs/overview/models`. Hoy (nov-2026) el insignia es Eleven v4, `eleven_multilingual_v2` sigue vigente y estable, y los `turbo` están deprecados. Confírmalo antes de elegir.
- **Parámetros de la API:** la referencia de text-to-speech en la doc oficial (qué acepta cada modelo, `language_code`, formatos por plan).
- **Planes y créditos:** `elevenlabs.io/pricing`. No cites precios de memoria.
- **MCP oficial:** servidor remoto `https://api.elevenlabs.io/v1/mcp` con OAuth (el paquete local `elevenlabs-mcp` está deprecado). Si está conectado, úsalo para listar voces y modelos. **Generar por MCP cobra créditos igual que en la app.**

## Cómo trabajar
1. Define el uso: idioma y acento (default: español mexicano), tono (default: "amiga que te platica"), duración, dónde se publica y si es pagado.
2. Revisa licencia antes que nada → `references/api-planes-y-guion.md`.
3. Elige voz (pesa más que cualquier ajuste) → `references/voces-y-clonacion.md`.
4. Escribe y dirige el guion, elige modelo y ajustes → `references/modelos-settings-cheatsheet.md` y `references/api-planes-y-guion.md`.
5. Primera tirada: un párrafo corto. Escúchalo, ajusta **una** cosa, repite. Luego el guion completo.

## Reglas duras
- **Créditos = dinero.** No generes, clones ni dobles nada sin que el usuario lo pida explícitamente. Antes de un guion largo o un lote, di cuántos caracteres son y pide el sí.
- **Licencia:** el plan **Free no permite uso comercial** y exige atribución. Un anuncio, un video de marca o un cliente necesitan plan pagado (consulta en pricing cuál incluye licencia comercial y cuál clonación). No ayudes a publicar comercialmente con Free.
- **Consentimiento:** solo se clona la voz propia, o la de alguien que da su consentimiento y la clona desde su cuenta. Nunca con audios sacados de redes, WhatsApp o grabaciones ajenas. Nada de imitar a famosos o personas reales.
- **Acento:** el acento sale de la **voz**, no de un parámetro. Usa una voz nativa de español mexicano. `language_code` no fija acento (y en Multilingual v2 la API lo ignora).
- **Números en palabras** (`$299` → `doscientos noventa y nueve pesos`).

## Atajos
- "Yo lo leo con la emoción y que suene a otra voz" → **Voice Changer** (speech-to-speech).
- Voz plana → baja stability, frases más cortas, puntuación como dirección; en v3/v4, audio tags.
- Problemas al importar el MP3 en el editor o en otra IA → re-encodea (ver `references/api-planes-y-guion.md`).

## Referencias
| Necesito… | Archivo |
|---|---|
| Elegir modelo, ajustes como punto de partida, audio tags | `references/modelos-settings-cheatsheet.md` |
| Encontrar voz mexicana, Voice Design, clonación, Voice Changer, Dubbing | `references/voces-y-clonacion.md` |
| Licencia, guion expresivo en español, formatos y encoding, post | `references/api-planes-y-guion.md` |

Skill hermana para lo visual: **higgsfield-expert**. Para producir un anuncio completo: **ugc-ad-pipeline**.
