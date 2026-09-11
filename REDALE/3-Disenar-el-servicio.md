# D — Diseñar el servicio

## Qué arquitectura elegimos

**Services pequeños en cadena, cada uno con una sola responsabilidad, más una cola para los picos y avisos de cambio para que nadie use estado viejo.** Es lo que vimos en clase con el caso de Leasing (Login Service → Validation Service → …), aplicado alrededor del LLM.

- Camino de una pregunta: Genius App → Login Service → Filtro Service → Consulta Service → (si no hay respuesta guardada) Contexto Service → Cola de Preguntas → LLM local → Revisión Service → respuesta.
- Camino de una acción: Revisión Service → Acciones Service → lectura (Copia de lectura, Pruebas Service) / escritura (Aprobación Service → otro SRE) / borrar (bloqueado) → Auditoría.
- Camino de un cambio de incidente: Incidentes Service → Cola de Cambios → Estado Actual, SLA Service, Auditoría, Cache de Respuestas.

| Otra opción | Por qué no |
|---|---|
| Un solo programa grande (lo de hoy, con más código) | Sigue siendo un solo punto de falla; sin cola, el pico del mes lo tumba; sin avisos de cambio, vuelve el estado viejo |
| Microservicios con todo separado | 100 usuarios y menos de 10 pedidos por segundo no lo justifican; cuesta más operarlo de lo que aporta. Solo separamos lo que es de riesgo alto (Acciones, Aprobación, LLM, Incidentes) |
| Todo por eventos | Las preguntas necesitan respuesta en el momento (< 5 s); los avisos solo los usamos para los cambios de incidente y los plazos |

## Dónde se guarda cada cosa

| Dato | Dónde | Por qué |
|---|---|---|
| Incidentes, escalamientos, aprobaciones, usuarios y roles | BD SQL principal + réplica síncrona (RPO 0) | Es la fuente de verdad y necesita transacciones |
| Auditoría | Tabla donde solo se agrega (sin UPDATE ni DELETE), copia mensual a almacenamiento de archivos | Nadie la puede cambiar; se guarda 1 año |
| Estado Actual y Cache de Respuestas | Memoria rápida (caché) que se actualiza con los avisos de la Cola de Cambios | Responder en menos de 1 segundo y siempre igual |
| Historial por incidente | BD SQL | Sobrevive a reinicios del LLM |
| Base de Conocimiento | Documentos con versión + índice de búsqueda por significado | Citar fuente y fecha en cada respuesta |
| Cola de Preguntas y Cola de Cambios | Cola durable (el mensaje no se pierde si una pieza está caída) | Aguantar picos y no perder avisos |
| Logs de pruebas E2E | Almacenamiento de archivos | Son grandes y baratos ahí |

## API de Genius (REST)

| Método | Endpoint | Para qué | Códigos |
|---|---|---|---|
| POST | `/ask` | Pregunta en lenguaje natural; `incident_id` opcional | 200 · 202 (en cola, devuelve posición) · 400 (rechazada por el filtro) · 503 (respuesta sin LLM, trae el estado) |
| GET | `/incidents/{id}` | Estado actual con `updated_at` y fuente | 200 · 404 |
| POST | `/incidents/{id}/escalate` | Escalar a ingeniería con contexto | 201 |
| POST | `/actions` | Pide ejecutar una acción (`action`, `params`) | 202 (espera aprobación) · 200 (lectura ejecutada) · 403 (fuera de su rol o prohibida) |
| POST | `/actions/{id}/approve` | Aprueba una escritura (otro SRE) | 200 · 403 · 410 (expiró) |
| POST | `/feedback` | Marca la respuesta correcta o incorrecta + corrección | 201 |
| GET | `/audit?incident_id=` | Quién pidió, quién aprobó, qué se ejecutó | 200 |
| GET | `/checks/latest` | % de aciertos de las pruebas diarias | 200 |
| GET | `/health` | Estado de cada pieza y de los circuit breakers | 200 · 503 |

Reglas de clase: endpoints con sustantivos, tipos y límites documentados (`params` se valida contra lo que pide cada acción), todos los códigos listados, playground en `/docs`.

## Alcance

- Sí: preguntas, acciones controladas, estado siempre actual, aguantar picos y caídas del LLM o de Slack, auditoría, pruebas diarias.
- No (por ahora): entrenar o afinar el modelo, varias regiones, arreglar incidentes solos sin una persona.
