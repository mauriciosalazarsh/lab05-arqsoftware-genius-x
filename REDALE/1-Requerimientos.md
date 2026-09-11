# R — Requerimientos

## ¿Tenemos claro el problema?

Genius (LLM local + MCP a BD y Slack) falla en cinco frentes: ejecutó un borrado de BD por una instrucción de soporte; responde con data vieja y no aprende; en la primera semana del mes no responde o responde mal; responde distinto a la misma pregunta; reporta como abierto un incidente cerrado. La causa común: **no hay harness**. El LLM habla directo con la BD y Slack sin permisos, cola, caché, conocimiento actualizado, fallback ni auditoría.

## ¿Para quién?

| Persona | Rol | Necesidad en una frase |
|---|---|---|
| [Diego](../Personas/Diego.md) | Soporte N2 | Estado real en segundos, misma respuesta para la misma pregunta, no poder romper nada |
| [Valeria](../Personas/Valeria.md) | SRE on-call | Queries y tests rápidos, escrituras solo con su aprobación, memoria del incidente, fuentes |
| [Marco](../Personas/Marco.md) | Incident manager | SLA visible, un solo estado por incidente, trazabilidad, salud de Genius |

Stakeholders: data science (dueña del LLM), la compañía y sus clientes (SLA 1 día / 3 días, datos dentro de la red).

## ¿Limitaciones?

- LLM **local** (los incidentes no pueden ser públicos): no se puede delegar capacidad a un proveedor externo; la capacidad la fijan las GPUs propias.
- Picos de 3× en la primera semana del mes con el mismo hardware.
- SLA de negocio: 1 día customer, 3 días engineering.
- El LLM debe poder **tomar acciones** (queries, E2E tests): no basta con quitarle permisos, hay que controlarlos.
- Disponibilidad y tolerancia a fallos son exigidas; latencia mínima para decisiones críticas.

## Salida

- [Requirements/ReqFunc.md](../Requirements/ReqFunc.md) — RF01–RF24
- [Requirements/ReqNoFunc.md](../Requirements/ReqNoFunc.md) — RNF01–RNF13
