# Biblioteca de Tokenomics y Gestión de Contexto

## Propósito

Base accionable de tokenomics y gestión de contexto. El ahorro de tokens se trata como control de calidad: menos ruido reduce deriva, olvido y falsos positivos.

## Uso operativo

- **Detectar**: Ubicar fugas de contexto, salida o exploración.
- **Diagnosticar**: Distinguir si el costo viene de entrada, salida, herramientas, relectura, reversión o mala ruta de trabajo.
- **Prevenir**: Aplicar poda, compactación, caching, routing o medición según el patrón.
- **Escalar**: Si el contexto amenaza continuidad, precisión o cierre verificable, exigir checkpoint antes de continuar.

## Regla de densidad cognitiva

No se busca menos prosa; se busca máxima relación señal/ruido. Cada entrada debe indicar qué se desperdicia, por qué se desperdicia y qué control reduce el desperdicio sin perder información crítica. La meta es preservar razonamiento, no solo bajar conteo.

## Regla anti-deriva

La optimización de tokens no debe convertirse en proyecto paralelo. Solo se aplica cuando reduce ruido, mantiene continuidad o evita colapso de contexto en el objetivo actual.

---

## Fugas Críticas Documentadas

| ID | Fuga | Síntoma operativo | Causa raíz teórica | Principio de solución agnóstica |
|---|---|---|---|---|
| TK-F01 | Reprocesamiento de contexto estable | El mismo bloque se paga o procesa muchas veces | Reuso no modelado | Separar contexto estable y contexto volatil |
| TK-F02 | Poda contextual primitiva | Tareas pequeñas cargan documentos completos | Recuperacion no selectiva | Extraer solo fragmentos relevantes |
| TK-F03 | Salida verbal excesiva | Preámbulos, explicaciones y cierres no agregan valor | Presupuesto de salida ausente | Restringir formato y longitud de salida |

---

## Categoría I: Gobernanza y Persistencia de Memoria

| ID | Anti-patrón / Vicio | Síntoma operativo | Causa raíz teórica | Principio de solución agnóstica |
|---|---|---|---|---|
| TK-001 | Checkpoint ausente | Nueva sesión reinicia todo | Estado efímero | Cerrar con resumen físico o lógico |
| TK-002 | Memoria de chat como fuente principal | Cambiar hilo pierde estado | Persistencia no externa | Mantener estado fuera del chat |
| TK-003 | Cambio de proyecto sin cierre | Contextos se contaminan | Frontera de tarea difusa | Checkpoint antes de cambiar objetivo |
| TK-004 | Setup reexplicado | Cada sesión consume tokens reconstruyendo entorno | Precondiciones no externalizadas | Mantener ficha mínima de arranque y salud |
| TK-005 | Handoff prose-heavy | Continuidad requiere leer historia completa | Estado no normalizado | Handoff atómico: objetivo, estado, evidencia, riesgos, siguiente acción |
| TK-006 | Merge manual de historial | Resolver conflicto consume contexto excesivo | Memoria no semántica | Fusionar por decisiones e invariantes, no por texto bruto |
| TK-007 | Fuente de verdad duplicada | Se releen copias contradictorias | Estado canónico no definido | Consultar un núcleo canónico y archivar copias como evidencia |
| TK-008 | Segregación Epistemológica de la Memoria | Reprocesamiento redundante de especificaciones estables | Confusión entre invariantes lógicas y variables de sesión | Separar directrices en Núcleo Inmutable y compactar el Búfer Transicional |

---

## Categoría II: Ingesta y Poda de Entrada

| ID | Anti-patrón / Vicio | Síntoma operativo | Causa raíz teórica | Principio de solución agnóstica |
|---|---|---|---|---|
| TK-009 | Poda semántica | Archivos completos saturan el prompt | Recuperación por documento, no por necesidad | Extraer secciones relevantes |
| TK-010 | Recuperación contextual | Fragmentos pierden significado | Chunks sin contexto padre | Enriquecer fragmentos con contexto mínimo |
| TK-011 | Delimitadores estructurados | Instrucciones se mezclan | Fronteras ambiguas | Separar rol, contexto, tarea y salida |
| TK-012 | Exploration tax | Muchos tokens antes de actuar | Exploración ciega | Usar índices, mapas y lectura dirigida |
| TK-013 | Tool schemas inflados | Herramientas no usadas consumen contexto | Carga anticipada excesiva | Carga de herramientas diferida |
| TK-014 | Lectura completa por defecto | Archivo grande enviado entero | Granularidad baja | Leer por rangos, índice o esqueleto |
| TK-015 | Archivo completo para duda puntual | El agente procesa información irrelevante | Consulta no localizada | Pedir sección exacta |
| TK-016 | Prompt gigante multiobjetivo | Modelo reparte atención | Sobrecarga de objetivos | Una tarea concreta por ciclo |
| TK-017 | Permisos narrados | Políticas largas se repiten en prompts | Autorización no estructurada | Representar permisos como matriz consultable |
| TK-018 | Backlog mezclado con objetivo | Ideas laterales ocupan ventana activa | Priorización no separada | Enviar side findings a cola externa |
| TK-019 | Esqueleto Jerárquico de Dependencias | Alto consumo en exploración ciega de directorios o archivos extensos | Baja granularidad de lectura y falta de mapas contextuales previos | Utilizar índices semánticos y skeletons para direccionar consultas quirúrgicas |

---

## Categoría III: Control y Compresión de la Salida

| ID | Anti-patrón / Vicio | Síntoma operativo | Causa raíz teórica | Principio de solución agnóstica |
|---|---|---|---|---|
| TK-020 | Restricción de salida | Respuestas largas por defecto | Espacio de salida no acotado | Definir presupuesto y formato |
| TK-021 | Prefilling | Formato variable | Distribución de salida amplia | Predefinir inicio y estructura |
| TK-022 | Optimización de ejemplos | Few-shot redundante | Repetición innecesaria | Usar ejemplos mínimos, diversos y densos |
| TK-023 | Logs crudos | Salida de comandos satura contexto | Ruido operacional | Comprimir o filtrar antes de entregar al agente |
| TK-024 | Resumen sin densidad | Compactación pierde decisiones | Compresión sin invariantes | Preservar hechos críticos, decisiones y próximos pasos |
| TK-025 | Salida de auditoría verbosa | El hallazgo se pierde entre ruido | Baja densidad informativa | Reportar hallazgos, evidencia y acción |
| TK-026 | Observabilidad ruidosa | Logs extensos desplazan el problema | Señal no jerarquizada | Registrar resumen causal y retener detalle bajo demanda |
| TK-027 | Compresión Léxica de Diagnósticos | Pérdida de contexto por trazas de error verbosas y repetitivas | Truncamiento ciego del historial por rebasar límites físicos | Aplicar filtros de redundancia léxica (elisión controlada) a trazas del entorno de ejecución |

---

## Categoría IV: FinOps y Eficiencia Operativa

| ID | Anti-patrón / Vicio | Síntoma operativo | Causa raíz teórica | Principio de solución agnóstica |
|---|---|---|---|---|
| TK-028 | Caching de contexto estable | Reprocesamiento recurrente | Memoria estable no separada | Marcar bloques reutilizables y evitar recarga |
| TK-029 | Procesamiento batch | Tareas diferibles se ejecutan una a una | Falta de agrupación | Agrupar trabajo no interactivo |
| TK-030 | Cascada de capacidades | Se usa capacidad máxima para todo | Asignación ineficiente de recursos | Elegir capacidad mínima suficiente |
| TK-031 | Compactación de contexto | Sesión larga se degrada | Ventana finita saturada | Resumir estado y reiniciar con continuidad |
| TK-032 | Cache cliff | Pausas invalidan beneficio de caché | TTL ignorado | Gestionar reanudación y checkpoints |
| TK-033 | Sin headroom | Contexto colapsa silenciosamente | Margen no reservado | Mantener presupuesto con zona de seguridad |
| TK-034 | Costo de reversión invisible | Loops de fix/revert consumen sesión | Retrabajo no medido | Registrar costo de rollback |
| TK-035 | Pensar con herramienta de ejecución | Contexto caro se usa para decidir | Routing incorrecto | Separar pensar, ejecutar y revisar |
| TK-036 | Respuesta sin modo | El agente no sabe si pensar o ejecutar | Intención no clasificada | Enrutar por fase: pensar, ejecutar, revisar |
| TK-037 | Monitoreo manual olvidable | Usuario cuenta mensajes | Control humano frágil | Umbrales visibles y automatizables |
| TK-038 | Relectura de estado completo | Cada turno arrastra todo | Estado no indexado | Mantener campos pequeños de estado |
| TK-039 | Herramientas externas no integradas | Estrategias existen pero no operan | Script espectral | Cada optimización debe estar en ruta activa |
| TK-040 | Ahorro prometido no medido | Se declara reducción sin telemetría | Métrica ausente | Medir antes y después |
| TK-041 | Cuotas invisibles | La sesión se corta por límites no presupuestados | Recurso externo no contabilizado | Incluir límites, backoff y degradación en el plan |
| TK-042 | Manifiestos sin restricción de tamaño | Archivos de gobernanza (AGENT.md, STATUS.md, SPEC.md) crecen sin control, saturando la ventana de contexto en cada sesión | Ausencia de umbrales físicos definidos y auditados para los documentos core de la Trinity | Definir y hacer cumplir límites de líneas en cada manifiesto (ej. AGENT.md ≤ 150 líneas per Trinity); auditarlos como compuerta de commit en el validador de gobernanza |

---

## Principios Positivos Consolidados

| ID | Principio | Directiva agnóstica |
|---|---|---|
| TK-P01 | Contexto mínimo suficiente | Incluir solo información necesaria para la decisión actual |
| TK-P02 | Estado externo al chat | Registrar estado estable en artefacto persistente |
| TK-P03 | Separación de fases | Pensar, ejecutar y revisar no consumen el mismo tipo de contexto |
| TK-P04 | Presupuesto visible | Todo ciclo debe saber cuánto contexto queda y qué riesgo implica |
| TK-P05 | Compresión con invariantes | Resumir sin perder decisiones, bloqueadores, evidencia ni próximo paso |
| TK-P06 | Medición antes de optimizar | Ningún ahorro se considera real sin comparación empírica |
| TK-P07 | Poda antes de razonamiento | Reducir ruido antes de pedir inferencia |
| TK-P08 | Cierre limpio | Cada sesión termina dejando contexto reanudable |
| TK-P09 | Rutas activas | Estrategia no integrada es documentación, no capacidad |
| TK-P10 | Tokenomics como calidad | Menos ruido mejora costo, precisión y mantenibilidad |
| TK-P11 | Trazabilidad compacta | La fuente original se conserva, pero el trabajo diario usa índices densos |

---

## Anexo A: Arquitectura de Persistencia Local (La Trinidad de la Memoria)

El búfer de atención (contexto activo) de los modelos basados en Transformer es intrínsecamente finito y propenso a la entropía lógica a largo plazo. Por ende, **el historial de chat de la conversación no debe tratarse nunca como la fuente de verdad del estado de un proyecto**. El entorno impone obligatoriamente un esquema de persistencia física en tres archivos desacoplados:

### 1. El Núcleo Inmutable (`AGENT.md` / Gobernanza Permanente)
*   **Propósito**: Gobernar el comportamiento, tono, estilo, restricciones y reglas de seguridad del agente de manera persistente.
*   **Restricción de Tamaño**: Mantenerse estrictamente por debajo de **150 líneas** para evitar que se convierta en una fuga de tokens fija de alto costo en cada interacción.
*   **Contenido**: Identidad del orquestador, directivas de traducción semántica, reglas de caja negra y prohibiciones destructivas críticas.

### 2. El Delta Activo (`STATUS.md` / Ledger de Estado de Corto Plazo)
*   **Propósito**: Persistir el estado exacto del sistema en el filesystem local, liberando al agente de la necesidad de releer el historial de la conversación anterior para reconstruir el contexto del trabajo.
*   **Restricción de Estructura**: Actualizado de forma obligatoria al final de cada sesión. Contiene exclusivamente:
    1.  *Estado actual*: Hitos y subsistemas validados físicamente.
    2.  *Cambios recientes*: Deltas aplicados en la sesión actual.
    3.  *Siguiente paso exacto*: Instrucciones atómicas y específicas para el próximo agente.
    4.  *Bloqueadores*: Anomalías activas no resueltas.

### 3. El Búfer Interactivo (`PROMPTS_RAPIDOS.md` / Plantillas de Ejecución)
*   **Propósito**: Contener los delimitadores estructurados y esquemas XML para guiar las consultas quirúrgicas complejas del operador.
*   **Contenido**: Casos de pocos ejemplos (*few-shot*), configuraciones de delimitación rígida de instrucciones y comandos estándar parametrizados.

---

## Anexo B: Algoritmo de Compresión por Elisión Léxica y Control Plane

El Control Plane actúa como la única autoridad lógica del sistema. Su función es canalizar las operaciones de validación, auditoría de integridad y control de versiones a través de una API conceptual abstracta, integrando filtros automáticos de tokenomics antes de transferir datos al búfer del orquestador.

### 1. Algoritmo Conceptual de Compresión por Elisión Léxica
Para neutralizar la fuga de tokens provocada por diagnósticos extensos de compilación, ejecución o análisis estático, el canal de observabilidad debe instrumentar el siguiente flujo de procesamiento léxico:

```
[Diagnóstico de Entrada Verboso] (Trazas, logs, diffs crudos)
               |
               v
  {Filtro 1: Límite de Longitud de Línea}
  -> Trunca líneas >120 caracteres aplicando bandera de elisión ("...").
               |
               v
  {Filtro 2: Colapso de Redundancia Léxica}
  -> Detecta repeticiones secuenciales de cadenas idénticas de error.
  -> Reemplaza N líneas repetidas por un resumen agregador: "[Repetición xN: [Mensaje]]".
               |
               v
  {Filtro 3: Extracción Causal Estricta}
  -> Elimina avisos no críticos (warnings) y encabezados de estilo.
  -> Conserva exclusivamente el delta de fallo (stack trace de origen + error de tipo).
               |
               v
[Payload de Salida Sanitizado] (Densidad cognitiva >40% de ahorro en tokens)
```

### 2. Orquestación del Control Plane
Toda transacción que altere el estado físico de los archivos debe ser invocada a través del router del Control Plane, ejecutando tres compuertas secuenciales:
1.  `check` (Auditoría Forense): Escanea las dimensiones lógicas de validación estructural contra el manifiesto de especificación y genera alertas preventivas si el volumen de mensajes del chat excede el umbral de seguridad de 20 interacciones.
2.  `sync` (Detección de Cambios de Gobernanza): Valida la integridad del protocolo mediante sumas de comprobación SHA256 de los archivos core. Si detecta desviaciones en los metadatos de gobernanza, bloquea la ejecución.
3.  `evidence` (Ledger de Evidencia JSON): Registra de forma inmutable y cronológica en disco un rastro de auditoría bajo el siguiente esquema persistente:

```json
{
  "timestamp": "ISO-8601-UTC-DATETIME",
  "agent_capability_tier": "TRUSTED | ISOLATED | AUDIT",
  "action_invoked": "STRING",
  "verification_outcome": "APPROVED | BLOCKED | REPLAN",
  "affected_deltas": ["FILE_PATH_1", "FILE_PATH_2"]
}
```
El éxito del sistema no se valida por su estética visual, sino por la consistencia demostrable de este ledger de evidencias transaccionales.
