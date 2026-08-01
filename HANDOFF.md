# HANDOFF

Continuity between sessions. Update it in the same commit as the work.

## NOW

- **2026-08-01 — Gobernanza Cerberus redesplegada (ola WP19, ejecutada desde el nucleo).** **suite_baseline vacio** — 0 fallas preexistentes, el ratchet queda en su posicion mas estricta y cualquier falla NUEVA bloquea el push. **dimension_baseline: 65 hallazgos preexistentes** de las 18 dimensiones, congelados como linea base: ninguna deuda vieja frena un commit, solo lo nuevo. Re-registrados los 5 hashes de confianza de los hooks contra el install pinneado, y `.claude/settings.json` resuelve `/opt/cerberus` (nunca un checkout de desarrollo). **Se restauro la regla `.protocol-core/` en `.gitignore`**, que una version anterior del de-vendorizado borraba: sin ella los 54 MB de copia derivada que los hooks materializan en runtime aparecian como untracked, a un `git add -A` de volver al repo (CC-99 en el nucleo; pasaba en 7 de 10 satelites). **VERIFICAR:** `git status` limpio tras el commit; los gates satelitales de pre-commit pasaron en vivo (hook-trust, estructura, gitleaks).
- 2026-07-31: Adoption finalized (adoption_verified true, core 7ccaf356): pinned hooks live, Spanish-identifier rename task registered in tasks/backlog/. Windows-only test module gated by tests/conftest.py off-platform; retired protocol-core bootstrap (sitecustomize) removed. Verify: git status clean, push gates green.
- 2026-07-31: Cerberus governance adopted; nothing else in flight.

## NEXT

- Fill in README.md and SPEC.md with the real content.

## VERIFY

- `python scripts/audit.py` exits 0.

## BLOCKERS

- None.
