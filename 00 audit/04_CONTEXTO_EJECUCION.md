# 04 — CONTEXTO DE EJECUCIÓN

## 0. Orden de carga

Cargar siempre en este orden:

1. `00_CONSTITUCION_CERBERUS.md`
2. `01_AUDITORIA_LOCAL.md`
3. `02_AUDITORIA_REPOSITORIOS.md`
4. `03_EVOLUCION_GOLDEN_STANDARD.md`
5. `04_CONTEXTO_EJECUCION.md`

Después de cargar los cinco archivos, ejecutar la auditoría completa sin pedir confirmación entre fases, salvo bloqueo técnico real.

---

## 1. Proyecto objetivo

```text
D:\GoogleDrive\AI\Cerberus
```

---

## 2. Golden Standard objetivo

```text
D:\GoogleDrive\AI\Cerberus\Golden_Standard\golden_standard.yaml
```
(Nota: Las bibliotecas de vicios y tokenomics `.md` fueron unificadas y deprecadas en `deprecated/Golden_Standard/` para ahorro de tokens de contexto)

---

## 3. Objetivos específicos de esta corrida

1. Ejecutar auditoría adversarial del proyecto local para detectar fallos propios.
2. Auditar repositorios externos de GitHub para integrar nuevas funcionalidades lógicas.
3. Asegurar que todo lo que contiene Golden Standard esté bien regulado y ejecutable por el proyecto.
4. Detectar deuda técnica.
5. Detectar deuda arquitectónica.
6. Verificar autonomía Set and Forget.
7. Validar si la implementación actual es la mejor para lo que pretende resolver.
8. Evaluar si ciertos componentes deberían ser JSON, YAML, SQLite, índice, skill, agente independiente, librería, pipeline o regla declarativa.
9. Proponer integración ejecutable sin contaminar el Golden Standard con herramientas concretas.
10. Dictaminar `APPROVED` o `REJECTED`.

---

## 4. Política de intervención

No pidas confirmación entre fases.

Ejecuta todas las fases en secuencia salvo bloqueo técnico real.

Si encuentras un bloqueo técnico:

1. Regístralo.
2. Explica su impacto.
3. Continúa con las fases no bloqueadas.
4. No detengas el trabajo salvo imposibilidad material.

---

## 5. Repositorios objetivo

```text
https://github.com/abravalheri/deptry
https://github.com/adamchainz/pytest-good-assertions
https://github.com/AgentOps-AI/tokencost
https://github.com/aquasecurity/trivy
https://github.com/BerriAI/litellm
https://github.com/cerberus-llm/cerberus
https://github.com/github/codeql
https://github.com/gitleaks/gitleaks
https://github.com/jeremylong/DependencyCheck
https://github.com/karpathy/code-review-assistant
https://github.com/kucherenko/jscpd
https://github.com/mutation-testing/mutation-testing
https://github.com/ogulcanaydogan/LLM-Cost-Guardian
https://github.com/openai/openai-prompt-optimizer
https://github.com/philips-software/cerberus
https://github.com/pre-commit/pre-commit
https://github.com/pre-commit/pre-commit-hooks
https://github.com/PV-Bhat/vibe-check-mcp-server
https://github.com/PyCQA/bandit
https://github.com/PyCQA/pylint
https://github.com/pytest-dev/pytest-cov
https://github.com/pythonguide/try-except-guard
https://github.com/refractionPOINT/viberails
https://github.com/returntocorp/semgrep
https://github.com/rubik/radon
https://github.com/samuelcolvin/token-bucket
https://github.com/scality/ghaudit
https://github.com/securecodebox/githubaudit
https://github.com/securecodebox/github-rate-limits-exporter
https://github.com/snyk/snyk
https://github.com/testdouble/testdouble
https://github.com/tomasbasham/ratelimit
https://github.com/typicode/git-hooks
https://github.com/typicode/husky
https://github.com/ujjwalm29/tokenator
https://github.com/yuvrajangadsingh/vibecheck
```

---

## 6. Reporte final obligatorio

Entrega el reporte final bajo este esquema exacto:

```markdown
# 🛡️ REPORTE DE AUDITORÍA ADVERSARIAL DE SOFTWARE — CODER CERBERUS

## 1. Traducción Ejecutiva de Riesgo

- **Riesgo Operativo Detectado:**
- **Impacto Financiero de Tokens:**
- **Estatus de la Autonomía Set and Forget:** EXCELENTE / FRÁGIL / INACEPTABLE
- **Estatus de Adecuación Arquitectónica:** OPTIMAL / ADECUADO / SUBÓPTIMO / DEFECTUOSO

## 2. Mapa de Código Vivo y Topología Limpia

- **Archivos del Core Activos:**
- **Scripts del Control Plane Clasificados:**
- **Estructura Oculta:**
- **Archivos en Cuarentena:**

## 3. Escrutinio Cruzado del Golden Standard

- **Vicios de Testing Detectados:**
- **Vicios de Vibe Coding Detectados:**
- **Fugas de Tokenomics Detectadas:**
- **Reglas Declarativas No Ejecutables:**
- **Diferencias entre MD y YAML:**
- **RULE THEATER Detectado:**

## 4. Auditoría 12D

| Dimensión | Veredicto | Evidencia | Riesgo traducido | Corrección |
|---|---|---|---|---|
| D1 Integridad & S19 | APPROVED / REJECTED | | | |
| D2 Completitud | APPROVED / REJECTED | | | |
| D3 Claridad | APPROVED / REJECTED | | | |
| D4 Anti-spaghetti | APPROVED / REJECTED | | | |
| D5 Angry Path | APPROVED / REJECTED | | | |
| D6 Anti-theater & Anti-slop | APPROVED / REJECTED | | | |
| D7 Seguridad | APPROVED / REJECTED | | | |
| D8 Cobertura | APPROVED / REJECTED | | | |
| D9 Pureza de Tests | APPROVED / REJECTED | | | |
| D10 Tokenomics | APPROVED / REJECTED | | | |
| D11 SCA Trivy | APPROVED / REJECTED | | | |
| D12 Satellite Drift | APPROVED / REJECTED | | | |

## 4B. Auditoría de Adecuación Arquitectónica

| Componente | Implementación Actual | Alternativa Recomendada | Veredicto | Impacto |
|---|---|---|---|---|

### Hallazgos Arquitectónicos Críticos

- Componentes innecesarios.
- Componentes sobreingenierizados.
- Componentes subdimensionados.
- Persistencia incorrecta.
- Patrones arquitectónicos inadecuados.
- Oportunidades de simplificación.

### Deuda Arquitectónica Detectada

| Severidad | Componente | Problema | Solución Recomendada |
|---|---|---|---|

## 5. Auditoría de Repositorios Externos

| Repositorio | Función Principal | Dimensión Cerberus | Vicio Mitigado | Lógica Operativa | Abstracción Agnóstica | Estado GS | Decisión |
|---|---|---|---|---|---|---|---|

## 6. Bloques Propuestos para Golden Standard

### Archivo: [nombre]

```markdown
[bloques exactos]
```

## 7. Estrategia de Integración Ejecutable

| Regla | Archivo / Runner / Hook | Acción | Falsabilidad | Resultado esperado |
|---|---|---|---|---|

## 8. Correcciones Aplicadas

| Archivo | ID GS / Mandato | Tipo de Cambio | Rationale | Test de Falsabilidad |
|---|---|---|---|---|

## 9. Estatus Final de Gobernanza

- **APPROVED / REJECTED:**
- **Razón causal:**
- **Criterio mínimo para pasar a APPROVED:**

## 10. Backlog Diferido

| Mejora | ID GS relacionado | Justificación | Prioridad |
|---|---|---|---|
```

---

## 7. Criterio final

El agente debe entregar un resultado completo.

No debe dividir la auditoría salvo bloqueo técnico material.

No debe pedir confirmación entre fases.

No debe declarar `APPROVED` si hay una sola violación crítica, duda razonable o deuda arquitectónica material.
