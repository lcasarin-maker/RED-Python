# CoderCerberus — Marco Conceptual y Filosofía Operativa
**Versión:** v0.5 | **Actualizado:** 2026-06-04 | **Estado:** DOCUMENTO DE IDENTIDAD ÚNICO

> **Fuente normativa de reglas:** [VibeCoding Golden Standard](https://github.com/lcasarin-maker/VibeCoding_GoldenStandard) — repo independiente en `D:\AI\VibeCoding_GoldenStandard`
> Este documento NO duplica reglas del GS. Explica qué ES Cerberus y por qué existe.

---

## 1. Idea rectora

CoderCerberus toma su nombre de Cerbero, el guardián del Inframundo. Su función era impedir el paso de quienes no cumplían los requisitos para ingresar.

Esa es la filosofía central: CoderCerberus es el **guardián, vigilante y gatekeeper** de proyectos de programación asistidos por inteligencia artificial.

Su propósito es impedir que llegue a producción cualquier código: mal hecho, malformado, frágil, no documentado, no reversible, difícil de auditar, desconectado de la funcionalidad real, construido solo para "pasar tests", o producto de malas prácticas de vibe coding.

**Cerberus no valida formalidades. Valida calidad real.**

El criterio final no es que el proyecto "parezca correcto". Es que funcione, sea trazable, reversible, mantenible, escalable y pueda ser usado por un humano.

---

## 2. Problema que resuelve

La programación asistida por IA permite avanzar rápido pero genera riesgos estructurales:

1. Código que aparenta funcionar pero está mal diseñado
2. Tests que validan teatro de seguridad
3. Funcionalidades implementadas parcialmente
4. Desconexión entre backend, frontend y experiencia de usuario
5. Archivos creados para satisfacer instrucciones, sin valor operativo real
6. Soluciones no reversibles y pérdida de trazabilidad
7. Crecimiento desordenado y deuda técnica invisible
8. Consumo excesivo de tokens por mala planeación o falta de estructura
9. Falta de memoria institucional entre sesiones, agentes y proyectos
10. Repetición de errores ya detectados anteriormente

CoderCerberus existe para evitar que esos vicios entren, permanezcan o se reproduzcan.

---

## 3. Directrices del Operador (Luis Casarin) — INMUTABLES

Todo protocolo, script y test se evalúa contra estas 20 directrices. Son la voluntad del operador.

1. No soy programador, soy abogado. El protocolo no puede asumir formación técnica.
2. El objetivo es vibe coding evitando los problemas comunes (deriva, teatro, tokens).
3. Uso varios agentes a la vez. El agotamiento de tokens es un problema operacional crítico.
4. La deriva es grave. Los agentes hacen side-quests y distraen con sugerencias que no atacan el problema.
5. Revisión siempre a fondo. La forma importa pero no es la meta. Los tests deben ser implacables respecto del fondo.
6. Si un proyecto no nace dentro del protocolo, se hace auditoría adversarial completa.
7. El protocolo es el cerebro rector de TODOS los proyectos.
8. El protocolo debe afectar con autoridad a cualquier agente: Claude, Codex, ChatGPT, Gemini.
9. Cuando cambie el protocolo, el cambio se propaga automáticamente a todos los agentes y proyectos.
10. Descubrimiento en proyecto → propagación al protocolo general.
11. Los permisos de los agentes deben ser los necesarios para operar, pero no tan amplios que puedan destruir.
12. El sistema debe ser 100% operativo, no aspiracional.
13. El agente debe escoger el modelo correcto para la tarea y sugerirlo o cambiarlo automáticamente.
14. Escoger siempre el modelo mínimo necesario para cuidar tokens.
15. Implementar estrategias de ahorro de tokens de forma automatizada.
16. Hacer auditorías periódicas contra estas directrices para evitar deriva automáticamente.
17. Hacer auditoría periódica contra deprecated para evitar pérdida de funciones o regresiones.
18. Debe haber candados y bloqueos claros para evitar destrucción o regresión.
19. Se pide 100% de pass pero no como meta: es consecuencia de validación real, no objetivo de diseño de tests.
20. Los tests van antes del código y con base en comportamiento deseado.

**Antipatrones prohibidos diagnosticados:**
- Auditar forma no fondo (validar existencia, no comportamiento)
- Sin mecanismo para detectar regresiones entre versiones
- Darle la vuelta al bloqueador en lugar de resolverlo
- Privilegiar deprecar sobre arreglar

---

## 4. Relación con Golden Standard

CoderCerberus y el Golden Standard son dos proyectos correlacionados pero distintos.

| | Golden Standard | CoderCerberus |
|---|---|---|
| **Naturaleza** | Base de conocimiento normativo | Herramienta de enforcement |
| **Alcance** | Universal (cualquier proyecto, cualquier agente) | Proyectos vigilados por Cerberus |
| **Repo** | `D:\AI\VibeCoding_GoldenStandard` (independiente) | `D:\AI\Cerberus` |
| **Lenguaje** | Inglés (primario) | Español + Inglés |

**Regla fundamental:**
> Todo mandato activo de Cerberus debe derivar de una entrada del Golden Standard.
> No debe existir regla en Cerberus sin traza al GS.
> No debe existir ítem crítico en GS sin reflejo operativo en Cerberus.

**Cadena mínima de operatividad:**
```
Golden Standard → Regla ejecutable → Prueba asociada → Evidencia generada → Consecuencia definida
```
Sin esta cadena, no hay control real.

---

## 5. Arquitectura de tres capas

### Capa 1 — Golden Standard (fuente normativa)
Repo Git independiente en `D:\AI\VibeCoding_GoldenStandard`. Cerberus lo consume por ruta externa; no existe copia local.

### Capa 2 — Cerberus al interior (autorregulación)
Garantiza que Cerberus no incurra en los mismos vicios que previene. Incluye auditoría 12D propia, tests de compliance y bloqueos pre-commit.

### Capa 3 — Cerberus al exterior (vigilancia de proyectos)
Audita y bloquea proyectos externos en dos momentos:
1. **En tiempo real:** pre-commit hooks con `exit 1`
2. **A posteriori:** auditoría adversarial 12D completa

---

## 6. Estructura física del repo

```text
D:\AI\Cerberus\
├── AGENT.md / PROTOCOL_SYSTEM.md / PROTOCOL_BEHAVIOR.md  ← Protocolo para agentes
├── SPEC.md                         ← Memory bank: whitelist, arquitectura, handoff
├── HISTORIAL.md                    ← Audit trail inmutable de sesiones
├── SOURCES_OF_TRUTH.md             ← Índice de fuentes de autoridad por concepto
├── scripts/                        ← 60+ scripts de automatización operativa
│   ├── run_security_audit_12d.py   ← Auditor 12D (gatekeeper principal)
│   ├── pre_edit_guard.py           ← Hook PreToolUse (bloqueo en tiempo real)
│   └── run_compliance_tests.py     ← Pre-commit gatekeeper
├── tests/                          ← Suite de compliance
├── .protocol/metadata/REGISTRY.json ← Registro de proyectos satélite
├── deprecated/                     ← Cuarentena de artefactos reemplazados
└── 00 audit/                       ← Metodología de auditoría adversarial
```

**GS externo (repo independiente):**
```text
D:\AI\VibeCoding_GoldenStandard\
├── golden_standard.yaml            ← Manifest ejecutable (única fuente de verdad)
├── golden_standard_*.yaml          ← Catálogos: coding, testing, tokenomics, insights
└── Wiki/                           ← Documentación navegable
```

---

## 7. Principio de autorregulación (Capa 2)

CoderCerberus debe auditarse a sí mismo. La autorregulación tiene 7 puntos de verificación, en orden de prioridad:

### Punto 1 — Cobertura total del Golden Standard (PRIORITARIO)
**Cada regla del GS debe tener implementación verificable en Cerberus.**

La cadena obligatoria para cada VC/TV/PI en el GS:
```
GS Rule (VC-xxx / TV-xxx / PI-xxx)
  → Mandato operativo en Cerberus (S-xx o B-xx en PROTOCOL_SYSTEM/BEHAVIOR.md)
  → Script o hook que lo enforcea (scripts/ o .git/hooks/)
  → Test que lo falsifique realmente (tests/test_*.py)
  → Evidencia de ejecución (log de terminal o audit report)
  → Consecuencia operativa si falla (exit 1, bloqueo, o audit FAIL)
```

Sin los 5 eslabones, la regla es decorativa. `test_golden_standard_compliance.py` verifica
existencia de IDs — pero la auditoría interior verifica que el **comportamiento** esté
implementado y testado. Ver `00 audit/05_AUDITORIA_INTERIOR.md` para checklist ejecutable.

### Punto 2 — Mandatos sin huecos
Todo mandato S1-S24 y B1-B28 de PROTOCOL tiene test que lo falsifique. Ningún mandato es solo texto.

### Punto 3 — Hooks que bloquean realmente
Pre-commit y pre_edit_guard no son teatro. Se verifican con simulación de violación → exit 1 confirmado.

### Punto 4 — Evidencia real en HISTORIAL.md
HISTORIAL.md contiene entradas verificables con fechas, acciones y resultados concretos — no solo encabezados.

### Punto 5 — Tests que falsifican de verdad (D9)
Ningún test hace `assert True` ni retorna éxito sin tocar el sistema bajo prueba.

### Punto 6 — El auditor pasa su propio audit
`run_security_audit_12d.py` se audita a sí mismo con la misma 12D. No hay excepciones para el gatekeeper.

### Punto 7 — Set and Forget
Ningún paso del protocolo requiere intervención manual del operador para ejecutarse. Si lo requiere, es una deuda de automatización que entra a HISTORIAL.md.

---

## 8. Los 12 dominios de auditoría (12D)

| Dominio | Verifica |
|---|---|
| **D1** Integridad estructural | Sin archivos zombie, shims ni compatibilidad zombie |
| **D2** Completitud del control plane | Hooks, runners, evidencia y reglas conectadas |
| **D3** Claridad y complejidad | Código legible, sin slop técnico ni salidas verbosas |
| **D4** Anti-spaghetti | Sin dependencias circulares ni acoplamiento excesivo |
| **D5** Angry Path | Excepciones con LOG + USUARIO + ESTADO + ACCIÓN |
| **D6** Anti-theater | Sin stubs vacíos, retornos falsos de éxito ni validaciones cosméticas |
| **D7** Seguridad | Sin secretos hardcodeados, shell=True peligroso ni rutas absolutas locales |
| **D8** Cobertura adversarial | Tests de fallo, fixtures maliciosos, casos de regresión |
| **D9** Pureza de tests | Tests que falsifican realmente, sin assert True ni mocks internos |
| **D10** Tokenomics | Sin fugas masivas de contexto ni lectura innecesaria de archivos grandes |
| **D11** SCA (Trivy) | Sin dependencias con CVEs críticos |
| **D12** Satellite Drift | Todos los proyectos satélite alineados a la versión del protocolo core |

---

## 9. Matriz nuclear del sistema

| Componente | Función | Riesgo que evita |
|---|---|---|
| Golden Standard (externo) | Fuente normativa de reglas | Pérdida de conocimiento entre proyectos |
| Cerberus interno (Capa 2) | Autorregulación | Que Cerberus incurra en los vicios que combate |
| Cerberus externo (Capa 3) | Vigilancia de proyectos satélite | Código viciado en GitHub |
| Auditoría 12D | Verificación multidimensional | Puntos ciegos por auditoría superficial |
| Pre-commit hooks | Bloqueo en tiempo real | Errores que llegan al repo |
| Testing real | Validación sustantiva | Teatro de seguridad |
| REGISTRY.json | Inventario de satélites | Drift no detectado entre proyectos |
| HISTORIAL.md | Audit trail inmutable | Pérdida de memoria institucional |
| Feedback loop (GS) | Aprendizaje acumulativo | Repetición de errores ya detectados |
| Consecuencias operativas | Regla → efecto real | Reglas decorativas sin bloqueo |

---

## 10. Tesis central

CoderCerberus impide que la velocidad del vibe coding destruya la calidad del software.

```
Hallazgo → Regla → Prueba → Evidencia → Consecuencia → Golden Standard
```

**Cerberus no existe para que el código parezca correcto.**
**Existe para que el código no pueda avanzar si está viciado.**

---

## 11. Contrato de consumo del Golden Standard (DOC_ONLY)

### 11.1 Problema que resuelve

Algunas entradas del GS no pueden verificarse con un test físico — son lecciones conceptuales, patrones de diseño o decisiones de arquitectura sin estado ejecutable. Esas entradas llevan `validating_mechanism: DOC_ONLY`. El error de concepto es tratarlas como ignorables. **DOC_ONLY no significa "sin consecuencias".**

### 11.2 Campo `downstream_verification` — Bifurcación de responsabilidad

| Valor | Obligación de Cerberus |
|---|---|
| `required` | Debe implementar un guard físico, bindear a uno existente, o registrar un consumer gap explícito en `golden_standard_audit.json` |
| `none` | Sólo advisory — indexar, citar, mostrar; no requiere guard |

### 11.3 Reglas de enforcement (binding para Cerberus)

1. **DOC_ONLY + `downstream_verification: required`** → NO es `test_exempt`. Cerberus debe actuar.
2. **DOC_ONLY + `downstream_verification: none`** → advisory únicamente; puede indexarse sin guard.
3. Las entradas DOC_ONLY forman parte de la superficie canónica de conocimiento — deben ser buscables en `protocol_engine/knowledge_loader.py`.
4. La ausencia de un test directo en el GS NO equivale a ausencia de responsabilidad del consumidor.

### 11.4 Campos requeridos en `golden_standard_audit.json`

Toda entrada DOC_ONLY registrada debe incluir:
`id`, `title`, `category`, `symptom`, `cause`, `solution`, `status`, `action`, `validating_mechanism`

### 11.5 Modos de acción válidos

| Modo | Descripción |
|---|---|
| `advisory_only` | `downstream_verification: none` — no se requiere guard |
| `consumer_guard_expected` | Guard implementado o bindeado a existente |
| `consumer_guard_absent_but_tracked` | Gap explícito registrado en audit JSON con justificación |

### 11.6 Modos de fallo prohibidos

- Tratar una entrada DOC_ONLY como si no existiera porque no tiene test
- Perder el campo `downstream_verification` en la ingesta (knowledge_loader debe preservarlo)
- Registrar `consumer_guard_expected` sin implementar ni bindear el guard
- Añadir entradas DOC_ONLY a la whitelist de `run_security_audit_12d.py` sin consumer gap documentado

---

*Documento de identidad de CoderCerberus v0.5 — Fuente única de verdad sobre qué ES Cerberus.*
*Para reglas ejecutables: `D:\AI\VibeCoding_GoldenStandard\golden_standard.yaml`*
*Para protocolo de agentes: `AGENT.md` + `PROTOCOL_SYSTEM.md` + `PROTOCOL_BEHAVIOR.md`*
*Para directrices completas del operador: ver Sección 3 de este documento.*


