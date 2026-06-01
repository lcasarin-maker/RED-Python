# Sprint 10 — Repos Externos y Vigilancia en Vivo

## Objetivo

Consolidar la investigación de repositorios externos con criterios agnósticos y dejar solo el conocimiento que mejora:

- integridad de dependencias;
- diagnóstico de tests;
- tokenomics y control de gasto;
- seguridad de borde;
- orquestación de proveedores;
- vigilancia del agente en tiempo real.

## Fuentes oficiales consultadas

- [deptry](https://github.com/osprey-oss/deptry)
- [deptry docs](https://deptry.com/usage/)
- [pytest docs](https://docs.pytest.org/en/stable/how-to/assert.html)
- [tokencost](https://github.com/AgentOps-AI/tokencost)
- [AgentOps](https://github.com/AgentOps-AI/agentops)
- [CostScope](https://github.com/costscope/costscope)
- [llm-pricing](https://github.com/tekacs/llm-pricing)
- [trivy](https://github.com/aquasecurity/trivy)
- [litellm](https://github.com/BerriAI/litellm)
- [pre-commit](https://github.com/pre-commit/pre-commit)
- [pre-commit-hooks](https://github.com/pre-commit/pre-commit-hooks)

## Matriz de decisión

| Repositorio | Fallo que ataca | Lógica agnóstica | Decisión | Encaje en Cerberus |
|---|---|---|---|---|
| `abravalheri/deptry` / `osprey-oss/deptry` | Dependencias fantasma, faltantes o mal declaradas | Comparar imports reales contra el manifiesto del proyecto | INTEGRAR | Refuerza D1 y D4 con control de deriva de dependencias |
| `adamchainz/pytest-good-assertions` | Fallos de test poco legibles | Densidad diagnóstica en aserciones | COMPLEMENTAR | El principio ya está cubierto por pytest y por la capa de tests de Cerberus; no se duplicó código |
| `AgentOps-AI/tokencost` | Ceguera de coste por sesión o por llamada | Metering preflight en USD | INTEGRAR | Reafirma D10 y la disciplina de gasto antes de ejecutar |
| `aquasecurity/trivy` | Secretos, CVEs, misconfiguraciones y SBOMs fuera de control | Escaneo de borde y superficie | INTEGRAR | Refuerza D7 y la higiene de seguridad en el workspace |
| `BerriAI/litellm` | Fragmentación de proveedores y rutas LLM | Capa de abstracción y fallback | COMPLEMENTAR | Útil como referencia de orquestación, pero ya existe cobertura conceptual en Cerberus |
| `cerberus-llm/cerberus` | Prompts y salidas sin aislamiento | Filtro I/O para LLM | DESCARTAR | El árbol activo de Cerberus ya aplica gates más fuertes en filesystem, pre-edit y auditoría |
| `pre-commit/pre-commit` | Commits que saltan controles | Enforcement en la frontera del VCS | INTEGRAR | Encaja con la política de gate local de Cerberus |
| `pre-commit/pre-commit-hooks` | Higiene básica del workspace | Hooks genéricos de limpieza y validación | INTEGRAR | Refuerza el bloque de higiene y formato |
| `AgentOps-AI/agentops` | Falta de observabilidad de agentes en vivo | Telemetría de ejecución, monitoreo y benchmarking | INTEGRAR | Corrobora la necesidad de vigilancia en tiempo real, no post-mortem |
| `costscope/costscope` | Gobernanza de gasto a escala | Normalización FinOps | BACKLOG | Útil si el footprint financiero de la plataforma crece |
| `tekacs/llm-pricing` | Coste real de requests con cache | Pricing vivo por input/output/cache | COMPLEMENTAR | Muy útil como inspiración de cálculo fino de coste por request |

## Conclusiones operativas

1. `deptry`, `trivy`, `pre-commit`, `pre-commit-hooks` y `AgentOps` sí aportan enforcement real.
2. `tokencost` y `llm-pricing` refuerzan la disciplina de tokenomics, pero Cerberus ya tiene el núcleo operativo para coste y tracking.
3. `litellm` es valioso como referencia de arquitectura de proveedor, aunque por ahora queda como complemento.
4. `cerberus-llm/cerberus` no se integra porque su lógica queda superada por los gates actuales de Cerberus.
5. No se añadió un PI nuevo al Golden Standard: los principios durables ya estaban cubiertos por `PI-003`, `PI-013`, `PI-015..PI-018` y las reglas de D1/D7/D10.

## Vigilancia en vivo

La lección transversal que sí queda absorbida es esta:

- observar señales de riesgo durante la ejecución;
- no esperar al post-mortem;
- cortar o replanificar antes de que el daño se consolide;
- medir coste, retries y deriva del agente mientras el flujo sigue vivo.

## Resultado

- Sprint 10 queda cerrado como investigación aplicada.
- El conocimiento útil se retiene como referencia canónica.
- Lo redundante no se duplica en el Golden Standard.
