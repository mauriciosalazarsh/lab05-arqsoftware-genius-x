# Reporte de Evaluaciones (Eval-Spec) — Lab 05 Genius-x

Evaluaciones ejecutadas con Claude (Claude Code) como cliente de IA: tres subagentes independientes en paralelo, uno por persona (`Agents/Diego-Agent.md`, `Agents/Valeria-Agent.md`, `Agents/Marco-Agent.md`), cada uno leyendo solo su persona, su agente y `Requirements/*.md`; luego un cuarto subagente como juez `Agents/Spec/Eval-Spec.md` auditando las tres salidas contra el texto de los requerimientos.

**Umbral:** promedio ≥ 8/10 (80 %) y ninguna persona < 7/10.

---

## Iteración #1 — Requerimientos v1 (2026-09-10)

### Evaluaciones de las personas (tal como salieron)

#### Diego (Ingeniero de soporte)

| Ítem | Requerimiento(s) que lo cubre(n) | Nivel (5/1/0) | Comentario (una línea) |
|---|---|---|---|
| N1 | RF01, RF02, RNF03, RNF08 | 5 | RF01 me da estado, owner, último cambio con timestamp y fuente; RF02/RNF08 garantizan ≤ 30 s de antigüedad y RNF03 me lo entrega en < 1 s si pregunto por ID. |
| N2 | RF04, RF03, RNF09 | 1 | La misma respuesta está garantizada solo si la pregunta está en el catálogo canónico; ningún RF dice que los pasos por tipo de escalamiento estén ahí ni quién aprueba el catálogo. |
| N3 | RF08, RF07, RF05 | 1 | RF08 arma resumen, queries e impacto con SLA visible, pero RF12 me deja en "solo lectura" y RF11 exige aprobación para escribir, así que no sé si mi comando de escalar pasa; RF07 no dice que ingeniería = 1 día y la verificación de RF08 no revisa el impacto. |
| N4 | RF10, RF11, RF12, RF19, RNF11 | 5 | Solo herramientas registradas, escritura con comando exacto y aprobación, destructivas bloqueadas siempre y yo como soporte solo leo: una instrucción mía mal escrita no ejecuta nada. |
| P1 | RF11, RF12, RF10 | 5 | Ataca la causa: "limpia duplicados" ya no puede volverse un DELETE/DROP; con mi rol se rechaza y a un SRE le muestra el comando exacto antes de aprobar. |
| P2 | RF02, RNF08 | 5 | Invalidación de caché por evento `incident.closed` y verificación de ≤ 30 s: un incidente cerrado nunca se reporta abierto. |
| P3 | RF17, RF18, RNF01, RNF03, RNF13 | 5 | RNF01 nombra el pico de primera semana (3×) con latencias medibles; RF17 me atiende primero y me muestra cola/ETA; RF18 me da estado + canónica marcada "sin LLM" en vez de cualquier cosa. |
| P4 | RF04, RNF09, RF20 | 1 | Dentro del catálogo 100 repeticiones = 1 respuesta; fuera del catálogo RNF09 admite 5 % de variación y nadie define qué entra al catálogo ni quién lo aprueba. |
| P5 | RF16, RF06, RNF10 | 5 | Mi corrección se sirve en la siguiente consulta igual y un runbook editado se cita en ≤ 15 min: ataca justo la causa de la data vieja. |

**Flujo:** con vacíos — en pico entro por RF17 (cola con prioridad), pregunto por INC-xxxx y RF01/RF02 me dan el estado real en < 1 s (RF18 si el LLM se cae); pido pasos siguientes y RF04/RF03 me responden igual y con cita solo si la pregunta es canónica; al escalar con RF08 el camino se corta porque RF12 me tiene en solo lectura y RF11 pide aprobación de otro rol para escribir; cierro marcando feedback con RF16.

**Gaps:**
1. RF08 choca con RF12/RF11: "abrir el hilo" es escritura y soporte es solo lectura. Modificar RF12 para que escalar a ingeniería (RF08) sea acción permitida a soporte sin aprobación de terceros (o registrarla en RF10 como escritura de bajo riesgo exenta de RF11). Añadir "impacto" a la verificación de RF08.
2. RF07 dice "1 día / 3 días" sin mapear tipo → SLA. Modificar RF07: escalamiento a ingeniería = 1 día, explícito.
3. RF04 no dice quién arma y aprueba el catálogo canónico ni cuándo se revisa, y no garantiza que exista respuesta de pasos siguientes por cada tipo de escalamiento de RF07. Crear RF "Runbook canónico por tipo de escalamiento" (owner, fecha de revisión, verificación: todo tipo de RF07 tiene su canónica) y modificar RF04 con rol aprobador.
4. Fuera del catálogo, RNF09 (≥ 95 %) permite que me cambie la respuesta sin avisar. Modificar RNF09 o crear RF: si la respuesta a una pregunta repetida cambia, Genius indica qué fuente/versión cambió (usando la cita de RF03); si nada cambió, sirve la misma desde caché.
5. RF16 no dice quién valida mi corrección ni en cuánto tiempo entra al catálogo; si nadie la valida, cualquier soporte puede meter una respuesta mala que yo termino mandando al cliente. Modificar RF16 con rol validador y plazo.
6. RF11 bloquea las destructivas "aunque haya aprobación"; RNF11 las permite "con aprobación humana". Alinear RNF11 con RF11.

**Veredicto:** ¿Genius me sirve en mi día a día? Sí, para lo que más me quemaba: el estado real con fecha y fuente en menos de un segundo (RF01/RF02), la seguridad de que no vuelvo a borrar nada por escribir mal (RF11/RF12), que aprenda de mis correcciones (RF16/RF06) y que aguante la primera semana del mes (RNF01/RF17/RF18). ¿Qué me falta? Certeza de que puedo escalar a ingeniería 30 veces al día sin pedirle aprobación a nadie (RF08 vs RF12), que los pasos siguientes por tipo de escalamiento estén en el catálogo con un dueño (RF04), y que fuera del catálogo no me cambie la respuesta de un día a otro sin decirme por qué (RNF09). Con eso cerrado, lo uso sin miedo.

#### Valeria (SRE on-call)

| Ítem | Requerimiento(s) que lo cubre(n) | Nivel (5/1/0) | Comentario (una línea) |
|---|---|---|---|
| N1 — Queries read-only y E2E en segundos, resultado confiable | RF13, RF14, RNF03, RF12 | 5 | RF13 (réplica, timeout 10 s, 1 000 filas) y RF14 (sandbox, pasó/falló + log) tienen verificación; RNF03 fija P95 < 10 s en lecturas; ojo: P95 y timeout son el mismo número, la cola del 5 % se me cancela. |
| N2 — Toda escritura muestra el comando exacto y pide aprobación | RF11, RF19, RNF11 | 5 | RF11 lo dice explícito (comando exacto, aprobación antes de ejecutar, destructivas bloqueadas) y se verifica; falta que la verificación compruebe que lo mostrado es lo ejecutado, y "rol autorizado" no dice si soy yo. |
| N3 — Memoria del incidente durante toda su vida | RF05, RF08 | 5 | RF05 conserva preguntas/acciones/resultados/hipótesis mientras esté abierto y lista lo ejecutado al reabrir; RNF07 no incluye esa memoria en RPO = 0. |
| N4 — Respuestas con fuente y fecha | RF03, RF06, RNF10 | 5 | RF03: ninguna respuesta generada sale sin cita con versión y fecha; RF06/RNF10 reindexan en ≤ 15 min. |
| P1 — En el pico se cuelga 40 s y hace timeout | RF17, RNF01, RNF03, RNF06, RNF13 | 1 | Atacan la causa (3× pico, bulkheads, autoescalado por cola), pero RNF01/RNF13 no dicen cómo se verifican bajo carga y RF17 solo prioriza customer/P1: mis engineering escalations no-P1 siguen en cola justo cuando más lo uso. |
| P2 — Fix de postmortem viejo, nunca cita fuente | RF03, RF06, RF16 | 1 | La cita con fecha queda resuelta (RF03); lo obsoleto no: RF06 solo reindexa lo que cambia, un postmortem de hace dos años sin editar sigue citable y solo se corrige después de que yo lo marque (RF16). |
| P3 — Reabrir el hilo y volver a explicar todo | RF05 | 5 | La verificación de RF05 es exactamente mi caso: al reabrir, Genius lista lo ya ejecutado sin que yo lo repita. |
| P4 — Misma credencial admin para todos; nadie sabe qué más puede hacer | RF12, RNF11, RF10, RF15 | 5 | RF12/RNF11 quitan la credencial admin al LLM y actúan con mi scope (verificado soporte vs SRE); RF10 acota el "qué más puede hacer" a la allowlist con nivel de riesgo; RF15 dice quién pidió/aprobó/ejecutó. |
| P5 — Genius caído, ni el estado básico desde el bot | RF18, RNF04, RNF05, RNF07 | 1 | RF18 solo cubre LLM caído (síntoma vecino): si cae el Router/bot no hay camino definido al estado; RNF05/RNF07 bajan la probabilidad pero sin verificación de failover. |

**Flujo:** Pregunto en el hilo del incidente en Slack → RF19 filtra la entrada → RF17 me encola (posición y ETA en pico) → el LLM responde con cita y fecha (RF03) o cae a modo degradado (RF18) → si pido datos, RF13 corre la query en la réplica ≤ 10 s o RF14 lanza el E2E en sandbox → el resultado queda en la memoria del incidente (RF05) → si pido un `UPDATE`, RF11 me muestra el comando exacto, RF12 valida mi rol, alguien aprueba y RF15 lo audita. **Con vacíos:** el tramo del pico y el tramo "Genius caído" no están cerrados.

**Gaps:**
1. **RNF01 / RNF13 sin verificación de pico:** agregar prueba de carga a 3× con 100 concurrentes (RNF02) que exija P95 lectura < 10 s y una tasa máxima de timeouts de RF13; hoy solo hay una meta, no una prueba. **Modificar RF17** para priorizar también engineering escalations asignadas al on-call, no solo customer/P1.
2. **RF03 / RF06 no atacan lo obsoleto:** modificar RF06 para marcar postmortems/runbooks superseded o de versiones anteriores y agregar a RF03 una advertencia cuando la fuente tiene más de N meses o pertenece a un incidente de otra versión del sistema; verificación: una pregunta cuyo único match es un postmortem superseded devuelve la fuente vigente o el aviso.
3. **RF18 asume Router vivo:** extender RF18 (o crear un RF nuevo) con un camino de estado básico independiente de Genius (comando Slack → Incident Service directo, o página de estado) y verificarlo con el bot apagado. **RNF05** necesita verificación de failover (matar una instancia del camino crítico y que la consulta de estado siga en < 1 s).
4. **RNF07 excluye la memoria de RF05:** incluir "memoria por incidente" en RPO = 0; verificación: tras caída y recuperación, reabrir el hilo sigue listando lo ejecutado.
5. **RF11 y RNF11 se contradicen:** RF11 bloquea destructivas siempre; RNF11 dice que son posibles con aprobación. Unificar la lista exacta de bloqueado vs aprobable. Además, en RF11 agregar a la verificación que el comando mostrado es byte a byte el ejecutado y definir quién aprueba (¿yo misma o cuatro ojos?).
6. **RF13 no dice qué devuelve:** especificar que el resultado incluye la query ejecutada, el timestamp/lag de la réplica y el conteo de filas, para que "confiable" sea verificable y quede en el hilo.

**Veredicto:** ¿Genius me sirve en mi día a día? En un día normal, sí: query en la réplica en menos de 10 s, E2E en sandbox con enlace al log, ningún `UPDATE` corre sin que vea el comando exacto y lo apruebe, cada respuesta trae fuente con fecha, y al reabrir el hilo no tengo que repetir nada. Lo que me falta es justamente lo que me duele a las 3 a. m. de la primera semana del mes: nadie ha probado que el pico 3× cumpla la latencia ni cómo se priorizan mis escalaciones que no son P1; si se cae el bot (no solo el LLM) sigo sin ver ni el estado básico; Genius todavía me puede citar un postmortem de hace dos años con fecha y todo, y solo se corrige después de que yo lo marque; y no hay garantía de que la memoria del incidente sobreviva a una caída. Ciérrenme el pico y el "Genius caído" y lo uso; si no, en el pico vuelvo a hacer las queries a mano.

#### Marco (Incident manager)

| Ítem | Requerimiento(s) que lo cubre(n) | Nivel (5/1/0) | Comentario (una línea) |
|---|---|---|---|
| N1 | RF09, RF07, RF01 | 1 | La alerta antes de vencer está completa (RF09: 50 %/80 %/vencimiento, por Slack, a mí, verificable) y RF07 fija la fecha límite al crearse; pero "ver el SLA restante de cada escalamiento" solo existe preguntando incidente por incidente (RF01): no hay vista de todos mis escalamientos abiertos con SLA y RF21 no la incluye. |
| N2 | RF01, RF02, RNF08, RF18 | 5 | Un solo estado leído de la fuente de verdad, con timestamp y fuente, antigüedad ≤ 30 s, "un cerrado nunca se reporta abierto", y sigue respondiendo aunque el LLM esté caído. |
| N3 | RF15, RF11, RNF12 | 1 | RF15 registra quién pidió, quién aprobó y qué se ejecutó con usuario y timestamp, pero el registro no lleva ID de incidente y nada dice que yo pueda consultarlo sin ingeniería (RF12 solo me da "consulta" de incidentes). |
| N4 | RF21, RF20, RNF04, RNF03 | 5 | Panel con disponibilidad, errores por componente, P95 y % de aciertos de evals que yo veo hoy sin pedirlo; RNF03/RNF04 me dan los objetivos contra los que comparar. |
| P1 | RF02, RNF08, RF01 | 5 | Ataca la causa: estado desde fuente de verdad o caché invalidada por evento, ≤ 30 s, y la verificación es exactamente mi caso (cerrar y consultar). |
| P2 | RF15, RF11, RNF12, RNF07 | 5 | Cada tool call y aprobación queda con usuario y timestamp en log append-only (1 año, RPO 0); RF11 muestra el comando exacto y bloquea DROP/TRUNCATE aunque haya aprobación. |
| P3 | RF09, RF07, RNF01 | 5 | Me entero por Slack al 50 % y 80 %, no por el cliente; la fecha límite nace con el incidente y RNF01 exige aguantar el pico 3× de la primera semana del mes. |
| P4 | RF04, RF16, RNF09 | 1 | Solo garantiza una respuesta para el catálogo de canónicas; fuera de él RNF09 admite 5 % de inconsistencia y nada obliga a que dos ingenieros reciban la misma respuesta sobre el mismo incidente. |
| P5 | RF21, RF20, RNF13 | 5 | Tengo el indicador de hoy (disponibilidad, reliability, P95, errores, evals) sin pedirlo a ingeniería; RNF13 exige health endpoints y métricas por endpoint. |

Flujo: con vacíos — RF07 clasifica y fija SLA al crearse → RF09 me alerta al 50 %/80 %/vencimiento → el cliente pregunta y consulto RF01 (rol consulta, RF12) con estado fresco por RF02/RNF08, incluso sin LLM (RF18) → si algo salió mal, RF15 dice quién pidió/aprobó/ejecutó → RF21 me dice si Genius está sano hoy; los vacíos: no hay lista de mis escalamientos con SLA y no hay camino para que yo saque la auditoría de un incidente sin ingeniería.

Gaps:
1. Vista de escalamientos abiertos con SLA restante (ordenada por vencimiento, separando customer 1 día / engineering 3 días) para el incident manager: crear un RF nuevo ("Tablero de SLA") o ampliar RF21 con sección de SLA; verificación: veo todos mis escalamientos abiertos con horas restantes sin preguntar uno por uno.
2. Modificar RF15: añadir ID de incidente como campo obligatorio y verificación "para cualquier incidente se listan todas sus acciones con quién pidió, quién aprobó y qué se ejecutó". Modificar RF12: el scope "incident manager: consulta" debe incluir consultar esa auditoría por incidente a través de Genius, sin ingeniería.
3. Consistencia fuera de canónicas (P4): crear un RF (o ampliar RF05) para que toda pregunta sobre un incidente abierto responda desde el mismo hilo, el mismo estado (RF01/RF02) y la misma cita (RF03); ampliar RNF09 con una métrica de consistencia en producción, no solo en evals, y mostrarla en RF21.
4. Modificar RF21: definir umbrales "sano / degradado / no confiar" (semáforo) a partir de RNF03/RNF04 y añadir el % de respuestas marcadas correctas por RF16 en producción, no solo el % de evals de RF20.
5. Modificar RF09: contenido mínimo de la alerta (ID, cliente, tipo, hora exacta de vencimiento, owner) y canal de respaldo si Slack falla (RNF06 solo pide retries y circuit breaker).

**"¿Genius me sirve en mi día a día? ¿Qué me falta?"** Sí, me sirve para lo que más me quema: antes de escribirle al cliente veo un solo estado con timestamp y fuente (RF01/RF02), me avisan por Slack antes de que venza el SLA (RF09), cualquier acción del LLM queda con nombre, hora y aprobador (RF15/RF11) y puedo mirar si Genius está sano hoy sin molestar a ingeniería (RF21). Me falta ver todos mis escalamientos con su SLA en una sola pantalla en vez de preguntar uno por uno, poder sacar yo mismo el "quién pidió/aprobó/ejecutó" de un incidente concreto, y una garantía de que dos ingenieros le digan lo mismo al cliente cuando la pregunta no está en el catálogo de canónicas. Con esos tres ajustes, lo firmo.

### Reporte del juez (Eval-Spec)

### Diego Ramos — Soporte N2
| Ítem | Req que lo cubre | Nivel (5/1/0) | Ajuste del juez |
|---|---|---|---|
| N1 | RF01, RF02, RNF03, RNF08 | 5 | Se mantiene: RF01 fija seis campos verificables; RF02 ≤ 30 s; RNF03 P95 < 1 s. |
| N2 | RF04, RF03, RNF09 | 1 | Se mantiene: ningún RF dice que los pasos por tipo de escalamiento estén en el catálogo canónico ni quién lo aprueba. |
| N3 | RF08, RF07, RF05 | 1 | Se mantiene: RF08 no dice quién ejecuta el comando; RF12 deja a soporte en "solo lectura" y RF11 exige aprobación para "toda acción de escritura"; la verificación de RF08 omite el impacto; RF07 no mapea tipo → SLA. |
| N4 | RF10, RF11, RF12, RF19, RNF11 | 5 | Se mantiene: allowlist, comando exacto + aprobación, destructivas bloqueadas, soporte solo lectura; todos con verificación. |
| P1 | RF11, RF12, RF10 | 5 | Se mantiene: verificación de RF11 y RF12 atacan la causa. |
| P2 | RF02, RNF08 | 5 | Se mantiene: "un incidente cerrado nunca se reporta abierto", verificado en ≤ 30 s. |
| P3 | RF17, RF18, RNF01, RNF03, RNF13 | 5 | Se mantiene: RF17 prioriza customer escalations y RF18 tiene verificación con LLM apagado. |
| P4 | RF04, RNF09, RF20 | 1 | Se mantiene: garantía solo dentro del catálogo; fuera, RNF09 admite 5 % de variación. |
| P5 | RF16, RF06, RNF10 | 5 | Se mantiene: la verificación de RF16 es literalmente su caso. |
| Flujo | RF17 → RF01/RF02/RF18 → RF04/RF03 → RF08 → RF16 | 1 | Se mantiene: el tramo "escalar" está en conflicto textual RF08 vs RF12/RF11. |

Sub-scores: Necesidades 3.0/5 (12/20 × 5) · Pain points 2.52/3 (21/25 × 3) · Flujo 1/2 → **Total 6.5/10**

### Valeria Torres — SRE on-call
| Ítem | Req que lo cubre | Nivel (5/1/0) | Ajuste del juez |
|---|---|---|---|
| N1 | RF13, RF14, RNF03, RF12 | 5 | Se mantiene: ambos RF con verificación. |
| N2 | RF11, RF19, RNF11 | 5 | Se mantiene: RF11 dice qué muestra, cuándo, quién y cómo se verifica. |
| N3 | RF05, RF08 | 5 | Se mantiene. |
| N4 | RF03, RF06, RNF10 | 5 | Se mantiene: "ninguna respuesta generada sale sin al menos una cita". |
| P1 | RF17, RNF01, RNF03, RNF06, RNF13 | 1 | Se mantiene: RF17 prioriza solo customer/P1; RNF01/RNF13 no dicen cómo se verifica el pico. |
| P2 | RF03, RF06, RF16 | 1 | Se mantiene: la cita queda resuelta, lo obsoleto no. |
| P3 | RF05 | 5 | Se mantiene. |
| P4 | RF12, RNF11, RF10, RF15 | 5 | Se mantiene. |
| P5 | RF18, RNF04, RNF05, RNF07 | 1 | Se mantiene: el disparador de RF18 es "LLM no responde", no "Genius caído"; RNF05 sin verificación de failover. |
| Flujo | RF19 → RF17 → RF03/RF18 → RF13/RF14 → RF05 → RF11/RF12 → RF15 | **2** (era 1) | **Subido:** cada paso de su camino tiene RF con verificación; los tramos abiertos ya están penalizados en P1 y P5. |

Sub-scores: Necesidades 5.0/5 · Pain points 1.56/3 (13/25 × 3) · Flujo 2/2 → **Total 8.5/10**

### Marco Salas — Incident manager
| Ítem | Req que lo cubre | Nivel (5/1/0) | Ajuste del juez |
|---|---|---|---|
| N1 | RF09, RF07, RF01 | 1 | Se mantiene: la alerta está completa, pero el SLA restante solo existe incidente por incidente. |
| N2 | RF01, RF02, RNF08, RF18 | 5 | Se mantiene. |
| N3 | RF15, RF11, RNF12 | 1 | Se mantiene: RF15 sin ID de incidente y sin decir quién puede consultarlo; RF12 no incluye auditoría. |
| N4 | RF21, RF20, RNF04, RNF03 | 5 | Se mantiene. |
| P1 | RF02, RNF08, RF01 | 5 | Se mantiene. |
| P2 | RF15, RF11, RNF12, RNF07 | 5 | Se mantiene. |
| P3 | RF09, RF07, RNF01 | 5 | Se mantiene. |
| P4 | RF04, RF16, RNF09 | 1 | Se mantiene: mismo criterio que Diego P4. |
| P5 | RF21, RF20, RNF13 | 5 | Se mantiene. |
| Flujo | RF07 → RF09 → RF01/RF02/RF18 → RF15 → RF21 | 1 | Se mantiene: faltan lista de SLA y acceso propio a la auditoría. |

Sub-scores: Necesidades 3.0/5 · Pain points 2.52/3 · Flujo 1/2 → **Total 6.5/10**

### Resumen
| Persona | Score |
|---|---|
| Diego | 6.5/10 |
| Valeria | 8.5/10 |
| Marco | 6.5/10 |
| **PROMEDIO** | **(6.5 + 8.5 + 6.5) / 3 = 21.5 / 3 = 7.1/10 (71 %) — FAILED** |

Umbral: promedio 7.1 < 8.0 y dos personas < 7.0 (Diego, Marco).

### Ajustes del juez
- Todos los IDs citados existen; todos los niveles usan 5/1/0.
- Valeria, Flujo, 1 → 2: cada paso de su camino mapea a un RF con verificación; los tramos abiertos (pico 3×, Genius caído) ya están descontados en P1 y P5.
- Se mantiene Diego P3 = 5 frente a Valeria P1 = 1 sobre el mismo pico: RF17 nombra customer escalations (Diego) y no engineering escalations no-P1 (Valeria).

### Gaps priorizados
1. (Alta) Catálogo canónico sin dueño ni cobertura garantizada; fuera del catálogo ninguna garantía de misma respuesta · Diego N2, P4 · Marco P4 · Modificar RF04; crear RF "Runbook canónico por tipo"; modificar RNF09 / crear RF "misma pregunta, misma respuesta mientras la fuente no cambie".
2. (Alta) RF08 no dice quién escala y choca con RF12/RF11; RF07 no mapea tipo → SLA; verificación de RF08 omite impacto · Diego N3, Flujo · Modificar RF12/RF10, RF07, RF08.
3. (Alta) Sin vista de escalamientos abiertos con SLA restante · Marco N1, Flujo · Crear RF "Tablero de SLA".
4. (Alta) RF15 sin ID de incidente ni quién consulta; RF12 sin auditoría para incident manager · Marco N3, Flujo · Modificar RF15 y RF12.
5. (Media) RNF01/RNF13 sin verificación de pico; RF17 no prioriza engineering escalations del on-call · Valeria P1 · Prueba de carga 3× con 100 concurrentes; modificar RF17.
6. (Media) RF18 solo cubre LLM caído; RNF05 sin verificación de failover · Valeria P5 · Camino de estado independiente de Genius; verificación de failover.
7. (Media) RF03/RF06 no atacan lo obsoleto · Valeria P2 · Marcar superseded; advertencia por antigüedad.
8. (Media) RF11 y RNF11 se contradicen sobre destructivas; RF11 no verifica mostrado = ejecutado ni nombra aprobador · Alinear.
9. (Baja) RF16 sin validador ni plazo. 10. (Baja) RNF07 no incluye memoria por incidente en RPO 0. 11. (Baja) RF13 no define qué devuelve. 12. (Baja) RF21 sin umbrales ni % correctas en producción. 13. (Baja) RF09 sin contenido mínimo ni canal de respaldo.

### Resumen Iteración #1

| Persona | Score |
|---|---|
| Diego | 6.5/10 |
| Valeria | 8.5/10 |
| Marco | 6.5/10 |
| **PROMEDIO** | **7.1/10 (71 %) — FAILED** |

### Cambios aplicados para la v2 (a partir de los gaps del juez)

| Gap | Cambio en v2 |
|---|---|
| 1 Catálogo canónico sin dueño; sin garantía fuera del catálogo | RF04 con aprobador y revisión mensual; **RF22** runbook canónico por tipo; **RF23** misma pregunta → misma respuesta mientras estado y fuentes no cambien; RNF09 a ≥ 99 % y métrica en producción |
| 2 RF08 choca con RF12/RF11; RF07 sin mapeo tipo → SLA | RF10 agrega nivel "escritura de bajo riesgo" (escalar, comentar, feedback) sin aprobación; RF12 lo permite a soporte; RF07 explicita customer/support = 1 día, engineering = 3 días; RF08 verifica impacto |
| 3 Sin vista de escalamientos con SLA | **RF24** tablero de SLA ordenado por vencimiento |
| 4 RF15 sin ID de incidente ni consulta por el incident manager | RF15 con ID de incidente obligatorio y consulta desde Genius; RF12 incluye auditoría en el scope del incident manager |
| 5 Pico sin verificación; RF17 no prioriza engineering escalations | RNF01 con prueba de carga 3× / 100 concurrentes / ≤ 1 % timeouts; RF17 prioriza también engineering escalations del on-call |
| 6 RF18 solo cubre LLM caído; RNF05 sin verificación | RF18 agrega `/incident <id>` directo al Incident Service, verificado con el bot apagado; RNF05 con prueba de failover |
| 7 Fuentes obsoletas siguen citables | RF06 marca versiones reemplazadas; RF03 advierte fuentes > 12 meses o reemplazadas y ofrece la vigente |
| 8 RF11 vs RNF11 contradictorios; sin verificación mostrado = ejecutado | Ambos: destructivas/DDL bloqueadas siempre; escrituras con filtro requieren aprobación de un SRE distinto del solicitante; hash del comando mostrado = ejecutado; expiración 30 min |
| 9 RF16 sin validador ni plazo | Validación por SRE lead o incident manager en ≤ 1 día hábil; "propuesta" hasta validar |
| 10 RNF07 sin memoria por incidente | Memoria por incidente incluida en RPO 0 con verificación |
| 11 RF13 sin formato de resultado | Devuelve query ejecutada, conteo de filas, tiempo y retraso de la réplica |
| 12 RF21 sin umbrales | Semáforo sano / degradado / no confiar con umbrales de RNF03/RNF04; % correctas en producción y % consistencia |
| 13 RF09 sin contenido ni respaldo | Campos mínimos de la alerta y correo de respaldo si Slack falla |

---

## Iteración #2 — Requerimientos v2 (2026-09-10)

Mismos agentes, mismos prompts, sin memoria de la iteración anterior. Cambios aplicados: los 13 de la tabla anterior (RF03, RF04, RF06–RF13, RF15–RF18, RF21 modificados; RF22, RF23, RF24 nuevos; RNF01, RNF05, RNF07, RNF09, RNF11, RNF13 modificados).

### Evaluaciones de las personas (tal como salieron)

#### Diego (Ingeniero de soporte)

| Ítem | Requerimiento(s) que lo cubre(n) | Nivel (5/1/0) | Comentario (una línea) |
|---|---|---|---|
| N1 | RF01, RF02, RF18, RNF03, RNF08, RNF01 | 5 | Con `/incident <id>` tengo estado, owner, último cambio con timestamp y fuente en < 1 s sin pasar por el LLM, con antigüedad ≤ 30 s y probado a 3× de carga; justo lo que necesito para contestarle al cliente. |
| N2 | RF22, RF04, RF23, RNF09 | 5 | Por cada tipo de escalamiento hay una canónica de "pasos siguientes" con aprobador y fecha de revisión, servida desde caché a temperatura 0: 100 repeticiones → 1 respuesta. |
| N3 | RF08, RF07, RF12, RF10 | 1 | "escalar" me arma resumen, queries e impacto y lo asigna al on-call sin aprobación, pero RF07 dice engineering = 3 días y RF08 solo dice "fecha límite visible": no sé si ingeniería ve mi día 1 del cliente o sus 3 días. |
| N4 | RF10, RF11, RF12, RF19, RNF11 | 5 | Como soporte solo tengo lectura y escrituras de bajo riesgo; DROP/TRUNCATE/ALTER/DELETE sin filtro bloqueados siempre, el resto necesita un SRE distinto y el hash del comando mostrado debe coincidir con el ejecutado. |
| P1 | RF11, RF12, RF10, RNF11 | 5 | "Limpia los duplicados" hoy se rechaza por mi rol (RF12) y, aunque lo pidiera un SRE, un DELETE con filtro pasa por aprobación y uno sin filtro se bloquea aunque haya aprobación: ataca la causa. |
| P2 | RF02, RF01, RNF08 | 5 | Caché invalidada por evento `incident.closed`, cierre reflejado en ≤ 30 s y "un incidente cerrado nunca se reporta abierto", con timestamp y fuente para mostrárselo al cliente. |
| P3 | RNF01, RF17, RF18, RNF03, RNF05, RNF13 | 5 | Prueba de carga a 3× antes de cada release con ≤ 1 % de timeouts, mis customer escalations van segundas en la cola con posición visible y si el LLM no responde en 5 s igual recibo estado + canónica marcada "sin LLM". |
| P4 | RF23, RF04, RNF09, RF20 | 5 | Misma pregunta = texto idéntico mientras estado y fuentes no cambien; si cambió algo, la respuesta me dice qué cambió, así sé cuál mandar; evals bloquean despliegue < 95 %. |
| P5 | RF16, RF06, RF03, RNF10 | 5 | Mi corrección la valida el SRE lead o el IM en ≤ 1 día hábil y recién entonces reemplaza la canónica y entra a evals; la KB se reindexa en ≤ 15 min y la versión vieja deja de citarse como vigente. |

**Flujo:** claro con un vacío. Llega el escalamiento y RF07 le pone tipo, prioridad y fecha límite de 1 día → pregunto `/incident <id>` (RF18) y en < 1 s tengo estado real con fecha y fuente (RF01, RF02, RNF03) → pregunto "¿qué hago con este escalamiento?" y recibo la canónica con dueño, igual cada vez (RF22, RF04, RF23) → si necesito datos, query de solo lectura sobre la réplica (RF13, RF12); nada destructivo pasa (RF10, RF11) → ejecuto "escalar" (RF08) y sale el hilo con resumen, queries, impacto y fecha límite al on-call → **aquí el vacío**: no sé qué fecha límite ve ingeniería (1 día del cliente o 3 días de RF07) y las alertas de SLA (RF09) van al owner y al IM, no a mí que respondo al cliente → si la respuesta estuvo mal, la marco y propongo corrección (RF16) → en pico de mes voy en cola con posición visible o en modo degradado (RF17, RF18).

**Gaps:**
1. **Modificar RF08 y RF07:** el hilo que abre "escalar" debe mostrar la fecha límite original del escalamiento del cliente (1 día) y RF07 debe decir explícitamente que escalar a ingeniería no reinicia ni extiende la fecha límite a 3 días. Si ingeniería ve 3 días y mi cliente espera 1, el problema soy yo.
2. **Modificar RF09:** además del owner y el IM, la alerta de 50 %/80 %/vencimiento debe llegar al ingeniero de soporte que escaló (quien responde al cliente). Hoy, tras RF08 el owner es el on-call y yo me entero cuando el cliente reclama.
3. **Modificar RF16:** notificar a quien propuso la corrección cuando se valida o se rechaza (con motivo) y alertar al validador antes de que venza el día hábil; si no, una "propuesta" puede quedarse ahí para siempre y vuelvo a corregir lo mismo diez veces.
4. **Modificar RF22:** tres runbooks (customer / engineering / support) es poco granular para 20-40 escalamientos por día; la canónica de "pasos siguientes" debería existir por categoría dentro de customer (por ejemplo acceso, facturación, datos), no solo por tipo.
5. **Modificar RNF03 o RF18:** cuando no tengo el ID y consulto por descripción (RF01), la consulta pasa por el LLM con P95 < 5 s, por encima de los 2 s que necesito en pico; falta un camino directo de búsqueda por cliente o descripción sin LLM, o una latencia medible para ese caso.

**Veredicto:** ¿Genius me sirve en mi día a día? Sí. Con esta v2 le pregunto por un incidente en pico de mes y en menos de un segundo tengo el estado real con fecha y fuente; la misma pregunta me da la misma respuesta y, si cambió algo, me dice qué; y ya no tengo miedo de escribirle: como soporte no puedo ejecutar nada destructivo aunque lo escriba mal, y ni un SRE con aprobación puede tirar la base. ¿Qué me falta? Saber con certeza que cuando escalo, ingeniería ve mi fecha límite de 1 día y no una de 3; que las alertas de SLA me lleguen a mí, que soy quien le da la cara al cliente; y que cuando corrijo algo, me digan si mi corrección quedó o la rechazaron, para no volver a corregir lo mismo.

#### Valeria (SRE on-call)

| Ítem | Requerimiento(s) que lo cubre(n) | Nivel (5/1/0) | Comentario (una línea) |
|---|---|---|---|
| N1 | RF13, RF14, RF12, RNF03, RNF01 | 5 | Query sobre réplica con timeout de 10 s, 1 000 filas y retraso de réplica en la respuesta; E2E en sandbox con resumen y log; P95 < 10 s incluso a 3× (≤ 1 % timeouts); yo como SRE tengo lectura sin aprobación. |
| N2 | RF11, RF10, RF19, RNF11 | 5 | Toda escritura muestra el comando exacto, lo aprueba un SRE distinto y el hash mostrado = hash ejecutado; DDL y DELETE/UPDATE sin filtro bloqueados aun con aprobación; la salida se valida contra esquema antes de ejecutar. |
| N3 | RF05, RNF07, RF15 | 5 | Preguntas, acciones, resultados e hipótesis se conservan mientras el incidente esté abierto, se resumen al reabrir, sobreviven caídas (RPO = 0) y quedan en auditoría inmutable. |
| N4 | RF03, RF06, RNF10 | 5 | Cada respuesta cita documento con versión y fecha; si tiene > 12 meses o fue reemplazado, avisa y ofrece la vigente; la KB se reindexa en ≤ 15 min. |
| P1 | RNF01, RNF03, RF17, RF13, RNF13, RNF06 | 5 | Ataca la causa: carga probada a 3× antes de cada release, cola que pone P1 y mi escalamiento primero con posición/ETA visible, autoescalado por cola, bulkheads y timeout duro de 10 s con mensaje claro; nunca más 40 s colgada. |
| P2 | RF03, RF06 | 5 | Nada sale sin cita; un postmortem reemplazado o de > 12 meses se advierte y se sustituye por la fuente vigente; la verificación prueba exactamente mi caso. |
| P3 | RF05, RNF07 | 5 | Al reabrir el hilo Genius lista lo ya ejecutado sin que yo lo repita, incluso tras una caída. |
| P4 | RF12, RNF11, RF10, RF11, RF15 | 5 | El LLM nunca tiene credencial de admin, cada acción corre con mi scope, solo existen herramientas en allowlist con nivel visible, y la auditoría dice quién pidió, quién aprobó y qué se ejecutó. |
| P5 | RF18, RNF04, RNF05 | 5 | `/incident <id>` va directo al Incident Service sin Router ni LLM (< 1 s con el bot apagado); con el LLM caído responde estado + canónica marcada "sin LLM"; 99,9 % para estado y sin SPOF. |

**Flujo:** con vacíos — RF08 me asigna el escalamiento con resumen y acciones previas → RF17 me prioriza en el pico → RF03/RF05 me dan contexto con fuente, fecha y memoria → RF13/RF14 leo y pruebo en < 10 s → RF11 muestra el comando exacto y otro SRE aprueba → RF15 lo audita → RF18 `/incident` si Genius cae; el único hueco es la aprobación a las 3 a. m. cuando no hay un segundo SRE despierto.

**Gaps:**
1. **Modificar RF11:** no dice qué pasa cuando no hay un segundo SRE disponible (guardia única de madrugada): a quién se notifica (SRE secundario / SRE lead), por qué canal, en cuánto tiempo, y qué ocurre con un P1 abierto cuando la solicitud expira a los 30 min. Hoy solo dice "expira".
2. **Modificar RF14:** falta el timeout explícito y el mensaje de cancelación que sí tiene RF13, y qué pasa si el E2E excede la ventana (ack inmediato + resultado asíncrono al hilo). Incluir RF14 en la métrica de ≤ 1 % de timeouts de RNF01, que hoy solo cuenta RF13.
3. **Modificar RNF11:** "ninguna credencial de admin accesible al LLM" se afirma pero no se verifica en la BD: agregar verificación de que el rol que usa el Tool Gateway no tiene grants de DDL/admin (un `DROP` falla en la BD, no solo en el gateway). RF11 bloquea en el gateway y RF12 verifica por rol; nadie verifica la credencial en sí.
4. **Modificar RF05 (menor):** aclarar que la memoria es por ID de incidente y no por hilo de Slack, que se restaura si el incidente se reabre tras cerrarse, y verificar el caso de varios incidentes abiertos en paralelo, que es mi primera semana del mes.

**Veredicto:** ¿Genius me sirve en mi día a día? Sí. Con v2 mi criterio se cumple en el texto: a las 3 a. m. pido una query y en < 10 s tengo el resultado con la query ejecutada, el retraso de la réplica y la fuente con fecha; un `UPDATE` nunca corre sin que un SRE vea el comando exacto, con hash verificado, y un `DROP` no corre ni con aprobación; si Genius se cae, `/incident` me da el estado en < 1 s. ¿Qué me falta? Que RF11 diga qué hago cuando soy la única SRE despierta y necesito una escritura con filtro para un P1 (hoy espero 30 min y expira), que RF14 no me deje colgada con un E2E largo, y que alguien pruebe en la BD, no solo en el gateway, que la credencial no es admin.

#### Marco (Incident manager)

| Ítem | Requerimiento(s) que lo cubre(n) | Nivel (5/1/0) | Comentario (una línea) |
|---|---|---|---|
| N1 | RF07, RF09, RF24, RF01, RF12 | 5 | Fecha límite al crear (RF07), alertas al 50/80 %/vencimiento por Slack a mí y al owner con correo de respaldo (RF09), tablero ordenado por vencimiento con horas restantes (RF24); todo con quién, cuándo y verificación. |
| N2 | RF01, RF02, RF23, RF18, RNF08 | 5 | Un estado con último cambio + timestamp + fuente (RF01), un cerrado nunca sale abierto y se refleja en ≤ 30 s (RF02/RNF08), texto idéntico para cualquiera que pregunte (RF23), `/incident` directo sin LLM (RF18). |
| N3 | RF15, RF11, RF12, RNF12, RNF07 | 5 | Auditoría inmutable por incidente con quién pidió, quién aprobó y qué se ejecutó (RF15), hash del comando mostrado = ejecutado (RF11), la consulto yo sin ingeniería (RF12), append-only 1 año y RPO 0 (RNF12/RNF07). |
| N4 | RF21, RF20, RNF03, RNF04, RNF13 | 5 | Semáforo sano/degradado/no confiar con disponibilidad, errores por componente, P95 y % correctas (evals y producción); lo veo hoy sin pedirlo (RF21). Umbrales de calidad del semáforo flojos (ver gaps). |
| P1 | RF02, RF01, RNF08, RF18 | 5 | Ataca la causa: estado leído de la fuente de verdad o caché invalidada por evento `incident.closed`; antes de escribirle al cliente veo hora de última actualización. |
| P2 | RF15, RF11, RF10, RNF11, RNF12, RNF07 | 5 | Cada tool call queda con usuario, aprobador y resultado (RF15); comando exacto con hash (RF11); DROP/TRUNCATE bloqueados aunque haya aprobación (RF10/RNF11); la auditoría sobrevive una caída (RNF07). |
| P3 | RF09, RF24, RF07, RNF01, RF17 | 5 | Me entero por Genius, no por el cliente: alertas al 50/80 % (RF09) + tablero (RF24); el pico de la primera semana está dimensionado a 3× (RNF01) y RF17 prioriza customer escalations en cola. |
| P4 | RF23, RF04, RNF09, RF16 | 5 | Dos usuarios, misma pregunta, mismo estado → texto idéntico (RF23); canónicas con dueño y temp 0, 100 repeticiones → 1 respuesta (RF04); una corrección no cambia nada hasta validarse (RF16). |
| P5 | RF21, RF20, RNF13 | 5 | Existe el indicador: semáforo del día con % de evals, errores por componente y disponibilidad, visible para mí sin pasar por ingeniería. |

**Flujo:** Se crea el escalamiento y RF07 le pone tipo y fecha límite → lo veo en el tablero RF24 → RF09 me avisa al 50/80 % por Slack (o correo) → antes de escribirle al cliente pido `/incident` (RF18) o consulto RF01 y obtengo un solo estado con timestamp ≤ 30 s (RF02) → cualquiera que pregunte recibe lo mismo (RF23) → si el LLM hizo algo, abro la auditoría RF15 con quién pidió/aprobó/ejecutó → RF21 me dice si hoy confío en Genius. **Claro.**

**Gaps:**
1. **RF12 (modificar):** mi scope lista consulta, tablero RF24 y auditoría RF15, pero omite el panel de salud RF21; si el RBAC lo aplica literal, me bloquea lo que RF21 promete. Agregar RF21 al scope del incident manager.
2. **RF21 (modificar):** el semáforo solo se define por los umbrales de RNF03/RNF04 (latencia y disponibilidad); el % de aciertos y el % de correctas en producción se muestran pero no encienden "no confiar". Agregar umbral: aciertos < 95 % (RF20) o consistencia < 99 % (RNF09) → "no confiar". Hoy podría ver luz verde con respuestas malas.
3. **RF24 (modificar):** no distingue escalamientos ya vencidos (quedarían con horas negativas mezcladas con los vivos). Agregar estado "vencido" y conteo separado.
4. **RNF13 (modificar):** "alerta cuando se abre el circuito hacia el LLM" no dice a quién llega. Que llegue también al incident manager o se refleje explícitamente como "degradado" en RF21.
5. **RF23 (modificar):** dice "pregunta repetida" sin precisar "exacta o semánticamente equivalente" como sí lo hace RF04; alinear el texto para que dos ingenieros con distinta redacción caigan en la misma caché.

**Veredicto:** ¿Genius me sirve en mi día a día? Sí. Con esta v2 tengo lo que pedí: un solo estado con hora antes de escribirle al cliente, alertas de SLA que me llegan a mí antes de vencer, un tablero para no preguntar uno por uno, auditoría por incidente con nombre, hora y aprobador de cada acción del LLM, y un semáforo para decidir si confío hoy. Lo que me falta es fino: que RF12 no me cierre la puerta del panel RF21, que el semáforo se ponga en rojo por calidad y no solo por latencia, y que el tablero me separe los vencidos. Si se corrigen esos cinco puntos, firmo.

### Reporte del juez (Eval-Spec)

Verificación previa: las tres evaluaciones usan solo 5/1/0 y todos los IDs citados existen (RF01–RF24, RNF01–RNF13).

#### Diego Ramos — Ingeniero de soporte N2
| Ítem | Req que lo cubre | Nivel (5/1/0) | Ajuste del juez |
|---|---|---|---|
| N1 | RF01, RF02, RF18, RNF03, RNF08, RNF01 | 5 | Sin ajuste. RF01 fija los siete campos; RF18 verifica `/incident` < 1 s sin LLM; RNF01 lo prueba a 3×. |
| N2 | RF22, RF04, RF23, RNF09 | 5 | Sin ajuste. RF22 exige canónica por tipo con aprobador y fecha; RF04 dice quién aprueba y cuándo se revisa. |
| N3 | RF08, RF07, RF12, RF10 | 1 | Se mantiene 1. RF08 no dice qué fecha límite muestra el hilo; RF07 admite 1 y 3 días y nada dice si escalar conserva el plazo original. |
| N4 | RF10, RF11, RF12, RF19, RNF11 | 5 | Sin ajuste. Rol verificado (RF12) y bloqueo absoluto de destructivas (RF11). |
| P1 | RF11, RF12, RF10, RNF11 | 5 | Sin ajuste. Ataca la causa en dos capas verificadas. |
| P2 | RF02, RF01, RNF08 | 5 | Sin ajuste. Invalidación por evento, verificación ≤ 30 s. |
| P3 | RNF01, RF17, RF18, RNF03, RNF05, RNF13 | 5 | Sin ajuste. Carga 3× probada, cola con posición, fallback a los 5 s. |
| P4 | RF23, RF04, RNF09, RF20 | 5 | Sin ajuste. RF23 verifica texto idéntico y que la respuesta nueva nombre el cambio. |
| P5 | RF16, RF06, RF03, RNF10 | 5 | Sin ajuste. RF16 dice quién valida, cuándo, qué produce y verifica ambos casos. |

Flujo: 1/2 — el camino existe de punta a punta pero se corta en "escalar": no está definido qué plazo ve ingeniería (RF08) y las alertas de RF09 no llegan a quien responde al cliente.

Sub-scores: Necesidades 4,0/5 · Pain points 3,0/3 · Flujo 1/2 → **Total 8,0/10**

#### Valeria Torres — SRE on-call
| Ítem | Req que lo cubre | Nivel (5/1/0) | Ajuste del juez |
|---|---|---|---|
| N1 | RF13, RF14, RF12, RNF03, RNF01 | 5 | Sin ajuste. RF13 dice qué produce y verifica la cancelación; RF14 produce resumen + enlace. Falta timeout propio en RF14 (gap). |
| N2 | RF11, RF10, RF19, RNF11 | 5 | Sin ajuste. Comando exacto, aprobación de un SRE distinto, hash mostrado = ejecutado. |
| N3 | RF05, RNF07, RF15 | 5 | Sin ajuste. RF05 conserva y resume; RNF07 fija RPO = 0 para la memoria. |
| N4 | RF03, RF06, RNF10 | 5 | Sin ajuste. Cita con versión y fecha; advierte > 12 meses o reemplazada. |
| P1 | RNF01, RNF03, RF17, RF13, RNF13, RNF06 | 5 | Sin ajuste. Capacidad probada a 3×, P1 primero en cola, timeout duro de 10 s. |
| P2 | RF03, RF06 | 5 | Sin ajuste. La verificación de RF03 prueba el caso del postmortem reemplazado. |
| P3 | RF05, RNF07 | 5 | Sin ajuste. |
| P4 | RF12, RNF11, RF10, RF11, RF15 | 5 | Sin ajuste. La cláusula "ninguna credencial de admin" no tiene verificación propia en la BD: gap de verificación, no de cobertura. |
| P5 | RF18, RNF04, RNF05 | 5 | Sin ajuste. `/incident` < 1 s con el bot apagado; sin SPOF verificado. |

Flujo: 1/2 — completo salvo un vacío real: RF11 exige un SRE distinto y solo dice "expira en 30 min"; en guardia única de madrugada una escritura con filtro para un P1 no tiene camino.

Sub-scores: Necesidades 5,0/5 · Pain points 3,0/3 · Flujo 1/2 → **Total 9,0/10**

#### Marco Salas — Incident manager
| Ítem | Req que lo cubre | Nivel (5/1/0) | Ajuste del juez |
|---|---|---|---|
| N1 | RF07, RF09, RF24, RF01, RF12 | 5 | Sin ajuste. RF09 dice cuándo, a quién, qué campos, fallback y verificación; RF24 verifica 100 % de abiertos. |
| N2 | RF01, RF02, RF23, RF18, RNF08 | 5 | Sin ajuste. RF23 aplica a cualquier usuario; RF02 verifica ≤ 30 s. |
| N3 | RF15, RF11, RF12, RNF12, RNF07 | 5 | Sin ajuste. Auditoría por incidente; RF12 la da al IM sin ingeniería. |
| N4 | RF21, RF20, RNF03, RNF04, RNF13 | 5 | Sin ajuste. RF21 muestra las métricas y nombra al IM en su verificación; la omisión en RF12 y el semáforo ciego a calidad son gaps. |
| P1 | RF02, RF01, RNF08, RF18 | 5 | Sin ajuste. |
| P2 | RF15, RF11, RF10, RNF11, RNF12, RNF07 | 5 | Sin ajuste. |
| P3 | RF09, RF24, RF07, RNF01, RF17 | 5 | Sin ajuste. |
| P4 | RF23, RF04, RNF09, RF16 | 5 | Sin ajuste. RF23 verifica dos usuarios → texto idéntico. |
| P5 | RF21, RF20, RNF13 | 5 | Sin ajuste. |

Flujo: 2/2 — RF07 → RF24 → RF09 → RF18/RF01 → RF02 → RF23 → RF15 → RF21, cada paso con verificación.

Sub-scores: Necesidades 5,0/5 · Pain points 3,0/3 · Flujo 2/2 → **Total 10,0/10**

### Resumen Iteración #2

| Persona | Score |
|---|---|
| Diego | 8,0/10 |
| Valeria | 9,0/10 |
| Marco | 10,0/10 |
| **PROMEDIO** | **(8,0 + 9,0 + 10,0) / 3 = 27,0 / 3 = 9,0/10 (90 %) — PASSED** |

Umbral: promedio 9,0 ≥ 8,0 ✓ · mínimo por persona 8,0 ≥ 7,0 ✓. Ajustes del juez: ninguno (todos los puntajes auditados y mantenidos).

### Gaps pendientes (entrada para una v3, no bloquean el lab)

| Prioridad | Gap | Afecta | RF/RNF |
|---|---|---|---|
| Alta | El hilo de "escalar" no dice qué fecha límite muestra; RF07 no dice si escalar conserva el plazo de 1 día | Diego N3, Marco | RF08, RF07 |
| Alta | Las alertas de SLA no llegan al ingeniero de soporte que escaló y responde al cliente | Diego, Marco | RF09 |
| Alta | RF11 no dice qué pasa sin un segundo SRE disponible (guardia única de madrugada, P1) ni qué ocurre al expirar | Valeria | RF11 |
| Media | "Ninguna credencial de admin" sin verificación en la BD (grants del rol del Tool Gateway) | Valeria, Diego, Marco | RNF11, RF12 |
| Media | RF23 sin "exacta o semánticamente equivalente" como RF04 | Diego, Marco | RF23 |
| Media | Scope del incident manager en RF12 omite RF21; semáforo no reacciona a calidad ni a circuito abierto; RNF13 sin destinatario | Marco | RF12, RF21, RNF13 |
| Baja | RF14 sin timeout ni resultado asíncrono; RNF01 solo mide timeouts de RF13 | Valeria | RF14, RNF01 |
| Baja | RF16 sin notificación al proponente ni recordatorio al validador | Diego | RF16 |
| Baja | RF24 no separa escalamientos vencidos | Marco | RF24 |
| Baja | Consulta por descripción pasa por el LLM sin latencia medible en pico | Diego | RF18, RNF03 |
| Baja | RF05 no aclara memoria por ID de incidente ni varios incidentes en paralelo | Valeria | RF05 |
| Baja | RF22 poco granular (una canónica por tipo) | Diego | RF22 |

---

### Nota

Después del eval reescribimos los requerimientos con palabras más simples y en formato de lista (sin tablas), y renombramos las piezas del harness (Consulta Service, Acciones Service, Cola de Cambios, etc.). No cambió el contenido de ningún RF/RNF ni sus IDs, por eso no volvimos a correr el eval: el 9,0 sigue valiendo. Después agregamos RF25 (skills) al comparar el harness con el esquema de clase; es un requerimiento nuevo, así que si el profe pide el eval sobre la versión final habría que correrlo de nuevo.

## ¿Qué cambió entre iteraciones?

| | Iteración #1 (v1) | Iteración #2 (v2) |
|---|---|---|
| Diego | 6,5 | 8,0 |
| Valeria | 8,5 | 9,0 |
| Marco | 6,5 | 10,0 |
| **Promedio** | **7,1 — FAILED** | **9,0 — PASSED** |

Lo que movió el score: (1) definir quién puede ejecutar cada acción y con qué nivel de riesgo (RF10/RF12) destrabó el flujo de soporte; (2) el tablero de SLA (RF24) y la auditoría consultable por incidente (RF15/RF12) cerraron las dos necesidades de Marco; (3) garantizar la misma respuesta fuera del catálogo (RF23) y el camino directo de estado sin LLM (RF18) resolvieron los pain points compartidos de determinismo y "Genius caído". Los tres gaps altos que quedan son de detalle en el flujo de escalar (plazo visible, destinatarios de alertas, aprobación en guardia única).
