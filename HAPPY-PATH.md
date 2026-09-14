# Happy paths

El happy path es el camino más común y sin errores por el diagrama. Tomamos uno por persona y lo seguimos flecha por flecha para comprobar que la arquitectura de verdad lo cumple. Cada uno tiene su copia del diagrama con el camino resaltado y los pasos numerados en `Diagramas/`.

## Happy path 1 – Soporte responde al cliente y escala (Diego)

Diagrama: [harness-hp1.pdf](Diagramas/harness-hp1.pdf)

1. Diego escribe en Genius App: "¿en qué está el INC-4471 y qué hago?".
2. Login Service ve que es soporte. Filtro Service revisa que la pregunta esté limpia.
3. Consulta Service busca en Cache de Respuestas. Como es un incidente puntual, no existe.
4. Contexto Service junta el Estado Actual del incidente, los pasos a seguir para customer escalations y el historial de ese incidente.
5. La pregunta entra a la Cola de Preguntas. Como es customer escalation va segunda en prioridad. LLM local #1 responde en menos de 5 segundos.
6. Revisión Service ve que es texto. Diego recibe el estado real con hora y fuente, y los pasos a seguir.
7. Diego ejecuta "escalar". Es una escritura de bajo riesgo, así que Acciones Service la pasa sin aprobación: Incidentes Service crea el escalamiento con resumen, queries hechas e impacto, con la fecha límite de 1 día, y se lo asigna al on-call.

Diego le responde al cliente con el estado correcto en menos de 10 segundos. Requerimientos que se cumplen: RF01, RF02, RF04, RF05, RF07, RF08, RF10, RF12, RF17, RF22.

## Happy path 2 – SRE ejecuta una query y una escritura aprobada (Valeria)

Diagrama: [harness-hp2.pdf](Diagramas/harness-hp2.pdf)

1. Valeria, de guardia a las 3 a. m., pide: "muéstrame los últimos 100 errores del servicio de pagos".
2. Login, Filtro, Consulta y Contexto igual que arriba. El LLM propone una query.
3. Revisión Service ve que es una acción. Acciones Service la busca en la lista: query de lectura, no necesita aprobación.
4. La query corre en la Copia de lectura con timeout de 10 segundos. Vuelve con la query que corrió, cuántas filas trajo, cuánto demoró y qué tan atrasada estaba la copia. Queda en el historial.
5. Valeria pide un UPDATE con WHERE para reprocesar 12 pagos. Acciones Service ve que es escritura. Aprobación Service muestra el comando exacto y se lo manda a otro SRE por Mensajes Service (por Slack; si Slack falla, por correo).
6. El otro SRE aprueba a los 4 minutos. Acciones Service ejecuta exactamente ese comando. En Auditoría queda quién pidió, quién aprobó y qué se ejecutó.

Requerimientos que se cumplen: RF11, RF13, RF15, RF19, RNF11.

## Happy path 3 – Se cierra un incidente y todos ven lo mismo (Marco)

Diagrama: [harness-hp3.pdf](Diagramas/harness-hp3.pdf)

1. Ingeniería cierra el INC-4471. Incidentes Service lo guarda en BD Incidentes y en su réplica síncrona.
2. Incidentes Service pone el aviso "cerrado" en la Cola de Cambios.
3. De la cola se actualiza el Estado Actual, se borran las respuestas guardadas de ese incidente, SLA Service apaga las alarmas y Auditoría registra el cambio.
4. Marco pregunta por el incidente 20 segundos después. Consulta Service lee el Estado Actual: cerrado. Si Diego pregunta lo mismo, recibe exactamente la misma respuesta.
5. Marco abre el Tablero SLA (Reportes Service) y el incidente ya no aparece entre los abiertos.

Requerimientos que se cumplen: RF02, RF09, RF23, RF24, RNF07, RNF08.

## Camino de falla – El LLM no responde

Diagrama: [harness-sin-llm.pdf](Diagramas/harness-sin-llm.pdf)

No es un happy path, pero es el caso que más nos preguntó el enunciado (la primera semana del mes).

1. El LLM no responde en 5 segundos. El circuit breaker se abre.
2. Consulta Service responde igual: el Estado Actual del incidente más la respuesta guardada si la pregunta es común, avisando que es una respuesta sin LLM.
3. Si Genius entero está caído, el comando `/incident 4471` va directo de Genius App a Incidentes Service y devuelve el estado en menos de 1 segundo.

Requerimientos que se cumplen: RF18, RNF04, RNF05.
