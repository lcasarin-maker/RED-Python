# Sprint 3.4 — Triage Catch-Alls de Circularidad

**Fecha:** 2026-05-31 | **Auditor:** CoderCerberus v0.3
**Alcance:** 119 VC (test_behavioral_compliance) + 42 TK (test_d10_tokenomics) = 161 IDs

**Metodología (B1):** Definición leída de golden_standard.yaml. STATIC-TESTABLE solo si check
AST/regex genérico detecta el vicio sin juicio semántico. Postura CONSERVADORA: la duda va DOC-ONLY.

---

## Resumen global

| Categoría | STATIC-TESTABLE | DOC-ONLY | STALE | Total |
|---|---|---|---|---|
| VC (test_behavioral_compliance) | 5 | 114 | 0 | 119 |
| TK (test_d10_tokenomics) | 2 | 39 | 1 | 42 |
| **TOTAL** | **7** | **153** | **1** | **161** |

**STATIC-TESTABLE (7):** VC-082, VC-109, VC-121, VC-122, VC-123, TK-005, TK-018
**STALE (1):** TK-043 ya tiene def real (audit_script_orphans) — remover del baseline

Cobertura honesta post-Sprint 3.4: ~12% PREVENTED real, ~88% DOC-ONLY declarado.

---

## Plan implementación (Partes B y C)

### Parte B — Tests failing-first para STATIC-TESTABLE

| ID | def | Descripción |
|---|---|---|
| VC-082 | test_vc082_ghost_import_detected | import fantasma vs pyproject.toml |
| VC-109 | test_vc109_absolute_path_in_scripts | rutas absolutas en scripts/ (extensión D9) |
| VC-121 | test_vc121_duplicate_function_names | funciones con nombre idéntico en módulos distintos |
| VC-122 | test_vc122_no_pip_install_in_scripts | subprocess pip install en scripts |
| VC-123 | test_vc123_no_git_add_all_in_scripts | git add -A / git add . en scripts |
| TK-005 | test_tk005_status_md_has_required_sections | STATUS.md sin secciones estructuradas |
| TK-018 | test_tk018_external_backlog_exists | review_queue.json ausente |

### Parte C — DOC-ONLY en generate_golden_audit.py

1. Fallbacks VC→test_behavioral_compliance y TK→test_d10_tokenomics se cambian a
   validating_mechanism="DOC_ONLY", status="DOC_ONLY".
2. El ratchet excluye IDs con validating_mechanism=="DOC_ONLY" de _current_circular().
3. El baseline se vacía de estos 161 IDs.

---

## SECCIÓN 1A: VC-001..VC-050 (DOC-ONLY salvo VC-082)

DO = DOC-ONLY (conductual/semántico, no falsable AST genérico)

VC-001 DO: adversarialidad epistemológica conductual
VC-002 DO: seguridad injustificada semántico
VC-004 DO: muestreo insuficiente conductual
VC-005 DO: "temporal" requiere juicio
VC-006 DO: UI/docs vs fallos — juicio humano
VC-007 DO: "lógica crítica" semántico
VC-008 DO: ignorar regresiones conductual
VC-009 DO: sesgo contextual del agente conductual
VC-010 DO: requiere historia de sesiones
VC-011 DO: interacción humana real
VC-012 DO: métrica equivocada semántico
VC-013 DO: excelencia sin prueba conductual
VC-014 DO: metavicio sobre el auditor — circular
VC-015 DO: delegación de juicio conductual
VC-016 DO: comprensibilidad — juicio humano
VC-018 DO: parchear sin diagnosticar conductual
VC-019 DO: bug vuelve con otra forma conductual
VC-020 DO: modificar sin caso mínimo conductual
VC-021 DO: fallos secundarios vivos conductual
VC-022 DO: más cambios menos certeza conductual
VC-023 DO: costos diferidos invisibles conductual
VC-024 DO: acumular antes de probar conductual
VC-025 DO: "objetivo ambiguo" semántico
VC-026 DO: incertidumbre alta conductual
VC-027 DO: estado vive en chat conductual
VC-028 DO: avanzar sin probar conductual
VC-029 DO: "enormes" subjetivo
VC-030 DO: ediciones grandes degradan coherencia conductual
VC-032 DO: mejoras no pedidas — requiere conocer intención
VC-033 DO: abandonar validación conductual
VC-034 DO: ausencia de causalidad semántico
VC-035 DO: repetir lo resuelto conductual
VC-036 DO: acción destructiva directa conductual
VC-037 DO: reemplazar sin diagnóstico conductual
VC-038 DO: éxito parcial conductual
VC-039 DO: atajos no registrados conductual
VC-040 DO: "difícil de cambiar" subjetivo
VC-041 DO: agente expande alcance conductual
VC-042 DO: fix-revert consume contexto conductual
VC-043 DO: cada fix introduce otro bug conductual
VC-044 DO: "dueño" fuera del alcance AST
VC-045 DO: "transferencia incompleta" semántico
VC-046 DO: archivar sin extraer valor conductual
VC-047 DO: memoria/estado difieren semántico
VC-048 DO: falta de estratificación — diseño
VC-049 DO: docs de agente igual a humana semántico
VC-050 DO: estado cambia sin evento conductual

## SECCIÓN 1B: VC-051..VC-114

VC-051 DO: agente olvida requisitos conductual
VC-052 DO: respuestas empeoran por exceso conductual
VC-053 DO: cambio rompe estado conductual
VC-054 DO: varias fuentes compiten — análisis arquitectura
VC-055 DO: actores pisan cambios — análisis semántico
VC-056 DO: dependencias inventadas semántico
VC-057 DO: versiones en múltiples docs — genérico semántico
VC-058 DO: requiere instrumentación de runtime
VC-059 DO: trabajo cae en actor incorrecto conductual
VC-060 DO: dos historias se combinan conductual
VC-061 DO: sustituto confundido con componente semántico
VC-062 DO: pérdida de commits por sesiones paralelas
VC-063 DO: estado declarado no coincide semántico
VC-064 DO: decisiones no explicables semántico
VC-065 DO: lógica precede al modelo conductual
VC-066 DO: UI sin layout — fuera del scope (no es UI)
VC-067 DO: reglas no listadas semántico
VC-068 DO: reglas chocan — lógica de negocio
VC-069 DO: grafo causal desconocido — análisis arquitectura
VC-070 DO: check S7 ya existe; duplicado sería circular
VC-071 DO: fallo se propaga — coupling semántico
VC-072 DO: corte rompe semántica semántico
VC-073 DO: se pierde coherencia global semántico
VC-074 DO: ausencia de schema en I/O — falsos positivos sin umbral
VC-075 DO: APIs externas asumidas — requiere conocer qué es externo
VC-076 DO: Any/sin type hints — falsos positivos sin umbral acordado
VC-077 DO: subconjunto semántico de tipado laxo
VC-078 DO: D2 StubVisitor ya cubre stubs en funciones
VC-079 DO: dependencias externas inestables — análisis arquitectura
VC-080 DO: duplicación semántica — análisis de código
VC-081 DO: docs y código divergen semántico
VC-082 **ST: check AST/regex: top-level import X vs pyproject.toml**
VC-083 DO: TK-043 ya cubre via audit_script_orphans/vulture
VC-084 DO: consumidores previos se rompen semántico
VC-085 DO: logs no explican fallos semántico
VC-086 DO: capa nueva evita tocar falla semántico
VC-087 DO: gate de zero-warnings ya existe; vicio ya cubierto
VC-088 DO: fallo documentado en vez de corregido semántico
VC-089 DO: editar sin entender conductual
VC-090 DO: repetir errores — memoria no cargada conductual
VC-091 DO: declarar inexistencia sin búsqueda conductual
VC-092 DO: universo auditado mal definido semántico
VC-093 DO: no buscar abusos conductual
VC-094 DO: controles dispersos — análisis arquitectura seguridad
VC-095 DO: falta de entorno seguro — requiere conocer producción
VC-096 DO: D8 ya existe con tests reales; redundante en catch-all
VC-097 DO: pruebas adaptadas al resultado semántico
VC-098 DO: fallos reales no cubiertos semántico
VC-099 DO: resiliencia no observada — requiere caos, no AST
VC-100 DO: performance o seguridad no medidos semántico
VC-101 DO: entorno idealizado semántico
VC-102 DO: fallo no diagnosticable semántico
VC-103 DO: fuera del scope del repo (no es UI)
VC-104 DO: runtime real difiere semántico
VC-105 DO: HTML/startup/build no auditados semántico
VC-106 DO: test_setup_validation ya cubre VT-107; VC genérico semántico
VC-107 DO: actores fuera de rol — requiere modelo de roles
VC-108 DO: confianza en disciplina humana conductual
VC-109 **ST: check regex/AST: rutas absolutas hardcodeadas en scripts/**
VC-110 DO: recurso finito no presupuestado semántico
VC-111 DO: directorio añadido sin verificar — requiere historia
VC-112 DO: protocolo copiado sin confirmar — requiere repos satélite
VC-113 DO: nombre no refleja alcance real semántico
VC-114 DO: defecto sin ítem ejecutable conductual

## SECCIÓN 1C: VC-119..VC-123

VC-119 DO: parchear síntoma en vez de causa raíz conductual
VC-120 DO: obsesión con plan defectuoso conductual
VC-121 **ST: funciones con nombre idéntico en módulos distintos — AST**
VC-122 **ST: pip install / subprocess.*pip en scripts — regex/AST**
VC-123 **ST: git add -A / git add . en scripts — regex/AST**

---

## SECCIÓN 2: TK (test_d10_tokenomics) — 42 IDs

TK-001 DO: nueva sesión reinicia — conductual
TK-002 DO: estado no externalizado — conductual
TK-003 DO: contextos contaminados — conductual
TK-004 DO: tokens reconstruyendo entorno — conductual
TK-005 **ST: STATUS.md debe tener secciones estructuradas (estado/siguiente/bloqueadores)**
TK-006 DO: resolver conflicto consume contexto — conductual
TK-007 DO: copias contradictorias — semántico
TK-008 DO: confusión entre invariantes y variables — semántico
TK-009 DO: archivos completos saturan — conductual
TK-010 DO: fragmentos pierden significado — semántico
TK-011 DO: instrucciones se mezclan — semántico
TK-012 DO: muchos tokens antes de actuar — conductual
TK-013 DO: herramientas no usadas — conductual
TK-014 DO: archivo grande enviado entero — conductual
TK-015 DO: información irrelevante procesada — conductual
TK-016 DO: modelo reparte atención — conductual
TK-017 DO: políticas largas se repiten — conductual
TK-018 **ST: .protocol/review_queue.json debe existir como backlog externo separado**
TK-019 DO: exploración ciega — conductual
TK-020 DO: respuestas largas por defecto — conductual
TK-021 DO: formato variable — conductual
TK-022 DO: few-shot redundante — conductual
TK-024 DO: compactación pierde decisiones — semántico
TK-025 DO: hallazgo se pierde entre ruido — semántico
TK-026 DO: logs extensos desplazan el problema — semántico
TK-027 DO: pérdida de contexto por trazas verbosas — semántico
TK-028 DO: reprocesamiento recurrente — conductual
TK-029 DO: tareas diferibles una a una — conductual
TK-030 DO: capacidad máxima para todo — conductual
TK-031 DO: sesión larga se degrada — conductual
TK-032 DO: pausas invalidan caché — conductual
TK-033 DO: contexto colapsa silenciosamente — conductual
TK-034 DO: loops de fix/revert no medidos — conductual
TK-035 DO: contexto caro para decidir — conductual
TK-036 DO: agente no sabe si pensar o ejecutar — conductual
TK-037 DO: usuario cuenta mensajes — conductual
TK-040 DO: reducción declarada sin telemetría — conductual
TK-041 DO: sesión cortada por límites no presupuestados — conductual
TK-043 **STALE: ya tiene def real (audit_script_orphans/audit_dead_code) — REMOVER**
TK-F01 DO: reuso no modelado — conductual
TK-F02 DO: recuperación no selectiva — conductual
TK-F03 DO: presupuesto de salida ausente — conductual (OutputCompressor parcial)
