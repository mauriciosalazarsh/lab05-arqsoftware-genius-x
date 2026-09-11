# E — Estimar

Supuestos declarados; se ajustan con datos reales de Genius cuando existan.

## Entradas

| Dato | Valor | Origen |
|---|---|---|
| Incidentes | 10 000 / semana; pico 3× en la primera semana del mes | Enunciado |
| Ingenieros | 50–100; se estima 100 concurrentes | Enunciado |
| Interacciones con Genius por incidente | 5 (estado, pasos, query, escalamiento, cierre) | Supuesto |
| Horas activas | 10 h por día hábil, 5 días | Supuesto |
| Tokens por llamada al LLM | 2 000 de entrada (estado + conocimiento + historial) · 300 de salida | Supuesto |
| Preguntas resueltas sin LLM (respuestas guardadas, estado directo) | 60 % | Supuesto (meta del harness) |

## Requests por segundo

- Semana normal: 10 000 × 5 = 50 000 interacciones → 10 000 / día → 10 000 / 36 000 s ≈ **0,3 RPS** promedio.
- Semana pico: 150 000 → 30 000 / día → **0,8 RPS** promedio; ráfagas ×10 → **8 RPS**.
- Techo por concurrencia: 100 ingenieros → como máximo **100 solicitudes en vuelo**.
- Al LLM llega el 40 %: **3,3 RPS** en ráfaga pico.

## Capacidad del LLM (local)

- Por llamada: 2 000 tokens de entrada + 300 de salida.
- En ráfaga pico: 3,3 × 2 000 = 6 600 tokens/s de entrada; 3,3 × 300 = **1 000 tokens/s de salida**.
- Una GPU atendiendo varias preguntas a la vez (modelo de 7–8B) rinde ≈ 1 500 tokens/s de salida y > 10 000 de entrada → **1 GPU al ~70 % en ráfaga pico**.
- Tiempo por respuesta: 300 tokens a ~60 tokens/s ≈ 5 s → cumple P95 < 5 s solo si la cola es corta; por eso el 60 % de las preguntas debe resolverse sin LLM.
- **Copias del LLM: 2** en semana normal (una de más, por si una se cae); **3** en la primera semana del mes.

## Servidores del harness

- Un core maneja ≈ 5 req/s de lógica (sin LLM) → servidor de 8 cores ≈ 40 RPS.
- Pico 8 RPS → **1 servidor**; sin SPOF → **2 copias** de cada service y **2 procesos** atendiendo la cola.

## Almacenamiento (por año)

| Tipo | Cálculo | Total |
|---|---|---|
| Incidentes | 520 000 × 5 KB | 2,6 GB |
| Auditoría (interacciones + tool calls) | 2,6 M × 10 KB | 26 GB |
| Historial por incidente | 520 000 × 50 KB, guardado 90 días | ≈ 6,5 GB en línea |
| Base de Conocimiento (texto + índice de búsqueda) | 100 000 fragmentos × 7 KB | 0,7 GB |
| Logs de E2E tests | 50 000 × 200 KB | 10 GB |
| **Total** | | **≈ 46 GB / año** |

Base pequeña: una instancia SQL con réplica síncrona basta; el costo está en el LLM, no en el almacenamiento.

## Ancho de banda

- Entrada: 2,6 M interacciones × 5 KB = 13 GB / año → despreciable.
- Salida: 2,6 M × 20 KB = 52 GB / año → **≈ 0,2 MB/s** en ráfaga pico. Todo texto; sin restricción.

## Conclusión

El cuello de botella es el **LLM** en la primera semana del mes (≈ 1 000 tokens/s de salida). Se resuelve con: Respuestas Guardadas (−60 % de llamadas), Cola de Preguntas con urgentes primero, 3 copias del LLM en el pico y respuesta sin LLM cuando no contesta. El resto del harness cabe en 2 servidores pequeños.
