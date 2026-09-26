# DECISIONS

Durable decisions only — not a log. One entry per decision, with the reason it
was taken and what it rules out.

Estas entradas recogen decisiones que ya estaban escritas en el repo (commit y
documento citados). No se añadió ninguna razón que esas fuentes no den.

---

## 2026-06-07 — Los sub-agentes son una decisión estratégica, no se automatizan

**Decisión.** Los sub-agentes requieren juicio estratégico y no se automatizan.

**Por qué.** No son una técnica de ahorro de tokens sino una decisión de flujo de trabajo; la decisión es contextual, no basada en una métrica. (Fuente: `docs/TK-046_MANUAL_SUBAGENTS.md`.)

**Qué descarta.** Disparar sub-agentes automáticamente por umbral de tokens o por regla mecánica.

---

## 2026-07-30 — Se retira el núcleo vendorizado y los hooks que lo llamaban

**Decisión.** Se quita `.protocol-core/` (copia vendorizada del modelo de junction WP1-3, sustituido por instalación fijada), la plantilla `settings.template.json` previa a la adopción y cuatro hooks locales de `.git/hooks` que seguían invocando ese binding retirado. Lo local sin seguimiento se respaldó antes de borrar. (Fuente: commit `10f2535`, `chore(governance): pre-adopt cleanup`.)

**Por qué.** El modelo de junction quedó superseded por la instalación fijada, y los hooks locales aún llamaban a un binding que ya no existe.

**Qué descarta.** Mantener una copia vendorizada del núcleo de gobierno de otro proyecto dentro de este repo.
