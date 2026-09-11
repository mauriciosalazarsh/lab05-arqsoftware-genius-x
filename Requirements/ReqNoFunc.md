# Requerimientos No Funcionales

- **RNF01** – Carga: 10 000 incidentes por semana y picos de 3× en la primera semana del mes, sin pasarse de los tiempos de RNF03. Antes de cada release se hace una prueba de carga a 3× con 100 usuarios a la vez, con máximo 1 % de timeouts en las queries.
- **RNF02** – 100 ingenieros usando Genius al mismo tiempo.
- **RNF03** – Tiempos de respuesta: consultar el estado (sin LLM) menos de 1 segundo en P95; una respuesta con LLM menos de 5 segundos en P95; una query o un E2E test menos de 10 segundos en P95.
- **RNF04** – Disponibilidad de 99,9 % para consultas de estado y acciones de lectura (contando la respuesta sin LLM) y 99,5 % para las respuestas con LLM. Se mide como Availability = 2xx / (2xx + 5xx).
- **RNF05** – Sin SPOF: cada pieza del camino crítico tiene por lo menos dos copias; el LLM tiene dos o más copias con balanceador y health checks; la base principal tiene réplica síncrona y cambia sola si se cae. Se prueba apagando una copia de cualquier pieza: la consulta de estado sigue respondiendo en menos de 1 segundo.
- **RNF06** – Toda llamada al LLM, a la base, a Slack o a una acción tiene timeout, reintentos cada vez más espaciados y circuit breaker. Las consultas y las acciones usan colas separadas, para que un pico de una no frene a la otra.
- **RNF07** – Recuperación en menos de 5 minutos (RTO) y sin perder nada de incidentes, aprobaciones, auditoría ni historial (RPO 0). Backups diarios y una restauración de prueba cada mes.
- **RNF08** – El estado que se muestra tiene como máximo 30 segundos de atraso respecto al cambio real.
- **RNF09** – El LLM genera sin aleatoriedad (temperatura 0); las respuestas aprobadas y las repetidas se sirven desde las respuestas guardadas; las pruebas diarias tienen que dar al menos 99 % de consistencia.
- **RNF10** – La base de conocimiento se actualiza en menos de 15 minutos cuando algo cambia; los incidentes cerrados entran al cerrarse.
- **RNF11** – Mínimo privilegio: el LLM nunca tiene credencial de administrador y cada acción corre con el rol del usuario. Borrar tablas o cambiar la estructura está bloqueado siempre; las escrituras, solo con aprobación de otro SRE. El LLM es local: ningún dato sale de la red.
- **RNF12** – El 100 % de las interacciones y acciones queda en auditoría por incidente, en un registro donde solo se agrega y nunca se borra, por 1 año.
- **RNF13** – Los services no guardan estado y se copian solos cuando la cola crece; el LLM siempre tiene una copia más de la necesaria. Todos tienen health endpoint; se mide Availability y Reliability = 2xx / (2xx + 4xx + 5xx) por endpoint; si se abre el circuit breaker hacia el LLM, avisa al incident manager y al on-call.
