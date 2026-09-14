# Happy path

El happy path es el camino más común y sin errores por el diagrama. Lo seguimos flecha por flecha para comprobar que la arquitectura de verdad lo cumple. Tiene su copia del diagrama con el camino resaltado y los pasos numerados en `Diagramas/`.

## Happy path – Soporte responde al cliente y escala (Diego)

Diagrama: [harness-hp1.pdf](Diagramas/harness-hp1.pdf)

1. Diego escribe en Genius App: "¿en qué está el INC-4471 y qué hago?".
2. Login Service ve que es soporte. Filtro Service revisa que la pregunta esté limpia.
3. Consulta Service busca en Cache de Respuestas. Como es un incidente puntual, no existe.
4. Contexto Service junta el Estado Actual del incidente, los pasos a seguir para customer escalations y el historial de ese incidente.
5. La pregunta entra a la Cola de Preguntas. Como es customer escalation va segunda en prioridad. LLM local #1 responde en menos de 5 segundos.
6. Revisión Service ve que es texto. Diego recibe el estado real con hora y fuente, y los pasos a seguir.
7. Diego ejecuta "escalar". Es una escritura de bajo riesgo, así que Acciones Service la pasa sin aprobación: Incidentes Service crea el escalamiento con resumen, queries hechas e impacto, con la fecha límite de 1 día, y se lo asigna al on-call.

Diego le responde al cliente con el estado correcto en menos de 10 segundos. Requerimientos que se cumplen: RF01, RF02, RF04, RF05, RF07, RF08, RF10, RF12, RF17, RF22.

## Camino de falla – El LLM no responde

Diagrama: [harness-sin-llm.pdf](Diagramas/harness-sin-llm.pdf)

No es un happy path, pero es el caso que más nos preguntó el enunciado (la primera semana del mes).

1. El LLM no responde en 5 segundos. El circuit breaker se abre.
2. Consulta Service responde igual: el Estado Actual del incidente más la respuesta guardada si la pregunta es común, avisando que es una respuesta sin LLM.
3. Si Genius entero está caído, el comando `/incident 4471` va directo de Genius App a Incidentes Service y devuelve el estado en menos de 1 segundo.

Requerimientos que se cumplen: RF18, RNF04, RNF05.
