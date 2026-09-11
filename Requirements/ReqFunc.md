# Requerimientos Funcionales

## Consultas

- **RF01** – El sistema debe permitir preguntar por un incidente (por ID o describiéndolo) y responder con su estado, owner, prioridad, tipo, cuánto SLA le queda, cuándo fue el último cambio y de dónde sale la información.
- **RF02** – El estado que responde Genius siempre tiene que ser el real. Si un incidente se cerró, la respuesta lo refleja en máximo 30 segundos. Nunca puede decir "abierto" de un incidente que ya está cerrado.
- **RF03** – Toda respuesta generada por el LLM debe decir de dónde salió (runbook, postmortem o incidente), con versión y fecha. Si la fuente tiene más de un año o ya fue reemplazada, debe avisarlo y ofrecer la vigente.
- **RF04** – Las preguntas frecuentes tienen una respuesta aprobada por el incident manager o el SRE lead, que se revisa cada mes. La misma pregunta (aunque se escriba distinto) devuelve siempre la misma respuesta, sin aleatoriedad del LLM.
- **RF05** – Genius guarda el historial de cada incidente (qué se preguntó, qué se ejecutó, qué salió) mientras está abierto, y lo resume cuando alguien reabre el hilo, sin que haya que explicarle todo de nuevo.
- **RF06** – Los runbooks, postmortems e incidentes cerrados entran solos a la base de conocimiento, como máximo 15 minutos después de cambiar. La versión nueva marca la vieja como reemplazada.

## Escalamientos y SLA

- **RF07** – Al crearse un escalamiento, el sistema le pone tipo (customer, engineering o support), prioridad y fecha límite: customer y support tienen 1 día, engineering 3 días.
- **RF08** – Un ingeniero de soporte o un SRE puede escalar un incidente a ingeniería con un comando. Genius arma el resumen, las queries que ya se hicieron y el impacto, abre el hilo con la fecha límite y se lo asigna al on-call. Soporte no necesita aprobación de nadie para escalar.
- **RF09** – Cuando un escalamiento va por el 50 % y el 80 % de su plazo, y cuando vence, el sistema avisa por Slack al owner y al incident manager con el ID, el cliente, el tipo, el owner y la hora exacta de vencimiento. Si Slack no responde, el aviso sale por correo.

## Acciones y seguridad

- **RF10** – Genius solo puede ejecutar acciones que estén en una lista, cada una con su nivel de riesgo: lectura (sin aprobación), escritura de bajo riesgo como escalar o comentar (sin aprobación), escritura (necesita aprobación, RF11) y prohibida: borrar tablas o cambiar la estructura de la base. Una acción que no está en la lista se rechaza.
- **RF11** – Antes de ejecutar cualquier escritura, Genius muestra el comando exacto y espera que lo apruebe un SRE distinto del que lo pidió. Si nadie aprueba en 30 minutos, se cancela. DROP, TRUNCATE, ALTER y DELETE o UPDATE sin WHERE están bloqueados siempre, aunque alguien los apruebe. Lo que se muestra es exactamente lo que se ejecuta.
- **RF12** – Cada usuario solo puede hacer lo que su rol permite: soporte lee y escala; SRE lee y escribe con aprobación; el incident manager consulta incidentes, el tablero de SLA y la auditoría. El LLM nunca tiene una credencial de administrador.
- **RF13** – Las queries que pide el LLM son solo de lectura y corren sobre una copia de la base, con timeout de 10 segundos y máximo 1 000 filas. La respuesta dice qué query corrió, cuántas filas trajo, cuánto demoró y qué tan atrasada estaba la copia.
- **RF14** – Los E2E tests se corren en un ambiente aparte que nunca toca producción, y devuelven pasó/falló, cuántos y un link al log.
- **RF15** – Todo queda en auditoría: cada pregunta, respuesta, acción, aprobación y resultado, con usuario, hora e incidente. No se puede borrar ni editar. El incident manager puede ver la auditoría de un incidente sin pedírsela a ingeniería.
- **RF16** – Cualquier usuario puede marcar una respuesta como correcta o incorrecta y proponer la corrección. La corrección la revisa el SRE lead o el incident manager en máximo un día hábil; hasta entonces se ve como "propuesta" y no cambia nada. Cuando se aprueba, reemplaza la respuesta anterior.

## Confiabilidad

- **RF17** – Las preguntas al LLM van por una cola con prioridad: primero los P1, después los customer escalations, después los engineering escalations del on-call, después el resto. El usuario ve en qué posición está y cuánto le falta.
- **RF18** – Si el LLM no responde en 5 segundos (o el circuit breaker está abierto), Genius responde igual con el estado del incidente y la respuesta guardada si la hay, avisando que es una respuesta sin LLM. Además, el comando `/incident <id>` va directo a Incidentes Service sin pasar por el LLM ni por el resto de Genius, para poder ver el estado aunque Genius esté caído.
- **RF19** – Antes de mandar la pregunta al LLM se filtran instrucciones escondidas y datos sensibles. Después, la respuesta del LLM se revisa (que tenga la forma correcta, que sea texto o una acción válida) antes de ejecutar nada.
- **RF20** – Todos los días, y cada vez que cambie el modelo o el prompt, se corre una lista de preguntas comunes con respuesta esperada. Si acierta menos del 95 %, el cambio no se despliega.
- **RF21** – Hay un panel de salud con disponibilidad, reliability, P95, tamaño de la cola, errores por pieza, % de aciertos de las pruebas diarias y % de respuestas marcadas como correctas, con un semáforo: sano, degradado, no confiar. El incident manager lo ve sin pedírselo a nadie.

## Agregados después de la primera corrida del eval

- **RF22** – Para cada tipo de escalamiento (customer, engineering, support) existe una respuesta aprobada de "qué hacer ahora", con dueño. La pregunta "¿qué hago con este escalamiento?" devuelve siempre la misma.
- **RF23** – Si dos personas hacen la misma pregunta (aunque la escriban distinto) sobre el mismo incidente y nada cambió, reciben exactamente la misma respuesta. Si algo cambió (el estado o la fuente), la respuesta dice qué cambió.
- **RF24** – El incident manager tiene un tablero con todos los escalamientos abiertos ordenados por vencimiento, con horas restantes, tipo, owner y estado, sin tener que preguntar uno por uno.

## Agregado al revisar el harness con el esquema de clase

- **RF25** – El LLM trabaja con skills: guías paso a paso por tipo de tarea (investigar un incidente de pagos, armar una query de solo lectura, correr un E2E, escalar), escritas por ingeniería y con versión. Contexto Service carga la skill que corresponde a la pregunta junto con el estado, el conocimiento y el historial; el LLM sigue esos pasos y usa solo las acciones que la skill indica. Una skill nueva o cambiada entra en máximo 15 minutos y pasa por las pruebas diarias antes de usarse.

Cada requerimiento sale de una necesidad o un pain point de Diego, Valeria o Marco (ver `Personas/`). Qué pieza del harness cumple cada uno está en `HARNESS.md`.
