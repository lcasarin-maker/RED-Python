# TODO / Pending Tasks

- [ ] **Revisar y actualizar el pre‑commit hook** para que la versión mostrada coincida con `VERSION.txt`.
- [ ] **Ejecutar `pre-commit install`** y validar que todos los hooks (black, ruff, mypy, rigor‑maestro) pasan.
- [ ] **Documentar el script `bump_version.py`** en `README.md` o en la sección de herramientas.
- [ ] **Añadir pruebas unitarias** para `scripts/bump_version.py` (incremento correcto de versiones y creación de tag).
- [ ] **Actualizar los archivos de protocolo** (`AGENT.md`, `PROTOCOL_SYSTEM.md`, `PROTOCOL_BEHAVIOR.md`) para reflejar la nueva versión `v0.02`.
- [ ] **Integrar generación automática de `docs/rules.md`** a partir de los archivos YAML de reglas.
- [ ] **Configurar CI/CD** (GitHub Actions) para ejecutar pruebas, lint y auditoría en cada push.
- [ ] **Revisar y cerrar tickets pendientes** en `pending_tasks.json` cuando se completen.
