# Lab 05 – Genius-x

Fabian Alvarado Vargas y Mauricio Salazar Hillenbrand.
Arquitectura de Software, UTEC 2026-II. Caso 5: reliability y fault tolerance.

## El problema

Genius es el software con el que la compañía maneja sus incidentes. Data science le puso un LLM local con MCP a la base de datos y a Slack, y nada más alrededor. Con eso: el LLM borró la base de datos, responde con data vieja, la primera semana de cada mes no responde, a la misma pregunta contesta distinto y dice "abierto" de incidentes que se cerraron hace horas.

Lo que hay que entregar es el diagrama del nuevo harness alrededor del LLM, marcando los SPOF y las piezas de riesgo alto. Son 10 000 incidentes por semana, 50 a 100 ingenieros y SLA de 1 día para customer escalations y 3 días para engineering.

## Qué hay acá

- `Personas/`: [Diego](Personas/Diego.md) (soporte), [Valeria](Personas/Valeria.md) (SRE on-call) y [Marco](Personas/Marco.md) (incident manager).
- Requerimientos: [funcionales](Requirements/ReqFunc.md) y [no funcionales](Requirements/ReqNoFunc.md).
- [HARNESS.md](HARNESS.md): qué falla hoy y qué pieza le pusimos a cada problema, con los SPOF y el riesgo de cada una.
- `REDALE/`: [requerimientos](REDALE/1-Requerimientos.md), [estimación](REDALE/2-Estimar.md) y [diseño del servicio](REDALE/3-Disenar-el-servicio.md).
- [HAPPY-PATH.md](HAPPY-PATH.md): los pasos del happy path.
- [REPORTE.md](REPORTE.md): las corridas del eval.

## Diagrama

Hecho en Excalidraw: [harness.pdf](Diagramas/harness.pdf) y [harness.excalidraw](Diagramas/harness.excalidraw). La iteración #1 es el harness de hoy con los SPOF en rojo; la #2 es el nuevo, con el cuello de botella, los circuit breakers y el caché marcados. El mismo diagrama en texto está en [DiagramaFinal.md](Diagramas/DiagramaFinal.md).

El diagrama con el happy path resaltado y los pasos numerados: [soporte responde y escala](Diagramas/harness-hp1.pdf) (Diego). Y el camino de falla, [el LLM no responde](Diagramas/harness-sin-llm.pdf).

## Eval

Un agente por persona (`Agents/`) evalúa los requerimientos contra sus necesidades y pain points, y un juez ([Eval-Spec](Agents/Spec/Eval-Spec.md)) da el puntaje: 7,1 en la primera corrida y 9,0 en la segunda. El eval del profesor dio 10/10. Está todo en [REPORTE.md](REPORTE.md).
