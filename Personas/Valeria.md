# Valeria Torres — SRE on-call

## Perfil

- **Edad:** 33 años
- **Rol:** Site Reliability Engineer. Hace guardia una semana al mes; atiende engineering escalations y los P1 de clientes.
- **Contexto:** Durante un incidente necesita ejecutar queries y E2E tests desde Genius sin salir de Slack. En la primera semana del mes atiende varios incidentes a la vez.
- **Nivel tecnológico:** Alto. Desconfía de respuestas sin fuente.

## Necesidades

- **N1:** Ejecutar queries de solo lectura y E2E tests desde Genius en segundos durante un incidente, con resultado confiable.
- **N2:** Que toda acción de escritura muestre exactamente qué va a ejecutar y pida su aprobación explícita antes de hacerlo.
- **N3:** Que Genius recuerde lo que ya se hizo en el incidente (queries, tests, hipótesis) durante toda su vida.
- **N4:** Respuestas con fuente (runbook, postmortem, incidente similar) y fecha, para decidir rápido.

## Pain Points

- **P1:** "En el pico del mes Genius se queda colgado 40 segundos y luego dice timeout; termino haciendo las queries a mano."
- **P2:** "Me sugirió un fix de un postmortem de hace dos años que ya no aplica; nunca cita de dónde saca las cosas."
- **P3:** "Cada vez que reabro el hilo tengo que volver a explicarle todo el incidente."
- **P4:** "El LLM usa la misma credencial de admin de la BD para todos; después del borrado nadie sabe qué más puede hacer."
- **P5:** "Cuando Genius se cae no hay forma de ver ni el estado básico del incidente desde el bot."

*Para Valeria, Genius funciona si a las 3 a. m. le pide una query y en menos de diez segundos tiene el resultado con la fuente, y si un `UPDATE` jamás corre sin que ella lo apruebe viendo el comando exacto.*
