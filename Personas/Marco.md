# Marco Salas — Incident manager

## Perfil

- **Edad:** 41 años
- **Rol:** Responsable de los customer escalations y del cumplimiento de SLA (1 día customer, 3 días engineering). Reporta impacto al negocio.
- **Contexto:** Habla con clientes y gerencia; no ejecuta queries. Necesita un solo estado por incidente y evidencia de lo que hizo el LLM.
- **Nivel tecnológico:** Medio-bajo.

## Necesidades

- **N1:** Ver el SLA restante de cada escalamiento y recibir alerta antes de que venza.
- **N2:** Un solo estado consistente por incidente para comunicar al cliente, sin importar quién pregunte ni cuándo.
- **N3:** Trazabilidad: quién pidió, quién aprobó y qué ejecutó Genius en cada incidente.
- **N4:** Saber si Genius está sano hoy (disponibilidad, errores, latencia, % de respuestas correctas) para decidir si confiar en él.

## Pain Points

- **P1:** "Le dije al cliente que su incidente estaba abierto y ya estaba cerrado; perdimos credibilidad."
- **P2:** "Después del borrado de la BD nadie pudo decir quién dio la orden ni qué ejecutó exactamente el LLM."
- **P3:** "Se me vencen SLAs de un día en la primera semana del mes y me entero por el cliente."
- **P4:** "Dos ingenieros le preguntan lo mismo a Genius y le dan respuestas distintas al mismo cliente."
- **P5:** "No tengo ningún indicador de si Genius está funcionando bien hoy o no."

*Para Marco, Genius funciona si antes de escribirle al cliente ve un solo estado con hora de última actualización, y si cualquier acción del LLM tiene nombre, hora y aprobador.*
