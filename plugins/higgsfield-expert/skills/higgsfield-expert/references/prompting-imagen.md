# Higgsfield — Prompting de imagen, consistencia y cámara

## JSON prompting (control quirúrgico)
JSON separa conceptos: el color del fondo deja de "sangrar" al sujeto y el prompt se vuelve plantilla repetible. Funciona mejor en modelos con buen seguimiento de instrucciones (Nano Banana Pro, FLUX, GPT Image, Seedream). Mándalo como texto en el campo `prompt`.

```json
{
  "label": "skincare-hero-v3",
  "Subject": ["mujer de 30 y tantos", "cabello oscuro liso", "maquillaje natural", "textura de piel real"],
  "Arrangement": "de pie, giro 3/4, peso en el pie izquierdo",
  "Background": "ciclorama beige cálido neutro",
  "ColorRestriction": ["tonos tungsteno cálidos", "marfil/beige/terracota", "sin primarios saturados"],
  "Camera": {"type": "medium format", "lens": "85mm", "aperture": "f/2.0", "grain": "ISO400 leve"},
  "OutputStyle": "editorial commercial photography",
  "Mood": "confident, calm, aspirational"
}
```

**Reglas:**
- `Subject` como **lista**: cada rasgo se lee como una restricción separada.
- `ColorRestriction` dice lo **permitido**, no lo prohibido. Para salud/estética: `["blancos clínicos fríos", "1 acento #0077B6", "mate, sin brillos"]`.
- `Camera` como objeto anidado activa el razonamiento fotográfico (apertura → profundidad de campo).
- **JSON desde una foto real:** analiza la foto con visión y devuelve el JSON; para más fidelidad, manda también la foto como referencia.
- No uses banderas de Midjourney (`--ar`) en el prompt: usa los parámetros del MCP (`aspect_ratio`, resolución, calidad).

## Persona fotorrealista (fórmula de 8 partes)
```
[disparador de realismo] + [sujeto e identidad] + [acción] + [lugar] + [luz concreta] +
[cámara y lente] + [imperfección] + [color y tono]
```
**El truco #1 anti-IA es la imperfección:** `visible skin pores, natural hair flyaways, slight fabric wrinkle` + lente real (`35mm f/2.0`).
Los negativos ("sin…") funcionan mal en muchos modelos de retrato; mejor describe lo que sí quieres, usa estilos/presets y una foto de referencia.

## Consistencia de personaje
- **Personaje entrenado con fotos de una persona real** (Soul ID u equivalente): solo con fotos propias o con consentimiento escrito. Pide fotos variadas (ángulos, expresiones, una de cuerpo completo), recientes, con buena luz, sin lentes oscuros ni grupos. Cuántas fotos y cuánto tarda: lo indica la herramienta.
- **Actor sintético** (sin fotos, por parámetros): para talento de anuncio que no es nadie real.
- Para video, usa la imagen del personaje como `start_image` o referencia en un modelo que preserve identidad (`models_explore`: "consistent identity").
- Reusa **la misma imagen base** en todas las tomas; cambiar de foto cambia de persona.

## Cámara: regla de tono
**Lento = lujo/premium. Rápido = viral/barato.**

| Marca | Movimientos | Evitar |
|---|---|---|
| Salud / estética | dolly in lento, crane up, cambio de foco, fijo | crash zoom, whip pan, FPV, plano holandés |
| Belleza / lujo | dolly in, timelapse glam | zooms bruscos, wiggle, cámara en mano |
| UGC directo a consumidor | **cámara en mano**, zoom rápido | grúa, giratorio |
| TikTok viral | crash zoom, whip pan, FPV | plano fijo, grúa |

**3 reglas:** un movimiento por clip · clips de 4 a 8 s (más largo expone deriva) · la puesta en escena se resuelve en el still, antes de animar. Los presets vigentes: `get_presets`.
