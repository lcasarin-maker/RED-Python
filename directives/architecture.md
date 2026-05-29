# 3‑Layer Architecture

## Capa 1 – Directiva

- **Qué:** SOPs escritos en Markdown que describen los objetivos, entradas, herramientas, salidas y casos límite.
- **Dónde:** `directives/`
- **Propósito:** Servir como guía de alto nivel para cualquier agente o humano que interactúe con el proyecto.

## Capa 2 – Orquestación

- **Qué:** El agente (tú) que interpreta las directivas, decide el flujo de trabajo, llama a scripts y maneja errores.
- **Dónde:** Código del agente (por ejemplo, `agent.py`, `protocol_cli.py`).
- **Propósito:** Traducir la intención escrita en la directiva a acciones concretas y determinísticas.

## Capa 3 – Ejecución

- **Qué:** Scripts Python determinísticos que realizan la lógica real (API calls, procesamiento de datos, generación de entregables).
- **Dónde:** `execution/`
- **Propósito:** Ser reproducibles, testeables y rápidos. Cada script tiene sus propias pruebas unitarias y documentación.

---

Esta arquitectura separa *intención* (directiva) de *decisión* (orquestación) y de *acción* (ejecución), reduciendo la probabilidad de fallos silenciosos y facilitando auditorías.
