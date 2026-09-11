# Diego Ramos — Ingeniero de soporte (nivel 2)

## Perfil

- **Edad:** 29 años
- **Rol:** Ingeniero de soporte N2. Procesa los customer escalations antes de pasarlos a ingeniería y los responde al cliente.
- **Contexto:** 20 a 40 escalamientos por día; el doble en la primera semana del mes. Vive en Slack y usa Genius para todo: estado de incidentes, pasos siguientes, queries simples.
- **Nivel tecnológico:** Medio. Sabe SQL básico; no toca producción.

## Necesidades

- **N1:** Saber el estado actual y real de un incidente (abierto/cerrado, owner, último cambio) en segundos, para responder al cliente.
- **N2:** Obtener los pasos siguientes (runbook) para un tipo de escalamiento y recibir la misma respuesta cada vez que pregunta lo mismo.
- **N3:** Escalar a ingeniería con todo el contexto ya armado (resumen, queries hechas, impacto) y con el SLA de 1 día visible.
- **N4:** Que Genius no pueda ejecutar nada peligroso a partir de una instrucción suya mal escrita.

## Pain Points

- **P1:** "Le dije a Genius 'limpia los registros duplicados del cliente' y borró la base de datos. Ahora tengo miedo de escribirle cualquier cosa."
- **P2:** "Le pregunto por el INC-4471 y me dice que sigue abierto; el cliente me responde que ingeniería lo cerró hace tres horas."
- **P3:** "La primera semana del mes Genius no responde o responde cualquier cosa, justo cuando tengo el doble de escalamientos."
- **P4:** "Pregunto lo mismo que ayer y hoy me da otra respuesta; no sé cuál mandarle al cliente."
- **P5:** "Genius no aprende: le corregí lo mismo diez veces y sigue respondiendo con data vieja."

*Para Diego, Genius funciona si en un pico de mes pregunta por un incidente y en menos de dos segundos recibe el estado real, con fecha y fuente, y si cualquier cosa que pueda romper algo le pide confirmación antes.*
