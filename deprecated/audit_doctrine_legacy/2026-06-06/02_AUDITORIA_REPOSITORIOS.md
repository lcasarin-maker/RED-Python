# 02 — AUDITORÍA DE REPOSITORIOS EXTERNOS

## 0. Objetivo

Auditar los repositorios externos listados en `04_CONTEXTO_EJECUCION.md` para extraer capacidades, heurísticas, métricas y lógicas operativas que puedan fortalecer Coder Cerberus.

La extracción debe hacerse sin copiar dependencias, sin contaminar el Golden Standard con nombres comerciales y sin generar redundancia.

> Nota: el Golden Standard canónico se trata aparte en `03_EVOLUCION_GOLDEN_STANDARD.md`. Esta fase audita repositorios externos de terceros, no GS.

---

## 1. Alcance

Para cada repositorio externo:

1. Identifica su función principal.
2. Clasifícalo dentro de una o más dimensiones de Coder Cerberus.
3. Extrae el vicio, falla o problema que resuelve.
4. Extrae la lógica operativa subyacente.
5. Abstrae esa lógica como conocimiento agnóstico.
6. Contrasta la lógica contra el Golden Standard.
7. Determina si aporta una regla nueva, métrica nueva, heurística nueva, patrón de enforcement nuevo o nada nuevo.
8. Determina si debe integrarse, complementarse, descartarse o registrarse en backlog.
9. Determina si la capacidad debe:
   - implementarse como regla Golden Standard;
   - implementarse como scanner;
   - implementarse como hook;
   - implementarse como runner;
   - implementarse como pipeline;
   - implementarse como skill;
   - implementarse como agente;
   - documentarse únicamente;
   - descartarse.

---

## 2. Método obligatorio por repositorio

Para cada repositorio:

1. Leer README.
2. Leer documentación principal.
3. Revisar estructura de código si el README no basta.
4. Identificar qué vicio, falla o riesgo busca prevenir.
5. Identificar mecanismo o lógica operativa.
6. Clasificarlo dentro de una o más dimensiones de Coder Cerberus.
7. Abstraer la lógica como principio agnóstico.
8. Comparar contra:
   - las dimensiones, principios y vacíos de Cerberus;
   - cuando aplique, la interfaz documental del Golden Standard externo, sin tratarlo como submódulo activo.
9. Determinar novedad real.
10. Emitir decisión.

---

## 3. Dimensiones Coder Cerberus para clasificación

Cada repositorio debe clasificarse en una o más de estas dimensiones:

1. D1 Integridad y Pureza Estructural.
2. D2 Completitud del control plane.
3. D3 Claridad, estilo y complejidad.
4. D4 Anti-Spaghetti y Aislamiento.
5. D5 Angry Path y Robustez.
6. D6 Anti-Theater y Anti-Slop.
7. D7 Seguridad de Datos y Confinamiento.
8. D8 Cobertura Adversarial.
9. D9 Pureza de Tests y Falsabilidad.
10. D10 Tokenomics e Higiene de Contexto.
11. D11 SCA Trivy.
12. D12 Satellite Drift (Adopción de Release).

---

## 4. Reglas de abstracción

Prohibido integrar en el Golden Standard:

- comandos de instalación;
- nombres comerciales;
- nombres de repositorios;
- dependencias concretas;
- instrucciones atadas a lenguaje específico;
- rutas o configuraciones específicas de terceros.

Permitido integrar:

- principios;
- métricas;
- heurísticas;
- condiciones de bloqueo;
- patrones de detección;
- criterios de falsabilidad;
- estrategias de enforcement;
- modelos de gobernanza;
- criterios de arquitectura;
- patrones de eficiencia.

---

## 5. Formato individual obligatorio

```text
Repositorio:
URL:
[HECHO] Función documentada:
[HECHO] Mecanismo relevante:
[INFERENCIA] Vicio que mitiga:
[INFERENCIA] Lógica agnóstica:
Dimensión Cerberus:
Golden Standard relacionado:
Estado frente al GS:
Decisión: INTEGRAR / COMPLEMENTAR / DESCARTAR / BACKLOG
Justificación:
Ruta de implementación sugerida:
```

---

## 6. Matriz obligatoria por repositorio

```markdown
| Repositorio | Función Principal | Dimensión Cerberus | Vicio Mitigado | Lógica Operativa | Abstracción Agnóstica | Estado GS | Decisión |
|---|---|---|---|---|---|---|---|
```

---

## 7. Manejo de repositorios inaccesibles o pobres en documentación

Si un repositorio no tiene documentación suficiente:

```text
Repositorio:
URL:
Limitación:
[SUPUESTO] Función probable:
Nivel de confianza:
Riesgo de inferencia:
Decisión:
```

No inventar hechos.

Toda deducción debe marcarse como `[SUPUESTO]`.

---

## 8. Criterios de decisión

### INTEGRAR

Usar cuando el repositorio aporta una lógica nueva, relevante, no cubierta y ejecutable.

### COMPLEMENTAR

Usar cuando la lógica ya existe parcialmente, pero el repositorio aporta métrica, enforcement o heurística adicional.

### DESCARTAR

Usar cuando la lógica ya está cubierta o no es pertinente.

### BACKLOG

Usar cuando la lógica es interesante, pero no crítica, no madura o requiere rediseño posterior.

---

## 9. Categorías de capacidades a buscar

Durante la auditoría externa, identificar capacidades vinculadas a:

1. Validación estática.
2. Linting.
3. Control de tokens.
4. Testing de mutación.
5. Escaneo de vulnerabilidades.
6. Gestión de agentes.
7. Detección de secretos.
8. Detección de dependencias muertas.
9. Cobertura de pruebas.
10. Calidad de aserciones.
11. Rate limiting.
12. Token budgeting.
13. Cost observability.
14. Duplicate code detection.
15. Git hooks.
16. Pre-commit governance.
17. Supply chain security.
18. Dependency risk.
19. Code query security.
20. Arquitectura de enforcement.

---

## 10. Repositorios objetivo

Auditar obligatoriamente los repositorios definidos en `04_CONTEXTO_EJECUCION.md`.

La lista base es:

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

## 11. Entregable

```markdown
## Auditoría de Repositorios Externos

| Repositorio | Función Principal | Dimensión Cerberus | Vicio Mitigado | Lógica Operativa | Abstracción Agnóstica | Estado GS | Decisión |
|---|---|---|---|---|---|---|---|

## Capacidades Nuevas Detectadas

| Capacidad | Fuente | Lógica Agnóstica | Ruta Recomendada | Prioridad |
|---|---|---|---|---|

## Repositorios Descartados

| Repositorio | Motivo | Riesgo de descarte |
|---|---|---|

## Repositorios a Backlog

| Repositorio | Motivo | Condición para reconsiderar |
|---|---|---|
```

## 11. Exclusión explícita

- GS no se audita aquí como repositorio externo genérico.
- GS se audita en la fase 3 como fuente canónica externa y como contrato de consumo para Cerberus.
