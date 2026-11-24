# Criterios de viralidad y métricas

Todo lo numérico de aquí está en código: `scripts/virales/seleccion.py` (con pruebas). Úsalo en vez de calcular a mano.

## Reels

| Caso | Regla | Función |
|---|---|---|
| Cuenta con menos de 50 mil seguidores | Vistas >= 10 veces sus seguidores | `es_viral()` |
| Cuenta con 50 mil seguidores o más | Más de 1,000,000 de vistas | `es_viral()` |
| Nivel S | Las dos a la vez: más de 1M y >= 10x. Se toman sin dudar. | `nivel()` |
| Nivel A | Más de 1M sin importar el tamaño de la cuenta. | `nivel()` |
| Nivel B | >= 10x sin llegar al millón. Solo si no se llena la cuota con S y A: `elegir_por_cuota()` pone S y A primero y marca el B que entra como relleno. | `nivel()` |
| Nivel 2 (rescate) | Umbral a la mitad (5x en cuentas chicas, más de 500 mil en grandes), **etiquetado como Nivel 2** y solo si no se llega a la cifra. | `es_viral_nivel_2()` |

El umbral es exacto: un 9.97x no es 10x. Nunca se baja un umbral en silencio; lo que entra por rescate lleva su
etiqueta en la tabla. Si la cuota no se llena, se entrega lo que hay y se dice cuántas búsquedas y cuántas cuentas se
revisaron (la skill base de investigación viral pide haber hecho 10 o más búsquedas y revisado 20 o más cuentas
antes de entregar menos de lo pedido).

Las vistas salen del payload de `/reels/` (`play_count`, que coincide con el contador de la miniatura); si no llegaron,
del contador visible convertido (`vistas_de()`). Las cuentas chicas con ratio alto son los hallazgos más valiosos:
prueban que el tema, no el creador, genera el alcance.

## Carruseles

Los carruseles no muestran vistas (una extensión que diga «Vistas: 0» da un dato falso). Tres maneras, según el encargo:

1. **Por likes, con equivalencia medida** (virales por nicho). Se calcula la mediana de vistas por like de los reels de
   la misma investigación (misma ventana, mismas cuentas o mismo nicho) y se multiplica:
   `alcance estimado = likes x mediana`. Luego se aplica la regla de reels. Se muestra la cifra exacta que se usó
   (por ejemplo «mediana 40.5 vistas por like, 214 reels»). Valores medidos en nichos de marketing, marca personal e
   IA: entre 40 y 52; mídela siempre, no la copies. `mediana_vistas_por_like()` y `carrusel_es_viral()`.
2. **Por comentarios, en cascada** (cuando el encargo es «los más comentados»): primero los de más de 1,000
   comentarios, luego más de 700, 500, 300 y 100, hasta juntar la cantidad pedida o, si no hay cantidad, el máximo
   posible. Se reporta en qué escalón entró cada uno. `cascada_comentarios()`.
3. **Carruseles de cuentas concretas** (censos y auditorías): likes y comentarios, las dos columnas.

## Parámetros de una investigación viral

Los parámetros confirmados se recitan antes de cada corrida y se pregunta solo lo que cambie (guárdalos en `*.local.md`).
Los que se usan por omisión:

- Plataforma: solo Instagram.
- Idiomas y cuota: inglés, luego portugués, luego español, 25/15/10 de 50. El orden ha cambiado entre encargos (una
  serie de corridas fue con español primero): **pregunta si no lo dicen**.
- Ventana: últimos 3 meses (para noticias, unos pocos días).
- Máximo 3 piezas por cuenta (`tope_por_cuenta()`).
- Excluir: lujo como estilo de vida, humor y memes del nicho, contenido dirigido a la audiencia que el encargo
  excluye (por ejemplo, si el avatar son hombres, lo dirigido a mujeres) y lo que no sea del nicho. Los recortes de
  pódcast de personas conocidas sí cuentan.
- Likes mínimos en la búsqueda para escanear una cuenta: 1,000.
- Si una cuenta sube el mismo video varias veces (con vistas distintas), se cuenta una vez.
- Las cuentas oficiales de las marcas que se buscan (por ejemplo la cuenta de una app cuando buscas esa app) se
  excluyen y se reportan aparte.

Cuando la cuota de un idioma no se llena, `elegir_por_cuota()` completa con el primer idioma de la lista y con ningún
otro: dilo en el documento («faltaron 4 en español; se completaron con inglés»).

## Competidores

Se ordenan por **tasa de interacción**, no por seguidores (cuentas grandes apagadas contra chicas calientes). Se marcan
las cuentas que ocultan likes.

## Comentarios: canje contra conversación

El «comenta X y te mando» infla los comentarios sin medir comunidad. Se separa siempre el lead magnet de la
conversación real y se clasifica **leyendo los comentarios, no solo el caption**: en una corrida de referencia, el 30%
de las piezas que no pedían palabra en el caption la pedían dentro del video o en la última lámina. Comentarios altos
con likes bajos suelen ser canje; para saber qué gusta, pesan más los likes; para saber qué duele, se leen los
comentarios que no son canje. `scripts/virales/comentarios.py` muestra la palabra más repetida y su proporción para
ayudar a leer. Comentarios en 0 cuando el creador los pide: probablemente ocultos o desactivados (`minfo.mjs` trae
`comments_disabled`).

## Motores de viralidad (para la tabla de temas)

Cada tema repetido lleva su motor: **validación** («por fin alguien lo dijo»), **revelación** («no sabía que esto era
la causa»), **miedo o urgencia** («esto te puede pasar»), **controversia** («el debate que todos tienen»),
**empoderamiento** («esto es exactamente lo que hay que hacer») o **identidad** («esto soy yo»).

## Fechas y seguidores

- Los seguidores que se leen son los de hoy, no los del día en que se publicó: avísalo en piezas viejas.
- La fecha que se calcula desde el id (`fecha_de_pk()`) es la de subida y puede adelantarse días a la publicación:
  confirma con `taken_at` (`fecha_de_publicacion()` ya lo prefiere). Trabaja en UTC.

## Formato de entrada de `seleccion.py`

Funciones puras, sin red ni archivos. Esperan un escaneo por cuenta como el que escribe `ig/batchscan.mjs`:

```json
{"handle": "cuenta", "followers": 12000,
 "items": [{"code": "ABC123", "pk": "<id numérico de la publicación>", "type": "clips",
            "play_count": 150000, "vistas_visibles": 150000, "like_count": 3200, "comment_count": 140,
            "taken_at": "<segundos unix>", "caption": "...", "thumb": "url"}]}
```

`type` es `clips` para reels y `carousel_container` para carruseles (estos llevan `slides` y no `play_count`). Para
cuotas por idioma, cada pieza necesita un campo `idioma` que pone la clasificación.
