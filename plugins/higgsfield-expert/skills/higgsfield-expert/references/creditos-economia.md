# Higgsfield — Créditos y disciplina de costo

> Precios, créditos por plan y costo por modelo cambian cada semana (promociones, modelos nuevos). Sácalos siempre del MCP: `show_plans_and_credits`, `balance`, `estimate_*_cost`, `transactions`.

## Antes de cualquier generación
1. `balance` → cuánto hay.
2. Cotiza exactamente lo que vas a mandar con `estimate_image_cost` / `estimate_video_cost` / `estimate_audio_cost`. No genera nada.
3. Dile al usuario: modelo, duración/resolución, número de tomas y **total en créditos**. Espera el sí.
4. Genera **exactamente** lo cotizado (la cotización devuelve una referencia para no reescribir los parámetros).
5. Después, `transactions` para confirmar lo que se cobró.

## Ilimitados: la trampa más común
- Los modelos "ilimitados" o "free gens" de los planes **se usan en la web**. Por el MCP se cobran créditos aunque el modelo sea ilimitado en la web.
- Excepción: si la cuenta tiene generaciones ilimitadas de prueba, el MCP no genera y devuelve una pregunta (`unlim_choice`). Pásale la pregunta al usuario tal cual; nunca elijas por él.
- Si el usuario quiere aprovechar sus ilimitados del plan, dile que lo haga en la web y usa esta skill para el prompt.

## Cómo no quemar créditos
- **Still primero:** perfecciona la imagen (barata) y solo entonces anímala (el video cuesta muchas veces más). Una imagen rechazada es barata; un video rechazado, caro.
- **Una prueba antes del lote:** primera tirada de un modelo o de un prompt nuevo = 1 generación.
- **Clips cortos:** 4 a 8 s y ensambla; un clip largo falla más y cuesta más.
- **Borradores:** si el modelo ofrece modo borrador o resolución baja, úsalo para aprobar y luego finaliza.
- **No reintentes a ciegas:** si un trabajo tarda, espera y consulta su estado. Reenviar cobra otra vez.
- **Sin audio si no lo usas:** algunos modelos de video generan sonido y cuesta más; apágalo si vas a poner tu voz.

## Planes y compras
- `show_plans_and_credits` muestra los planes vigentes con su liga de pago. No compres, no actives recargas automáticas ni pruebas con tarjeta por el usuario: dale la liga y que decida.
- Revisa con el usuario si su plan es mensual o anual antes de recomendar subir de plan. Los créditos de recarga caducan (el widget dice cuándo).
