# Harness de Genius-x

El harness son todas las piezas que van alrededor del LLM para que responda bien, rápido y sin romper nada. Hoy Genius solo tiene API → LLM → MCP a la base de datos y a Slack. Por eso pasan las cinco cosas del enunciado. Fuimos problema por problema y para cada uno pusimos una pieza, cada una con una sola responsabilidad, como los services que vimos en clase.

Diagrama: [Diagramas/harness.pdf](Diagramas/harness.pdf) (fuente editable: [harness.excalidraw](Diagramas/harness.excalidraw)).

## 1. Qué falla hoy y por qué

| Lo que pasó | Por qué pasa con el harness actual | Qué es |
|---|---|---|
| El LLM borró la base de datos | El LLM habla directo con la BD con una credencial de administrador. Nadie revisa qué va a ejecutar ni pide permiso | Riesgo alto |
| Responde con data vieja y no aprende | El LLM solo sabe lo que tiene en la pregunta o lo que aprendió al entrenarse. No hay runbooks ni postmortems actualizados ni historial del incidente | Riesgo alto |
| La primera semana del mes no responde | Hay un solo LLM y una sola API. Sin cola, todos le caen a la vez; sin timeout, se cuelga | SPOF (LLM y API) |
| La misma pregunta, respuestas distintas | No guarda respuestas. Cada vez genera una nueva | Riesgo medio |
| Dice "abierto" de un incidente cerrado hace horas | Nadie le avisa cuando cambia un incidente | Riesgo alto |
| Si Slack se cae, Genius se cae | Le habla directo a Slack, sin cola ni circuit breaker | SPOF (Slack) |

## 2. Cómo lo pensamos: seguir el camino de cada cosa que pasa

**Camino de una pregunta.** El ingeniero escribe en Genius App → **Login Service** ve quién es y qué puede hacer → **Filtro Service** revisa que la pregunta no traiga cosas raras (instrucciones escondidas, datos sensibles) → **Consulta Service** busca en **Cache de Respuestas**: si ya existe, responde igual que siempre (así la misma pregunta da la misma respuesta); si no existe → **Contexto Service** junta lo que el LLM necesita: el **Estado Actual** del incidente, los runbooks y postmortems de la **Base de Conocimiento** (con fecha y versión), el **Historial** de lo que ya se hizo en ese incidente y la **Skill** de la tarea (la guía paso a paso de cómo se hace ese tipo de trabajo y con qué acciones) → **Cola de Preguntas** (las urgentes primero) → **LLM local** → **Revisión Service** revisa la respuesta antes de mostrarla → respuesta al ingeniero, con su fuente y fecha.

**Camino de una acción.** Si la respuesta del LLM es "quiero ejecutar algo" → **Acciones Service** mira la lista de acciones permitidas y el rol del usuario: lectura → ejecuta en la **Copia de lectura** de la BD o en **Pruebas Service**; escritura → **Aprobación Service** le manda el comando exacto a otro SRE por **Mensajes Service** y espera el OK; borrar tablas o cambiar estructura → **BLOQUEADO**, sin excepción. Todo queda en **Auditoría**.

**Camino de un cambio de incidente.** Cuando **Incidentes Service** crea, cambia o cierra un incidente, pone un aviso en la **Cola de Cambios**. De ahí se actualiza el **Estado Actual** (para que nunca se diga "abierto" de algo cerrado), se borran las **Cache de Respuestas** de ese incidente, **SLA Service** arma o apaga sus alarmas y **Auditoría** guarda el cambio.

**Aprender y vigilar.** **Aprendizaje Service** recibe el "esta respuesta estuvo mal" con la corrección, la valida una persona y recién ahí entra a Cache de Respuestas. **Indexar Job** actualiza la Base de Conocimiento y las Skills cada 15 minutos. **Pruebas Diarias Job** le hace al LLM las preguntas comunes cada día y compara con la respuesta esperada. **Monitoreo Service** mide disponibilidad, latencia y errores de cada pieza. **Reportes Service** arma con eso, y con los plazos de SLA Service, el **Tablero SLA** y el **Panel de salud** con semáforo que ve el incident manager.

## 3. Piezas del harness

| # | Pieza | Qué hace | Problema que arregla | Cómo aguanta fallas | Riesgo | RF / RNF |
|---|---|---|---|---|---|---|
| 1 | **Genius App** (Slack / Web) | Donde el ingeniero pregunta y ve respuestas, tablero y panel | — | Dos copias detrás de un balanceador | Bajo | RF01, RF24 |
| 2 | **Login Service** | Sabe quién es el usuario y qué puede hacer (soporte, SRE, incident manager) | Todos usaban la misma credencial de admin | Dos copias; límite de pedidos por usuario | Alto | RF12 |
| 2b | **Registro de Usuarios Service** | Un administrador crea la cuenta, le pone el rol y la desactiva cuando alguien sale del equipo. Guarda usuario y rol en la BD que consulta el Login | Nadie sabía quién tenía acceso ni con qué permisos | Solo el administrador entra; cada alta y baja queda en Auditoría | Alto | RF26, RF12 |
| 3 | **Filtro Service** | Revisa la pregunta antes de pasarla: instrucciones escondidas, datos sensibles, ¿es consulta o acción? | Instrucciones peligrosas | Si duda, rechaza | Alto | RF19 |
| 4 | **Consulta Service** | Busca si la pregunta ya tiene respuesta guardada; si no, la manda a armar contexto | Respuestas distintas a la misma pregunta; carga innecesaria al LLM | Responde desde lo guardado aunque el LLM esté caído | Medio | RF01, RF04, RF18, RF23 |
| 5 | **Cache de Respuestas** (BD) | Respuestas aprobadas a preguntas comunes y respuestas ya dadas por incidente. Es el caché que protege al LLM, que es el cuello de botella | Misma pregunta, distinta respuesta | Se borran cuando cambia el incidente o la fuente | Medio | RF04, RF22, RF23 |
| 6 | **Estado Actual** (BD) | Copia del estado de cada incidente, actualizada al instante por la Cola de Cambios | "Abierto" de un incidente cerrado | Antigüedad máxima 30 s | Alto | RF02 |
| 7 | **Contexto Service** | Junta estado actual + fragmentos de la Base de Conocimiento (con fecha) + historial del incidente | Data vieja, sin fuente | Si una fuente tiene más de 12 meses o fue reemplazada, lo avisa | Medio | RF03, RF05, RF06 |
| 8 | **Historial** (BD) | Lo que ya se preguntó y se hizo en cada incidente | Volver a explicar el incidente | Guardado en BD, no en el LLM; sobrevive caídas | Bajo | RF05 |
| 9 | **Base de Conocimiento** (BD) | Runbooks, postmortems e incidentes cerrados, con versión y fecha | "No aprende" | Indexar Job la actualiza cada 15 min | Medio | RF06 |
| 9b | **Skills** (BD) | Guías paso a paso por tipo de tarea (investigar pagos, query de lectura, E2E, escalar), escritas por ingeniería, con versión. Contexto Service carga la que corresponde; el LLM sigue esos pasos y usa solo las acciones que la skill indica | Respuestas improvisadas y distintas para la misma tarea; acciones fuera de lugar | Versionadas; una skill nueva pasa por las pruebas diarias antes de usarse | Medio | RF25 |
| 10 | **Cola de Preguntas** | Ordena las preguntas al LLM: P1, customer escalations, engineering del on-call, resto. Muestra posición | El pico de la primera semana del mes | Si la cola crece, se levantan más copias del LLM | Alto | RF17 |
| 11 | **LLM local** (2 o 3 copias) | Genera la respuesta | Un solo LLM que se cuelga | Timeout 5 s, reintento en otra copia, circuit breaker: si no responde, Consulta Service contesta sin LLM | Alto | RNF01, RNF05 |
| 12 | **Revisión Service** | Revisa la respuesta del LLM: ¿tiene la forma correcta? ¿es texto o es una acción? | Acciones mal armadas o inventadas | Si no pasa la revisión, no se ejecuta nada | Alto | RF19 |
| 13 | **Acciones Service** | Lista de acciones permitidas con su nivel: lectura, escritura de bajo riesgo, escritura, prohibida. Aplica el rol del usuario | El borrado de la BD | Borrar tablas o cambiar estructura: bloqueado siempre. Timeout por acción | **Muy alto** | RF08, RF10, RF11, RF13 |
| 14 | **Aprobación Service** | Manda el comando exacto a otro SRE y espera su OK; expira en 30 min | Escrituras sin control | Guarda el hash del comando: lo mostrado es lo ejecutado | Alto | RF11 |
| 15 | **Copia de lectura** (BD) | Copia de la BD solo para consultas del LLM | Consultas pesadas en la BD principal | Timeout 10 s, máximo 1 000 filas | Medio | RF13 |
| 16 | **Pruebas Service** | Corre E2E tests en un ambiente aparte y devuelve resumen + log | Tests que tocan producción | Aislado de producción | Medio | RF14 |
| 17 | **Incidentes Service** | Crea, clasifica y cierra incidentes; pone tipo, prioridad y fecha límite (1 día / 3 días) | Estados inconsistentes | BD principal con réplica síncrona y cambio automático si se cae | Alto | RF01, RF07, RF18 |
| 18 | **BD Incidentes** (principal + réplica síncrona) | Fuente de verdad | — | Réplica síncrona: no se pierde nada (RPO 0) | Alto | RNF05, RNF07 |
| 19 | **Cola de Cambios** | Avisa a las demás piezas cada vez que un incidente cambia | Nadie se enteraba de los cambios | Cola durable: el aviso no se pierde aunque una pieza esté caída | Medio | RF02 |
| 20 | **SLA Service** | Alarmas al 50 %, 80 % y 100 % del plazo; arma el Tablero SLA | Plazos vencidos sin aviso | Alarmas guardadas en BD, se reintentan | Medio | RF07, RF09, RF24 |
| 21 | **Mensajes Service** | Manda avisos y pedidos de aprobación por Slack o correo | Slack caído tumbaba a Genius | Cola con reintentos y circuit breaker; si Slack falla, correo | Medio | RF09, RF11 |
| 22 | **Auditoría** (BD) | Cada pregunta, respuesta, acción, aprobación y resultado, con usuario, hora e incidente | Nadie sabía quién dio la orden | Solo se agrega, nunca se borra; 1 año | Medio | RF15 |
| 23 | **Aprendizaje Service** | Recibe el feedback (correcta / incorrecta + corrección), lo valida una persona y actualiza Cache de Respuestas | Corregir lo mismo diez veces | Nada cambia hasta que se valida | Bajo | RF16 |
| 24 | **Indexar Job** (cada 15 min) | Mete en la Base de Conocimiento lo nuevo o cambiado y marca lo reemplazado | Fuentes viejas | Corre por aviso o por reloj | Bajo | RF06 |
| 25 | **Pruebas Diarias Job** | Hace las preguntas comunes y compara con la respuesta esperada; si acierta menos de 95 %, no se despliega el cambio | Respuestas que cambian sin que nadie se dé cuenta | Corre a diario y ante cada cambio de modelo | Medio | RF20 |
| 26 | **Monitoreo Service** | Health de cada pieza, Availability = 2xx/(2xx+5xx), Reliability = 2xx/(2xx+4xx+5xx), P95, cola, errores | No saber si Genius está sano | Alerta cuando se abre un circuit breaker | Bajo | RF21, RNF13 |
| 27 | **Reportes Service** + **Tablero SLA / Panel de salud** | Arma el tablero de plazos (de SLA Service) y el panel con semáforo sano / degradado / no confiar (de Monitoreo Service) | Preguntar uno por uno; no saber si confiar hoy | Solo lee; si se cae, Genius sigue respondiendo | Bajo | RF21, RF24 |

APIs externas: **Slack API** (mensajes y aprobaciones) y **correo**. El LLM es interno, pero lo tratamos como si fuera externo: timeout y circuit breaker.

## 3b. Cómo se compara con el harness de la clase

El esquema de clase pone alrededor del LLM ocho bloques. Así quedan en el nuestro:

| Bloque de la clase | En Genius-x |
|---|---|
| System Prompts | Las instrucciones base del LLM (rol, reglas, formato) que Contexto Service pone al inicio de cada pregunta. Tienen versión: si cambian, corren las Pruebas Diarias antes de desplegar (RF20) |
| Context Loading | Contexto Service: carga estado actual, historial, conocimiento y skill |
| RAG | Contexto Service + Base de Conocimiento (busca los fragmentos que sirven y los cita con fecha) |
| Skills | Skills: guías por tipo de tarea, versionadas |
| 3rd-Party Tools | Acciones Service con su lista de acciones permitidas (queries en la Copia de lectura, E2E en Pruebas Service, escalar, Slack) |
| Code Sandbox | Pruebas Service (E2E en un ambiente aparte) y la Copia de lectura para queries |
| Sub-agents | No usamos sub-agentes que ejecuten cosas por su cuenta (riesgo). Lo más parecido: el modelo chico del Filtro Service y la Revisión Service, que solo revisan |
| Loop Control | Revisión Service corta el ciclo: máximo 3 acciones por pregunta y luego el LLM tiene que responder; timeout de 5 s y circuit breaker en la Cola |

## 4. SPOF: qué se caía antes y qué pasa ahora

| Antes (SPOF) | Ahora |
|---|---|
| Un solo LLM | 2 o 3 copias; si ninguna responde, Consulta Service contesta con el estado del incidente y la respuesta guardada, marcado "sin LLM" |
| Una sola API | Genius App y cada service en dos copias detrás de un balanceador |
| Una sola BD, y el LLM podía borrarla | BD principal con réplica síncrona; el LLM solo llega a la Copia de lectura; escribir pasa por Acciones y Aprobación; borrar está bloqueado |
| Slack directo | Mensajes Service con cola, reintentos y circuit breaker; correo de respaldo |
| Conocimiento solo en la pregunta | Base de Conocimiento actualizada + Historial por incidente en BD |

El único SPOF que queda es **Slack API**, porque es de un tercero y es el único canal de avisos. No lo podemos duplicar, así que lo aguantamos con el circuit breaker de Mensajes Service y con el correo de respaldo.

## 5. Piezas de riesgo alto (las que hay que vigilar primero)

1. **Acciones Service + Aprobación Service**: es el único camino para ejecutar algo. Si fallan "abiertos", se repite el borrado. Por eso, ante cualquier duda, no ejecutan.
2. **LLM local** (el cuello de botella): se satura en la primera semana del mes. Lo aguantan la Cola de Preguntas, las dos copias, el circuit breaker y el Cache de Respuestas. Sin eso, se cae todo.
3. **Estado Actual**: si no se actualiza, vuelve el "abierto" de un incidente cerrado.
4. **BD Incidentes**: fuente de verdad. Réplica síncrona obligatoria.
5. **Login Service**: si se equivoca de rol, el LLM hace más de lo que debe.

## 6. Qué pasa si el LLM no responde

1. Pasan 5 segundos sin respuesta, o el circuit breaker ya está abierto.
2. Consulta Service responde igual: estado del incidente desde Estado Actual + respuesta guardada si la pregunta es común, marcado "respuesta sin LLM".
3. Las acciones de lectura siguen funcionando. Las de escritura se pausan.
4. Si se cae Genius entera (no solo el LLM), el comando `/incident <id>` va directo a Incidentes Service y responde el estado en menos de 1 segundo.
5. El circuit breaker prueba de nuevo cada 30 segundos y se cierra después de 3 respuestas buenas.

## 7. Patrones de reliability que usamos (nombres de clase)

Timeout · Retry · Circuit breaker · Cola para aguantar picos · Copias de cada service (sin SPOF) · Réplica síncrona de la BD · Copia de lectura · Respuesta sin LLM (degradación controlada) · Health endpoints · Aviso de cambio para no usar estado viejo · Aprobación humana antes de escribir · Mínimo privilegio · Auditoría · Pruebas diarias antes de desplegar.
