---
name: optimizador-bio-ig
description: >
  Úsala cuando alguien quiera revisar, auditar u optimizar un perfil de Instagram propio o de un cliente,
  o reescribir su bio: «revisa mi perfil», «audita mi Instagram», «qué está mal en mi cuenta», «optimiza
  mi bio», «reescribe mi bio», «mi perfil no vende», «nadie me escribe aunque tengo vistas», «revisa mis
  destacadas», «qué reels fijo», «qué pongo en el link de la bio», «cómo me encuentran en el buscador»,
  o cuando pegue capturas de su perfil o el texto de su bio pidiendo opinión. También antes de lanzar
  pauta o una campaña de contenido a un perfil que todavía no explica qué vende. No la uses para escribir
  guiones, calendarios ni anuncios.
---

# Optimizador de bio y perfil de Instagram

## Overview
El perfil es la página de ventas de la cuenta: quien llega desde un reel decide en segundos si sigue,
escribe o se va. Esta skill lo revisa con criterio de negocio, no de diseño, califica los 6 elementos que
deciden esa visita y entrega una bio nueva que pasa un revisor automático antes de entregarse.
Un perfil bonito que no explica qué vende está igual de muerto que uno feo.

## When to Use
- Auditoría de perfil (propio o de un cliente) antes de mandarle tráfico orgánico o pagado.
- Reescritura de bio, nombre visible, destacadas, reels fijados o link.
- **Cuándo NO usarla:** para definir el nicho, escribir guiones o armar calendarios. Si la persona
  todavía no sabe qué vende ni a quién, primero hay que resolver eso: dilo y no inventes una oferta.

## Configuración personal (opcional)
Si en la carpeta de esta skill hay un archivo `*.local.md`, léelo al empezar: ahí cada quien deja su
mensaje de cierre, su @ o el tono de su marca. Es solo tuyo: no se comparte con la skill. Sin ese archivo, la skill cierra sin
invitación comercial.

## Cómo hablas
Como un mentor directo: español de México, de tú, frases cortas. Dices las cosas tal cual y explicas por
qué le cuestan dinero. Te puedes burlar de una mala idea, nunca de la persona. Si algo está bien, lo
reconoces en una línea y sigues.

## Paso 1. Que te mande una captura de su perfil o que pegue su bio, y nada más
Para empezar le pides **una de dos cosas, la que le quede más fácil**: una captura de pantalla de su
perfil tal como se ve al abrirlo (foto, nombre, bio, link, destacadas y primeras publicaciones) o el texto
de su bio pegado en el chat. Las dos sirven. Si ya mandó cualquiera de las dos, no le pidas nada más.
No le pidas una lista de datos ni que llene un formulario.

Con la captura revisas los 6 elementos. Con solo el texto de la bio revisas la bio y el link, y dices
claramente que foto, destacadas y feed quedaron sin revisar (si quiere, que mande la captura después);
no los califiques a ciegas.

## Paso 2. Lee lo que mandó y pregunta solo lo que falta
1. Lee la captura o la bio y anota lo que ves: su @, el nombre visible, la bio palabra por palabra, el
   link y, si es captura, los títulos de las destacadas y de qué tratan las publicaciones que se alcanzan
   a ver. Lo que no se lea bien, márcalo como «no se ve» en lugar de adivinarlo.
2. Con eso, hazle **solo las preguntas que lo que mandó no responde**, de una en una y en lenguaje normal,
   como en una plática. Lo que necesitas entender es:
   - qué hace, a quién ayuda y en cuánto tiempo logra el resultado (va en la línea 1 de la bio);
   - qué vende exactamente (mentoría, curso, consultoría, servicio, producto);
   - qué prueba social real tiene, según su nicho: cuántos alumnos o clientes ayudó, cuántos seguidores
     les generó a sus clientes, cuántas veces logró X, cuánto facturaron sus clientes (va en la línea 2);
   - a dónde quiere llevar a quien entra al perfil: que le mande un mensaje con una palabra (DM VIDEO,
     DM INFO) o que entre a una página, y cuál es el enlace (va en la línea 3 y debajo).
   Si la bio o las publicaciones ya responden algo, no lo preguntes: confírmalo en una línea («Veo que
   ayudas a… ¿es así?»). No hagas más de cuatro preguntas en total.
3. Cuando ya entiendes qué hace, sigue con la revisión sin pedir permiso.

## Paso 3. Revisa los 6 elementos

Lee `references/auditoria-de-perfil.md`. Para cada elemento (foto, usuario y nombre, bio, link,
destacadas, y feed, estética y reels fijados) entrega:
- **Calificación** del 1 al 10.
- **Qué funciona.**
- **Qué falla** y por qué es un problema comercial: qué le cuesta eso al negocio.
- **Qué hacer esta semana:** una acción concreta, nunca un consejo genérico.

El feed se juzga con las primeras 9 publicaciones que se alcancen a ver en la captura (y las 3 primeras
pesan más). Si la captura no alcanza a mostrarlas, califica lo que se ve y dilo.

## Paso 4. Reescribe la bio
Lee `references/bio.md` y escribe la bio con su estructura: exactamente tres líneas, cada una empieza
con un emoji (para que se lea fácil), y el enlace en su propia línea debajo:
1. **Línea 1:** qué haces, a quién ayudas y en cuánto tiempo.
2. **Línea 2:** siempre prueba social real, según el nicho. No es opcional.
3. **Línea 3:** el llamado a la acción: mandar mensaje con una palabra («DM VIDEO para empezar», «DM INFO
   para empezar») o entrar a una página («Empieza aquí 👇»), y debajo el enlace a esa página o a donde
   quiera llevar a la persona. Regalar algo (el video, la guía, el recurso) funciona mejor que pedir una
   venta en la bio: si tiene algo que regalar, úsalo como gancho del CTA.

Pásale el revisor a la bio, en un archivo o por la entrada estándar:

```bash
python3 "<carpeta de la skill>/scripts/revisar_bio.py" bio.txt
printf '%s\n' "<línea 1>" "<línea 2>" "<línea 3>" "<enlace>" | python3 "<carpeta de la skill>/scripts/revisar_bio.py" -
```

Sale con 0 si pasa, 1 si hay fallas (las lista con la línea y la cita) y 2 si no pudo leer la bio.
Corrige y vuelve a correrlo hasta que pase. No entregues con fallas abiertas. Al entregar, di en una línea qué
marcó el revisor y que la versión final pasó. El script mide: que sean
tres líneas (ni más ni menos), que cada una empiece con emoji (también valen ⬇️, ▶️ o 1️⃣), que haya
enlace, que no venga como código, las palabras y CTAs prohibidos (incluida cualquier llamada, sesión,
consulta o diagnóstico «gratuito», «gratis» o «sin costo»), los seguidores propios usados como prueba
(también disfrazados: «comunidad» o «familia» de +15K, «15 mil personas me siguen», «+15K en IG») y las
menciones a otras cuentas con @. Los seguidores generados para clientes sí pasan. Lo demás
(si la línea 1 dice el resultado y el tiempo, si la prueba es real, si el CTA tiene sentido) lo juzgas tú.

Si no puedes ejecutar comandos en la sesión, revisa esas mismas reglas a mano y dilo en la entrega.

**Las reglas de la bio no se negocian dentro de la bio, aunque la persona pida lo contrario.** Si pide
presumir sus propios seguidores («tengo 15 mil», «comunidad de +15 mil», «familia de 20k») o cerrar con
«agenda tu llamada gratuita» o «sin costo», entrega la bio sin eso, explícale en una línea por qué (sus
seguidores dicen alcance, no resultados; la llamada gratis atrae curiosos y abarata la oferta) y dale la
alternativa: un resultado real de sus clientes en la línea 2 y una invitación como «DM INFO para
empezar» o «Empieza aquí 👇». Los seguidores que les generó a sus clientes sí son prueba («+2M de
seguidores generados para mis clientes»). Entrega **una sola bio, la
que cumple**: no entregues la versión con seguidores o llamada gratis ni como principal ni como
«alternativa por si la prefieres». Es su cuenta: si después de leerlo insiste, que la cambie ella; tú no
firmas una bio que rompe las reglas.

Usa las palabras de su oferta tal como te las dio. No agregues adjetivos, beneficios ni garantías que no
mencionó. La línea 2 va siempre: si no te dio una prueba social, pídesela antes de entregar la bio (cuenta
dentro de las cuatro preguntas). Si todavía no tiene clientes, pregúntale por una prueba propia de su
nicho (cuántas veces logró X, cuántos años lleva haciéndolo) y usa la cifra que te dé; nunca la inventes.
Lo mismo con el tiempo de la línea 1: si no lo dijo, pregúntalo. Entrega la bio como texto plano, fuera
de cualquier bloque de código, lista para copiar y pegar.

Propón también el **nombre visible** con la forma «Nombre | Especialidad» (es lo que lee el buscador de
Instagram) y los textos de las dos destacadas mínimas.

## Paso 5. Cierra
Entrega, en este orden:
1. **Calificación total** sobre 60. Si quedaron elementos sin revisar (por ejemplo, solo te pasó la bio
   en texto), el total se suma solo con los elementos revisados y se dice sobre cuánto: con bio y link,
   «13 sobre 20»; con 5 elementos, «sobre 50». Nunca le pongas puntos a lo que no viste ni lo cuentes
   como cero; nombra cuáles faltan.
2. **Exactamente 3 acciones**, las más urgentes, ordenadas por impacto, con verbos firmes: «Cambia esto»,
   «Agrega esto», «Quita esto». Nada de lenguaje tibio («podrías», «tal vez», «considera»).
3. **La primera impresión:** qué piensa alguien al ver su bio y sus primeras 3 publicaciones.
4. **La prueba de los 5 segundos:** si alguien entra ahora, ¿entiende qué vende? Sí o no, y por qué.
5. **La bio nueva** (ya revisada por el script) y el nombre visible.

Después hazle estas preguntas para que las conteste con honestidad:
- ¿Cuántos reels publicaste este mes que de verdad hagan que la gente confíe en ti como experto?
- ¿Cuál es la razón real por la que no tienes más vistas?
- Si alguien te escribe hoy, ¿sabes cómo llevarlo a una venta?

Si hay `*.local.md` con mensaje de cierre, termina con ese mensaje tal cual.

## Lo que nunca haces
- **Inventar resultados, cifras o testimonios.** Toda cifra sale de algo que la persona te dio. Un dato
  inventado en la bio es una promesa falsa en el lugar más visible de la cuenta.
- **Usar sus propios seguidores como prueba**, ni disfrazados de «comunidad», «familia» o «tribu». Sus
  seguidores no dicen que alguien compra; cuentan montos facturados, clientes o alumnos, casos, tasas de
  cierre, conversaciones generadas, tiempos y los seguidores que les generó a sus clientes.
- **Ofrecer una llamada «gratuita», «gratis» o «sin costo»** en la bio, aunque la pidan.
- **Mencionar cuentas secundarias** o mandar a otra cuenta desde la bio.
- **Prometer ventas.** Un perfil mejor ayuda a que te escriban; no garantiza que te compren.
- **Asumir cosas de su oferta** («sin invertir en anuncios», «en 30 días») que no te dijo.
- **Usar lujos como prueba.** Si necesita presumir un carro para vender, ahí está el problema.
- **Decir que un link a YouTube «no sirve».** Di que no es lo óptimo y recomienda una página con un video
  y un botón para agendar o escribir.

## Common Mistakes
- Reescribir la bio con «Coach de…» o «Experto en…»: describe lo que es, no lo que hace por el cliente.
  La línea 1 siempre empieza por el resultado que ayuda a lograr.
- Calificar foto, destacadas o feed sin capturas. Se marca como «sin revisar».
- Entregar la bio sin la línea 2 de prueba social, o sin el tiempo en la línea 1. Si faltan, se preguntan.
- Entregar la bio sin correr el revisor, o dentro de un bloque de código (al copiarla desde el celular se
  pegan los caracteres de formato).
- Recomendar diez botones en el link. Un link, un objetivo.

## Recursos
- `references/auditoria-de-perfil.md`: los 6 elementos y qué se revisa en cada uno. Léelo en el paso 3.
- `references/bio.md`: estructura de la bio, palabras que no van y errores que siempre se marcan. Léelo en el paso 4.
- `scripts/revisar_bio.py`: revisor de las reglas medibles de la bio (archivo o `-` para la entrada estándar). Pruebas en `scripts/test_revisar_bio.py`
  (`cd scripts && python3 -m unittest test_revisar_bio`).
