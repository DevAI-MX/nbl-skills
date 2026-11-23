---
name: ugc-ad-pipeline
description: Úsala cuando alguien quiera crear un anuncio o ad UGC completo — video vertical estilo creador (9:16), una persona hablando a cámara, comercial o testimonial con IA — o llevar una idea de marca hasta un video final editado combinando imagen, voz y video con IA.
---

# UGC Ad Pipeline

Orquestas un anuncio UGC vertical de principio a fin. El usuario trae una idea; tú entregas el video. Tú manejas y el usuario solo aprueba en los puntos que cuestan dinero o comprometen a la marca.

Apóyate en **higgsfield-expert** (imagen, video, lip-sync) y **elevenlabs-expert** (voz). Los modelos, precios y herramientas vigentes salen de sus MCP y docs oficiales, no de esta skill.

## Primero: ¿qué ruta?
- **Rápida, voz generada por el modelo:** si Higgsfield está conectado, carga su workflow oficial `ugc-video` (`get_workflow_instructions`) y síguelo. Tú aportas brief, guion en español y guardrails.
- **Con voz propia o de ElevenLabs, más control:** las 7 etapas de abajo.
Pregunta una vez cuál prefiere si no es obvio. Default: voz de ElevenLabs (suena más natural en español mexicano y se reusa en toda la campaña).

## Las 7 etapas
1. **BRIEF** — Producto, audiencia y su dolor, ángulo en una frase, plataforma, tono, qué NO decir. Si hay marca, arma un brand brain (voz, personas, colores HEX, prohibidos).
2. **GUION** — Gancho → Empatía → Revelación → Prueba → Llamado. Tono "amiga", 30 s ≈ 75-90 palabras. Léelo en voz alta. **Aprobación del usuario.**
3. **VOZ** — `elevenlabs-expert`: plan con licencia comercial, voz nativa mexicana, prueba con un párrafo; o Voice Changer si el usuario quiere grabar. Normaliza a −16 LUFS.
4. **TALENTO** — `higgsfield-expert`: persona sintética realista (o la persona real que dio su consentimiento). Foto base frontal o ¾, **dientes visibles**, a medio gesto, con imperfecciones y lente real.
5. **ANIMAR** — `higgsfield-expert` → lip-sync: foto + audio o dos pasadas (movimiento → lip-sync). Tomas cortas, cortes en pausas reales. Una toma de prueba antes de las demás.
6. **EDICIÓN** — ffmpeg local o el workflow `video-montage`: ensamble, subtítulos, b-roll, música, llamado en pantalla, export 9:16.
7. **ENTREGA** — Revisa cada toma (labios, manos, texto). Etiqueta de contenido IA. **Aprobación final del dueño** antes de publicar.

## Puntos de cobro (pide el sí antes de cada uno)
Voz (caracteres × tomas) · imágenes de talento · cada clip de video · lip-sync · cualquier predicción o upscale. Presenta un **presupuesto total** después del guion: cotiza con las herramientas de costo del MCP y suma. Aunque el usuario diga "no me preguntes", no gastes sin un sí a ese total.

## Guardrails
- **Testimonios:** la actriz IA da una **opinión** o cuenta una experiencia de uso; nunca se presenta como clienta real ni promete resultados que no estén comprobados. Nada de antes/después falsos, cifras inventadas ni "me curó".
- **Salud y profesionales:** sin claims médicos no aprobados. Un profesional real aparece solo con material real, o con su consentimiento escrito y su aprobación del guion exacto.
- **Personas reales:** nada de famosos ni de clonar la cara o la voz de alguien sin su permiso.
- **Licencia de voz:** ElevenLabs Free no sirve para anuncios.
- **Etiqueta de IA** según la política vigente de la plataforma (Meta, TikTok, YouTube).

## Referencia
Checklist por etapa y plantilla de storyboard: `references/checklist-y-storyboard.md`.

Salida: un MP4 9:16 listo para TikTok/Reels/Meta (voz + subtítulos + música + llamado), más las tomas crudas por carpeta.
