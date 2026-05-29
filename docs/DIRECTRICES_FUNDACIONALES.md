# DIRECTRICES_FUNDACIONALES.md — Requisitos del Operador Luis Casarin
**Estado:** INMUTABLE | **Fuente:** deprecated/docs/Directrices.md | **Rescatado:** 2026-05-24

Estas son las 20 directrices fundacionales del sistema. Todo protocolo, todo script, todo test debe ser evaluado contra esta lista. Son la voluntad del operador, no sugerencias.

---

## LAS 20 DIRECTRICES

1. No soy programador, soy abogado. El protocolo no puede asumir formacion tecnica.
2. El objetivo es vibe coding evitando los problemas comunes (deriva, teatro, tokens).
3. Uso varios agentes a la vez. El agotamiento de tokens es un problema operacional critico.
4. La deriva es un problema grave. Los agentes quieren alejarse del plan, hacer side-quests y distraer con sugerencias aparentemente utiles que no atacan el problema directo.
5. Revision siempre a fondo. La forma importa pero no es la meta. Los tests deben ser implacables respecto del fondo.
6. Si un proyecto no nace dentro del protocolo, se debe hacer auditoria adversarial de codigo: todos los archivos, HTML, scripts, todos lados.
7. El protocolo es el cerebro rector de TODOS los proyectos. No me voy a convertir en programador por magia.
8. El protocolo debe afectar con autoridad a cualquier agente: Claude, Codex, ChatGPT, Gemini.
9. Cuando cambie el protocolo, el cambio debe propagarse automaticamente a todos los agentes en todos los proyectos.
10. El protocolo es el sistema operativo de todos los proyectos. Cambio aqui = cambio en todos. Descubrimiento en proyecto = propagacion al protocolo general.
11. Los permisos de los agentes deben ser los necesarios para operar, pero no tan amplios que puedan destruir.
12. El sistema debe ser 100% operativo, no aspiracional.
13. El agente debe escoger el modelo correcto para la tarea y sugerirlo o cambiarlo automaticamente.
14. Escoger siempre el modelo minimo necesario para cuidar tokens.
15. Implementar estrategias de ahorro de tokens de forma automatizada.
16. Hacer auditorias periodicas contra estas directrices para evitar deriva automaticamente.
17. Hacer auditoria periodica contra deprecated para evitar perdida de funciones o regresiones.
18. Debe haber candados y bloqueos claros para evitar destruccion o regresion.
19. Se pide 100% de pass pero no como meta: el 100 se gana con validacion real del codigo, es consecuencia no objetivo. No se disenan tests para que pasen — se disenan tests con base en funciones deseadas.
20. Los tests van antes del codigo y con base en comportamiento deseado.

---

## ERRORES DEL PROTOCOLO A CORREGIR

Los siguientes son errores diagnosticados por el operador que el protocolo debe resolver:

- **"Auditar forma no fondo":** El auditor actual valida la existencia de archivos y textos, no que el codigo funcione. Fix: tests behaviorales.
- **"No hay mecanismo para detectar regresiones entre versiones":** No existe comparacion entre version actual y anterior. Fix: hash-based regression detection en CI.
- **"Si hay bloqueador, darle la vuelta en lugar de resolver":** Politica incorrecta. Un bloqueador debe resolverse, no workaroundearse y dejarse en historial. Fix: ESCALATION_PROTOCOL.md debe exigir resolucion, no bypass.
- **"Privilegia deprecar sobre arreglar":** Cuando algo falla, el protocolo tiende a mover el archivo a deprecated en lugar de arreglar el problema. Fix: regla explicita "fix before deprecate".

---

## EVALUACION DE CUMPLIMIENTO

Antes de cada sesion, el agente debe responderse internamente:

| Directriz | Cumplida | Evidencia |
|-----------|----------|-----------|
| D5 (fondo, no forma) | ? | Tests behaviorales existentes |
| D13/D14 (modelo minimo) | ? | Modelo actual declarado |
| D16 (auditoria vs directrices) | ? | Ultima auditoria vs este archivo |
| D19 (100% ganado, no forzado) | ? | Tests escritos antes de codigo |

---

**Antipatron prohibido:** Declarar "cumplimiento con directrices" sin ejecutar la tabla de arriba.
