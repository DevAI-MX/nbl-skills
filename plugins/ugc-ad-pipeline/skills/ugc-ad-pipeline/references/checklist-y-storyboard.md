# UGC Ad — Checklist de producción y plantilla de storyboard

## Checklist por etapa

### 1. Brief
- [ ] Producto y su beneficio #1 (verdadero y comprobable)
- [ ] Audiencia: quién es y qué le duele
- [ ] Ángulo en una frase
- [ ] Plataforma y formato (9:16 por default)
- [ ] Tono y brand brain (voz, HEX, qué NO decir, claims permitidos)
- [ ] Ruta: workflow oficial `ugc-video` o pipeline con voz propia

### 2. Guion
- [ ] Gancho → Empatía → Revelación → Prueba → Llamado
- [ ] Tono "amiga" (tú, `Mira,`, `¿Sabes qué?`)
- [ ] 30 s ≈ 75-90 palabras; oraciones de 10 a 18 palabras
- [ ] Sin resultados inventados, sin testimonio presentado como real
- [ ] Leído en voz alta
- [ ] Aprobado por el dueño de la marca
- [ ] Presupuesto total cotizado y aprobado

### 3. Voz
- [ ] Plan de ElevenLabs con licencia comercial (verificado en pricing)
- [ ] Voz nativa de español mexicano, audicionada con este guion
- [ ] Modelo elegido según la doc vigente; prueba de un párrafo aprobada
- [ ] Export limpio (WAV o MP3 CBR); −16 LUFS para lip-sync

### 4. Talento
- [ ] Persona sintética, o persona real con consentimiento escrito
- [ ] Foto base frontal o ¾, **dientes visibles**, a medio gesto, buena luz
- [ ] Imperfecciones y lente real en el prompt
- [ ] La misma imagen base para todas las tomas

### 5. Animar
- [ ] Modelo confirmado con `models_explore` (duración máxima, acepta tu audio)
- [ ] Tomas cortas, cortes en pausas reales (Whisper + silencedetect)
- [ ] Cada toma verificada re-transcribiendo el corte
- [ ] Una toma de prueba antes de las demás

### 6. Edición
- [ ] Ensamble de tomas
- [ ] Subtítulos clave y llamado en pantalla
- [ ] B-roll REAL donde aplique
- [ ] Música y mezcla (−14 LUFS)
- [ ] Export 9:16 con branding

### 7. Entrega
- [ ] Revisión cuadro por cuadro (labios, manos, texto, logo)
- [ ] Etiqueta de contenido IA según la plataforma
- [ ] Aprobación final del dueño
- [ ] Tomas crudas archivadas por carpeta
- [ ] Gasto real revisado contra el presupuesto

---

## Plantilla de storyboard (toma por toma)

| # | ~Tiempo | Línea (VO) | Visual | Subtítulo | Toma de talento |
|---|---|---|---|---|---|
| 1 | 0-4 s | Gancho | selfie cercano, directo a cámara | gancho en pantalla | nueva A |
| 2 | 4-10 s | Empatía | jump-cut, mismo encuadre | frase clave | reusa A |
| 3 | 10-18 s | Revelación | producto en mano o cutaway | nombre del producto | reusa A |
| 4 | 18-25 s | Prueba | gesto (mano al pecho) + b-roll REAL | dato verdadero | nueva B |
| 5 | 25-30 s | Llamado | cierre + llamado en pantalla | "Compra / Agenda" ↓ | reusa A |

**Clave UGC:** la variedad no viene de muchos ángulos de la persona (eso rompe el realismo y multiplica el costo), sino de **jump-cuts, subtítulos y cutaways**. Bastan 1-2 tomas de talento.
