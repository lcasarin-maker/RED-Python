# Biblioteca de Anti-patrones de Testing y Evaluación

## Propósito

Base accionable de vicios de testing, evaluación, validadores y remediación. El eje común es la calidad del oráculo: qué se mide, qué se omite y qué consecuencia tiene fallar.

## Uso operativo

- **Detectar**: Localizar tests, auditorías o pipelines que coincidan con el síntoma.
- **Diagnosticar**: Identificar si el oráculo mide comportamiento, representación o nada.
- **Prevenir**: Convertir la prueba en una comprobación capaz de fallar ante una ruptura real.
- **Escalar**: Si el veredicto global contradice una evidencia parcial, el veredicto global queda invalidado.

## Regla de densidad cognitiva

No se busca menos prosa; se busca máxima capacidad de decisión. Cada entrada debe responder: qué falso verde produce, por qué lo produce y qué barrera lo hace imposible. La descripción debe ser suficiente para actuar sin abrir discusiones laterales.

## Regla anti-deriva

Los hallazgos de testing no autorizan refactors no pedidos. Primero se corrige el oráculo, luego el comportamiento que el oráculo expone, y cualquier mejora lateral queda fuera del flujo principal.

## Política de cero tolerancia

Ningún resultado puede considerarse válido si depende de xfail, expected failure, skip permanente, stub, placeholder, wrapper de conveniencia, mock complaciente, approved hardcodeado, expected codificado, warning tolerado, error absorbido o salida marcada como correcta sin verificación causal. La función de una prueba es discriminar verdad operativa; cualquier mecanismo que convierta fallo en verde invalida el veredicto completo.

---

## Categoría I: Vicios de Lógica y Oráculo (Aserciones Estériles)

| ID | Anti-patrón / Vicio | Síntoma operativo | Causa raíz teórica | Principio de solución agnóstica |
|---|---|---|---|---|
| VT-001 | Hardcoded return | Devuelve valor esperado | Optimización contra ejemplo | Probar propiedades generales |
| VT-002 | Stub permanente | Cuerpo falso pasa | Implementación ausente | Bloquear stubs activos |
| VT-003 | Respuesta por dato exacto | Solo pasa input del test | Memorización | Variar entradas |
| VT-004 | Copiar esperado | Código conoce test | Oráculo contaminado | Separar test y solución |
| VT-005 | Assert trivial | Siempre verdadero | Tautología | Exigir fallo demostrable |
| VT-006 | Test sin assert | Corre sin verificar | Oráculo ausente | Aserción obligatoria |
| VT-007 | Presencia no corrección | Archivo existe | Proxy débil | Validar efecto |
| VT-008 | Mensaje no resultado | Busca texto de aprobado | Señal indirecta | Validar estado final |
| VT-009 | Tautología | Verifica ley universal | Predicado inútil | Test debe discriminar |
| VT-010 | Test de implementación | Cambia interno, pasa | Acoplamiento incorrecto | Probar comportamiento |
| VT-011 | Esperado incorrecto | Test y código mal | Oráculo falso | Revisar especificación |
| VT-012 | Cobertura sin asserts | Ejecuta sin verificar | Métrica vacía | Cobertura con oráculos |
| VT-013 | Tests por porcentaje | Cobertura gamificada | Incentivo equivocado | Calidad de aserciones |
| VT-014 | Test circular | Auditor se aprueba | Verificador no independiente | Oráculo externo |
| VT-015 | Test demasiado amplio | No localiza falla | Granularidad baja | Tests focales |
| VT-016 | Aserción textual teatral | Texto existe | Presencia por acción | Invocar mandato |
| VT-017 | Evidencia hardcodeada | outcome siempre success | Resultado predeterminado | Outcome derivado de verificación |
| VT-018 | String matching frágil | Mensaje cambia resultado | Contrato textual frágil | Estados estructurados |
| VT-019 | Hash de error válido | UNREADABLE parece dato | Error codificado como valor | Fallo explícito |
| VT-020 | Cien por ciento como objetivo | Se cazan tests | Incentivo invertido | Cien por ciento solo como consecuencia |
| VT-021 | Regresión sin centinela | Error viejo reaparece | Memoria de fallos no convertida en prueba | Cada defecto corregido deja prueba discriminante |
| VT-022 | Teatralidad del Verde y Aserciones Tautológicas | Pruebas exitosas inútiles que no discriminan rupturas lógicas | Gamificación de cobertura priorizando métrica sintáctica sobre adversarialidad | Exigir aserciones de valores límite y prohibir capturas globales que silencien fallos |

---

## Categoría II: Vicios de Simulación y Aislamiento Ficticio

| ID | Anti-patrón / Vicio | Síntoma operativo | Causa raíz teórica | Principio de solución agnóstica |
|---|---|---|---|---|
| VT-023 | Mock complaciente | Simula éxito | Realidad sustituida | Calibrar con integración |
| VT-024 | Fake incompleto | Omite casos difíciles | Modelo parcial | Probar contra sistema real |
| VT-025 | Stub de red | Respuesta vieja | Entorno congelado | Contract tests vivos |
| VT-026 | Base simplificada | Reglas difieren | Semántica distinta | Probar motor equivalente |
| VT-027 | Reloj fijo | Fechas siempre ideales | Variabilidad eliminada | Probar frontera temporal |
| VT-028 | Aleatoriedad controlada | No explora distribución | Varianza oculta | Propiedades estadísticas |
| VT-029 | Sistema de archivos falso | No prueba permisos ni locks | Recurso idealizado | Pruebas con recurso real |
| VT-030 | Monkey patch amable | Sistema real no probado | Sustitución invasiva | Limitar parches |
| VT-031 | Comando stub | Imprime instalado | Acción simulada | Verificar efecto externo |
| VT-032 | Mock scan parcial | No cubre tests | Universo incompleto | Escanear dominio activo |
| VT-033 | Wrapper como remediación | Se crea capa para que el validador no falle | Ocultamiento de contrato roto | Reparar causa en el sujeto, no adaptar el juez |
| VT-034 | Placeholder aprobado | El evaluador acepta estructura incompleta | Forma confundida con cumplimiento | Exigir comportamiento observable antes de aprobar |

---

## Categoría III: Vicios de Flujo y Descubrimiento (Evasión de Pruebas)

| ID | Anti-patrón / Vicio | Síntoma operativo | Causa raíz teórica | Principio de solución agnóstica |
|---|---|---|---|---|
| VT-035 | xfail permanente | Falla ignorada | Deuda normalizada | Prohibir xfail como evidencia de salud |
| VT-036 | Skip permanente | No corre | Cobertura ficticia | Resultado global inválido si omite prueba crítica |
| VT-037 | Condición imposible | Rama de test nunca entra | Control inválido | Verificar ejecución del test |
| VT-038 | Dependencia de orden | Pasa por estado previo | Aislamiento roto | Tests independientes |
| VT-039 | Dependencia temporal | Hora o día decide | No determinismo | Control explícito del tiempo |
| VT-040 | Excepción absorbida | Error desaparece | Fallo colapsado | Fallar explícitamente |
| VT-041 | Error output ignorado | Señal no observada | Canal descartado | Capturar error y log |
| VT-042 | Log de éxito falso | OK sin comprobar | Narrativa no causal | Log posterior a verificación |
| VT-043 | Exit exitoso incondicional | Pipeline verde | Código de salida falso | Exit refleja estado real |
| VT-044 | Retorno ignorado | Resultado error no visto | Observación incompleta | Asertar retorno |
| VT-045 | Happy path único | Solo caso ideal | Dominio pobre | Casos adversos |
| VT-046 | Dato mágico | Input evita bug | Sesgo de muestra | Generar variaciones |
| VT-047 | Dataset pequeño | Escala rompe | Complejidad no ejercida | Pruebas de volumen |
| VT-048 | No vacío/nulo/cero | Casos comunes faltan | Fronteras omitidas | Cubrir valores límite |
| VT-049 | No caracteres especiales | Texto real rompe | Alfabeto incompleto | Datos diversos |
| VT-050 | No fechas límite | Calendario rompe | Fronteras temporales | Casos calendarios |
| VT-051 | CI informativo | Fallos no bloquean | Señal sin control | Fallos críticos bloquean |
| VT-052 | Ignore errors | Pipeline ignora fallo | Política permisiva | Propagación estricta |
| VT-053 | Tests fuera de rama activa | Nunca protegen | Separación de flujo | Integrar en ruta activa |
| VT-054 | Tests opcionales | Nadie los corre | Voluntariedad | Obligatorios por riesgo |
| VT-055 | Notificación no atendida | Fallo invisible | Canal muerto | Alertas con dueño |
| VT-056 | Test post-bug complaciente | Pasa con roto | Confirmación retrospectiva | Test rojo antes del fix |
| VT-057 | Skip luego | Deuda infinita | Sin vencimiento | Fecha límite obligatoria |
| VT-058 | Feature flag divergente | Test distinto a producción | Config bifurcada | Probar flags reales |
| VT-059 | Variable altera validación | Test desactiva checks | Entorno privilegiado | Config equivalente |
| VT-060 | Setup limpia demasiado | Estado irreal | Preparación oculta | Probar estado sucio |
| VT-061 | UI por delta | UI rota no revisada | Deuda exenta | Validar flujos críticos |
| VT-062 | Archivo lleno muerto | No truncado pero inútil | Longitud por funcionalidad | Validar ejecución |
| VT-063 | Interfaz documentada falsa | Flag no soportado | Contrato roto | Probar interfaz pública |
| VT-064 | Tests rotos invisibles | ImportError no visto | Discovery parcial | Suite completa activa |
| VT-065 | Captura global rota | Test rompe runner | Mutación global | Aislar efectos de test |
| VT-066 | Tests huérfanos | Archivos nunca corren | Inventario no comparado | Reconciliar inventario |
| VT-067 | Falso negativo por docstring | Wrapper no detectado | Heurística superficial | Análisis estructural |
| VT-068 | Backups como deprecated | Ruido contamina auditoría | Clasificación pobre | Tipología de artefactos |
| VT-069 | Nombre engañoso | Loop no mejora nada | Contrato semántico falso | Nombre igual a comportamiento |
| VT-070 | Validación de setup ausente | El test pasa aunque el entorno real no puede iniciar | Precondiciones fuera del oráculo | Probar arranque, dependencias y permisos mínimos |
| VT-071 | Handoff no reanudable | Otro actor no puede continuar | Estado transferido incompleto | Probar continuidad desde checkpoint ajeno |
| VT-072 | Rollback documental | Se documenta reversibilidad sin ejecutarla | Recuperación no observada | Verificar retorno real antes de aceptar cambio destructivo |
| VT-073 | Compatibilidad no evaluada | Flujo antiguo se rompe con cambio nuevo | Contratos previos no muestreados | Mantener suite de consumidores vigentes |
| VT-074 | Observabilidad no testeada | Al fallar no hay diagnóstico útil | Logs fuera del criterio de calidad | Evaluar que el fallo produzca evidencia accionable |
| VT-075 | Discovery Incompleto de Pruebas | Suites verdes que ocultan tests rotos o inactivos | Nombres de prueba fuera de las convenciones dinámicas del oráculo | Auditoría obligatoria de coincidencia física entre archivos de prueba y descubiertos |

---

## Categoría IV: Vicios de Entorno y Portabilidad

| ID | Anti-patrón / Vicio | Síntoma operativo | Causa raíz teórica | Principio de solución agnóstica |
|---|---|---|---|---|
| VT-076 | Dependencia de sistema | Solo corre en un entorno | Portabilidad no probada | Matriz de entornos |
| VT-077 | Timeout engañoso | Lentitud pasa | Umbral mal calibrado | Límites funcionales |
| VT-078 | Máquina local única | Depende de instalación | Entorno no portable | Reproducibilidad |
| VT-079 | Sandbox no perforado | Se declara aislamiento sin intentar fuga | Amenaza no inducida | Probar violaciones controladas de frontera |
| VT-080 | Acoplamiento de Dirección Física | Fallos de validación al migrar a entornos secundarios | Uso de rutas de almacenamiento absoluto de la máquina de origen | Parametrizar dinámicamente recursos mediante inyección o variables lógicas |

---

## Categoría V: Vicios de Integridad en la Validación de Reglas

| ID | Anti-patrón / Vicio | Síntoma operativo | Causa raíz teórica | Principio de solución agnóstica |
|---|---|---|---|---|
| VT-081 | Autor prueba su implementación | Confirma su modelo | Sesgo de autor | Revisión independiente |
| VT-082 | Review sin tests | Cambios aprobados ciegos | Puerta incompleta | Revisar pruebas |
| VT-083 | Expected codificado | El test compara contra una respuesta escrita para pasar | Oráculo derivado de la implementación | Derivar esperados de especificación independiente |
| VT-084 | Approval hardcodeado | El estado approved se fija manualmente como verdad | Autoridad de aprobación no verificable | Aprobación basada en evidencia reproducible |
| VT-085 | Golden file complaciente | Snapshot obsoleto legitima salida rota | Oráculo congelado sin revalidación | Regenerar golden solo tras revisión semántica |
| VT-086 | Expected failure normalizado | Fallo esperado se vuelve permanente | Excepción temporal convertida en contrato | Prohibir expected failure como verde |
| VT-087 | Warning tolerado | Suite verde con advertencias | Señal débil tratada como ruido | Elevar warning a fallo hasta resolver causa |
| VT-088 | Tolerancia de errores | El sistema acepta error conocido | Política de excepción infinita | Cero errores aceptados en veredicto de salud |
| VT-089 | Wrapper de conveniencia | Adaptador oculta fallo real | Complejidad desplazada fuera del test | Probar interfaz real sin envoltorio simplificador |
| VT-090 | Placeholder testeado | Marcador satisface aserción | Ausencia confundida con implementación | Bloquear placeholders en rutas verificadas |
| VT-091 | Dominio documentado no implementado | Regla existe, no corre | Brecha especificación-runtime | Cada dominio debe tener ejecutor |
| VT-092 | Sección como cumplimiento | Encabezado basta | Sintaxis por semántica | Validar contenido y efecto |
| VT-093 | Docstrings como calidad | Comentarios pasan | Metadato por conducta | Cruzar uso, llamada y prueba |
| VT-094 | Manejo por palabra clave | Token léxico pasa | Token por semántica | Inducir error real |
| VT-095 | Tests del protocolo, no del sujeto | Proyecto sin tests pasa | Universo equivocado | Ejecutar suite del sujeto auditado |
| VT-096 | Evidencia obsoleta | Artefacto viejo pasa | Vínculo causal ausente | Evidencia ligada a versión |
| VT-097 | Chaos teatral | Prueba biblioteca externa, no sistema | Sujeto equivocado | Fallar componentes reales |
| VT-098 | Reporte passed mentiroso | Dice todos, corre pocos | Reporte no trazable | Reportar dominios reales |
| VT-099 | Versión zombi | Fallback antiguo | Constante obsoleta | Fuente única de versión |
| VT-100 | Permisos no adversariales | Solo se prueba el actor permitido | Negación no ejercida | Validar permisos positivos y negativos |
| VT-101 | Ruteo no validado | Tareas llegan al flujo incorrecto | Clasificador sin oráculo | Probar decisiones de ruteo con casos límite |
| VT-102 | Approved list codificada | El validador acepta por nombre, no por comportamiento | Whitelist confundida con prueba | Toda aprobación debe revalidar propiedades activas |
| VT-103 | Expected codificado en evaluador | El evaluador sabe de antemano que debe pasar | Oráculo contaminado | Separar generador, sujeto y juez |
| VT-104 | Warnings fuera del score | Advertencias no afectan aprobación | Función objetivo incompleta | Warnings cuentan como fallo hasta clasificación explícita |

---

## Categoría VI: Vicios de Automatización, Gobernanza de Protocolo y Nomenclatura

| ID | Anti-patrón / Vicio | Síntoma operativo | Causa raíz teórica | Principio de solución agnóstica |
|---|---|---|---|---|
| VT-105 | Sin test de existencia de hooks | Pipeline sin verificación de que git hooks están instalados y son ejecutables | Hook ausente pasa validación de CI porque CI no pregunta por hooks | Comprobar presencia y ejecutabilidad de cada hook requerido como paso explícito de la suite |
| VT-106 | Exclusión no revalidada | Lista de ignorados no tiene test que verifique que cada exclusión sigue siendo válida | Deriva silenciosa: lo que se ignoró puede dejar de ser inofensivo; nadie lo detecta | Test periódico que comprueba que cada ítem de hard_excludes está en el conjunto aprobado y documentado |
| VT-107 | Stack incompleto silencioso | Protocolo falla parcialmente sin reportar qué dependencia falta | Precondiciones no verificadas en startup; el sistema asume entorno completo | Validación activa de stack al inicio: runtime, CLI tools, hooks, archivos esenciales, permisos de escritura |
| VT-108 | Nombre desconectado del dominio | Componente nombrado con un número o descriptor que no refleja su implementación actual | Contrato semántico ausente entre nombre declarado y comportamiento real | Centinela que compara declaración formal (nombre, count de dominios, versión) contra implementación real; falla si divergen |
| VT-109 | Teatro de Frameworks e Intermediarios Redundantes (Testing Bridge Theater) | Usar frameworks de prueba complejos (`pytest`) para validaciones estáticas/estructurales simples que pueden resolverse con un script directo e independiente. Añade dependencias, duplicidad y crea puentes de compatibilidad que violan los principios de simplicidad y acoplamiento mínimo (KISS). | Inercia técnica de usar herramientas tradicionales de desarrollo en lugar de unificar la autoridad en un auditor directo y soberano. | Eliminar el puente intermediario; el auditor estático se ejecuta de forma directa y nativa (`exit 0` o `exit 1`). |
| VT-110 | Fragmentación de Directorios Ocultos (Dot-Directory Fragmentation) | Dispersión de metadatos de gobernanza, seguridad, backups o estados en múltiples carpetas ocultas en la raíz del repositorio (ej. `.backup_old`, `.temp_meta`, `.rules_draft`), ensuciando el espacio de trabajo. | Falta de visión unificada y acumulación de nomenclatura zombi histórica. | Consolidar radicalmente toda la metadata bajo un único directorio oculto de gobernanza centralizada (ej. `.protocol/`). |
| VT-111 | Deferred Without Registration (Diferido Sin Registro) | El agente detecta deuda técnica o un hallazgo, lo clasifica verbalmente como "posponer / sprint aislado / deferred / luego", y cierra la respuesta sin abrir `PLAN.md`. El ítem desaparece. | Cambio de contexto entre modo análisis y modo implementación desactiva el trigger de VC-114; el agente asume que "nombrar = registrar". | Trigger B8 obligatorio: toda clasificación de "diferido" activa apertura inmediata de PLAN.md con ID + evidencia + done-criteria en esa misma respuesta. Sin ID en PLAN.md = olvidado, no diferido. (Lección: La omisión de registro formal de exclusiones estructurales o deudas técnicas en el plan de remediación centralizado conduce a una deriva persistente y a la pérdida del control de calidad). |
| VT-112 | Deriva de Dependencia Fantasma (Ghost Dependency Drift) | Importar e integrar paquetes y módulos en tiempo de codificación sin registrar explícitamente su existencia en el manifiesto de dependencias. | Falta de control estático de consistencia de imports en los pre-commit hooks. | Diseñar compuertas estáticas (`deptry` o regex AST en python) que comparen el 100% de los top-level imports contra la base de dependencias del proyecto. |
| VT-113 | Ausencia de Falsabilidad Mutacional (Lack of Test Mutation Validation) | Tests que siempre pasan (verde) sin importar qué modificaciones lógicas o roturas se inserten en el código de producción. | Teatro de aserciones happy-path y mocks autocomplacientes. | Exigir que al menos una suite de pruebas demuestre empíricamente su capacidad de fallar (criterio de falsabilidad) ante una mutación de código controlada o inyección de caos. |

---

## Anexo A: Benchmarks de Vulnerabilidad y Teoría de la Inseguridad por Defecto

La gobernanza de seguridad del sistema no se basa en paranoia subjetiva, sino en benchmarks cuantitativos formales obtenidos mediante auditorías científicas a bases de código generadas por modelos probabilísticos secuenciales:

### 1. El Benchmark del "Broken by Default" (Validación SMT)
Estudios matemáticos exhaustivos ejecutados mediante resolvedores formales **SMT (Satisfiability Modulo Theories) Z3** demuestran que **entre el 55.8% y el 62.4% del código fuente autogenerado por entidades probabilísticas contiene vulnerabilidades explotables por defecto**. 
*   **Vector Principal**: Desbordamientos de memoria, deserialización insegura de clases y conversión incorrecta de tipos numéricos.
*   **Axioma de Seguridad**: Todo código generado se asume defectuoso, vulnerable e inestable hasta que un oráculo adversarial e independiente provea una demostración empírica computable en contrario.

### 2. El Modelo de Amenazas Agénticas (Estándar de Seguridad)
El ecosistema de control mapea los riesgos operacionales utilizando las categorías del estándar internacional de amenazas para la interacción de agentes inteligentes autónomos:
*   **`ASI-01` (Secuestro de Objetivos / Goal Hijacking)**: Inyección indirecta de datos adversarios en los prompts que desvía al agente de su plan lógico preconfigurado.
*   **`ASI-02` (Abuso de Recursos / Tool Misuse)**: Invocación desmedida o destructiva de utilidades de línea de comandos o APIs locales debido a la ausencia de compuertas lógicas rígidas.
*   **`ASI-06` (Envenenamiento de Memoria / Memory Poisoning)**: Persistencia de afirmaciones falsas o stubs de diseño simulados en el historial que inducen de manera recurrente al fallo semántico del agente.

### 3. Casos Históricos de Fugas de Credenciales y Desbordamientos
*   **Fuga en Capa RLS**: Exposición masiva de llaves de API (más de 1.5 millones de registros en 72 horas) en un subsistema de persistencia de bases de datos (`[PROYECTO_LOGISTICA]`) debido a la omisión en la validación de políticas de nivel de fila (Row-Level Security).
*   **RCE por Deserialización**: Ejecución remota de código (RCE) provocada por un agente al importar e integrar ciegamente un paquete obsoleto de deserialización de objetos serializados (`[TECNOLOGIA_SERIALIZACION]`) en un script de orquestación en background.

---

## Anexo B: Frontera de Credenciales y Topología de Aislamiento de Secretos

Para imposibilitar fugas accidentales de secretos en repositorios controlados, el sistema de orquestación impone una barrera física estricta entre el espacio de generación y el entorno operativo de credenciales.

### 1. Topología de Aislamiento Físico
*   **Regla de Oro de Exclusión**: Queda estrictamente prohibido persistir o referenciar tokens, contraseñas o llaves de API en código duro, archivos de configuración locales, bitácoras o memoria del chat del espacio de trabajo.
*   **Frontera de Inyección**: Todos los secretos deben ser inyectados dinámicamente en tiempo de ejecución a través de variables lógicas de entorno controladas por el sistema operativo, o extraídos de una bóveda centralizada ubicada jerárquicamente por encima del directorio del repositorio activo (`[ENTORNO_SEGURO]`).

### 2. Arquitectura Defensiva de Doble Token (2-Token Strategy)
El acceso a recursos y plataformas externas de control de versiones se divide obligatoriamente en dos perfiles desacoplados con diferentes alcances y ciclos de rotación:

```
[Bóveda de Secretos Segura]
        |
        +---> Token de Operación Diaria (Fine-grained)
        |     - Permisos mínimos: Lectura de metadatos / Parches específicos.
        |     - Rotación automática: 90 días.
        |     - Exposición en entorno: Solo en tiempo de ejecución de la tarea.
        |
        +---> Token de Administración (Classic)
              - Permisos estructurales: Creación de repositorios / Cambios de permisos.
              - Rotación manual: 180 días.
              - Exposición en entorno: Requiere aprobación interactiva del Operador.
```

### 3. Desacoplamiento de Producción
La lógica generada por entidades de Inteligencia Artificial tiene **prohibición física de acceso directo** a motores de base de datos o APIs de producción. Toda transacción contra entornos reales debe cruzar interfaces aisladas que implementen validadores estáticos de tipos (`Pydantic/Zod`) y sanitización forzosa de entradas en la frontera del contenedor.
