# Prompts de imagen para que la persona genere los slides

Cuando la persona genera las imágenes en un generador (ChatGPT u otro) y quiere copiar y pegar sin pensar,
o cuando el carrusel necesita imágenes de contexto que no se hacen con HTML (una persona en su trabajo, una
escena, un objeto, un estilo de ilustración). El entregable es `PROMPTS.md` en la carpeta del carrusel.

## Reglas del entregable
1. **Un prompt por slide, autónomo:** el estilo completo va dentro de cada prompt. Nada de «paso 0 de
   estilo» que haya que pegar antes: cada prompt funciona solo.
2. **Arriba de cada prompt, qué adjuntar y en qué orden** («Adjunta en este orden: 1. tu foto, 2. la
   captura del perfil»). Dentro del prompt, cada adjunto se nombra por su número (Imagen 1, Imagen 2).
3. **Proporción, nunca píxeles:** escribe «formato vertical 4:5» en portadas y slides (1:1 para stickers
   o íconos sueltos). No pongas medidas en píxeles: en la app no fijan el tamaño y solo confunden.
4. **Cierre fijo** de cada prompt: «Genera la imagen exactamente como está descrito, sin reinterpretar ni
   añadir elementos.» En slides con texto: «Todo el texto completo, legible, correctamente escrito, con
   todas las tildes y los signos de apertura.»
5. **Capturas de la persona:** explica exactamente cómo sacarla (qué app, qué pantalla, hasta dónde bajar,
   qué debe verse y con qué nombre guardarla). Las capturas van en `mis-capturas/` del carrusel.
6. **Fotos e imágenes de contexto: el prompt va en inglés y termina con «No text in the image.»** El
   generador hace la foto; el texto exacto lo pone el HTML encima. Avísale a la persona que los
   generadores deforman letras en slides con mucho texto: las listas largas (10 renglones) o los prompts
   largos se arman en código copiando el estilo, y se le dice por qué.
7. **Letra a mano:** nunca una fuente que imite plumón. Se edita una foto real de la libreta de la persona
   («Edita la última imagen adjunta, que es una foto real de mi libreta: úsala como base y conserva
   exactamente el papel, los renglones, la espiral, la mano, la luz y el fondo; no la redibujes ni la
   conviertas en ilustración, y deja el resultado en formato vertical 4:5 (recorta un poco si hace falta).
   Sobre la hoja escribe y dibuja a mano con plumón de punta media, como si yo lo hubiera escrito con una
   pluma real: trazo con variaciones de presión, ligeras imperfecciones, siguiendo la perspectiva y los
   renglones de la hoja, con la tinta un poco absorbida por el papel.»). La tinta, en los colores de su
   marca. La foto de la libreta va **siempre al final** de los adjuntos y es la misma en todo el carrusel.
8. **Carruseles de libreta, 100 % orgánicos:** sin la foto de perfil de la persona, ni dibujada ni pegada.
   El @ solo donde la referencia lo traía, escrito a mano y chiquito o como marca de agua gris, sin foto ni
   insignia.
9. Paleta y fuentes de la marca de la persona dentro de cada prompt, aunque la referencia use otras.
10. Si piden repetir un carrusel ya hecho, copia los prompts tal cual y cambia solo lo que pidieron.

## Si quien genera es un agente que lee archivos (por ejemplo Codex)
Además del `PROMPTS.md`, deja en la misma carpeta un `CODEX.md` listo para pegarle, con:
- la ruta absoluta al `PROMPTS.md`;
- las rutas absolutas de cada imagen a adjuntar, en el orden de «Adjunta»;
- la carpeta de salida (una nueva, que no pise otras versiones);
- la regla de no inventar capturas que falten (si falta una, que lo diga);
- la lista de revisión final: @ correcto, texto exacto, capturas fieles, estilo igual en todas.

## Plantilla de un prompt de slide con texto

```
Slide 3 de 8. Adjunta en este orden: 1. captura-perfil.png

Formato vertical 4:5. Fondo [color de la marca en palabras y hex]. [Descripción completa del estilo:
tipografía, tamaño relativo, alineación, márgenes, acento]. Arriba, el título: "[texto exacto]". Debajo,
la Imagen 1 dentro de una tarjeta blanca con sombra suave, centrada.

Todo el texto completo, legible, correctamente escrito, con todas las tildes y los signos de apertura.
Genera la imagen exactamente como está descrito, sin reinterpretar ni añadir elementos.
```

## Plantilla de un prompt de imagen de contexto

```
Slide 1 de 8. Adjunta en este orden: (nada)

Vertical 4:5 format. Realistic photo of [la escena u objeto del concepto de imagen: qué es, qué pasa,
encuadre, ángulo, luz, colores dominantes, distinto a la referencia]. Leave the lower third clean for a
headline. No text in the image.
Generate the image exactly as described, without reinterpreting or adding elements.
```

Si la imagen lleva a la persona, se usa una foto real suya (la que pasó o una reciente que autorice); el
generador no inventa su cara.
