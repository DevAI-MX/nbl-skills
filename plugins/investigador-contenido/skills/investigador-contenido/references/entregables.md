# Entregables por modo

Todo va en Markdown, con nombre `<tema>_<AAAA-MM>.md`, y los datos crudos en `<tema>_<fecha>/` al lado. Números en
tablas. Cada documento termina con **Método y límites**: búsquedas hechas, cuentas escaneadas, descartes con su motivo,
qué no cubre y qué es supuesto.

## 1. Viral por nicho
- **Tabla 1, piezas:** n, cuenta, seguidores, mercado, idioma, formato, vistas (o likes y alcance estimado si es
  carrusel), veces sus seguidores y nivel, fecha, enlace, tema o ángulo, gancho literal (primera frase y texto de
  portada), caption hasta 600 caracteres. `pasos.py documento` la arma con la ficha de cada pieza.
- **Tabla 2, temas más repetidos:** tema, cuántas piezas, cuentas clave y su motor de viralidad (validación,
  revelación, miedo o urgencia, controversia, empoderamiento, identidad), ordenada de más a menos frecuente.
- **Tendencias** e **insights accionables:** fórmula dominante, huecos (temas que nadie cubre en el idioma de la
  persona), cuentas chicas que rompen, mercados sin resultados (océano azul), patrones de formato y duración.
- **Aparte, los 12 carruseles con más likes de cada idioma**, con la equivalencia vistas por like usada.
- Carpeta de portadas numeradas igual que la tabla.
- Si se juntan varias investigaciones, un **consolidado** ordenado de la mejor a la peor pieza, con las candidatas sin
  verificar en una sección aparte.

## Ángulos (cuando se piden)
Taxonomía de 15 a 25 ángulos con su motor psicológico y ganchos de ejemplo reescritos (no copiados), marcados como
**saturados** o **calientes**, y **ganadores** (probados por datos) contra **de descubrimiento** (huecos sin probar).
Recomendación típica: prender un ganador y uno de descubrimiento por semana. Si la persona ya tiene una matriz de
ángulos o un calendario acomodado, no se toca: las propuestas van debajo de lo que ya hay.

## Carruseles de referencia con sus láminas
Ver `carruseles-referencia.md`: tabla de elegidos y una ficha por carrusel (lámina por lámina), con método y límites.

## 2. Auditoría de cuenta
Top por comentarios, top por vistas y top por ratio vistas entre comentarios; reels y carruseles en secciones
separadas, con el anexo de solo carruseles en el mismo archivo. Di cuántos reels salieron solo en `/reels/`. Si piden
juntar varias auditorías, un documento unificado con tres vistas (ranking maestro, solo carruseles, solo reels)
generado con un script, no transcrito a mano (`scripts/virales/auditoria.py`).

## 3. Recursos de la competencia
Por publicación: palabra clave, recurso, tema y fuente del título (caption, lámina o audio) con la frase textual.
Ranking de palabras clave, catálogo de recursos (varias palabras clave pueden llevar al mismo recurso), «descripción
aproximada» cuando no hay título y una lista de verificación final. Si se proponen recursos propios, con palabra clave
sugerida que nadie más use (verificado).

## 4. ADN de marca de competidores
Censo por tasa de interacción. Ficha por perfil: posicionamiento, personaje y arquetipo, tono y muletillas, ganchos,
paleta en hex sacada por programa de portadas y destacadas, tipografía aproximada, escenario, temas, embudo,
monetización, porcentaje de canje. Mapa de posicionamiento con el cuadrante vacío, temas saturados contra libres, y
una hoja HTML con las paletas lado a lado (la de la persona al final, si la da) y los choques medidos
(`scripts/adn/paleta.py` y `scripts/adn/hoja_paletas.py`).

## 5. Voz del cliente
Qué quiere, problemas en sus palabras, dudas textuales, qué consume, vocabulario exacto (las palabras que usa y las
que no usa), qué pide más, y cruce con los ángulos existentes: duda real contra ángulo que nadie pide.

## 6. Anuncios
Ver `biblioteca-anuncios.md`, sección de ficha.

## 7. Embudos, 8. Guiones y 9. Negocios locales
Ver `embudos-y-guiones.md`.

## Cierre en el chat (todos los modos)
Ruta del documento y de los datos crudos, cuántas piezas calificaron de cuántas revisadas y por qué, 3 a 5 hallazgos,
qué es dato y qué es supuesto, qué no se pudo ver. No vuelques tablas enteras en el mensaje. Al final abre el documento
(en macOS `open -R <ruta>` lo muestra en Finder; o en el editor que la persona tenga abierto), salvo que esté
editando video: entonces solo da la ruta.
