# CODE_MAP — Mapa de los módulos núcleo de Cerberus

Mapa de la **superficie crítica de código** de Cerberus: los símbolos que el grafo interno
(`internal_graph.py` Capa 1, vía graphify) marca como `god_nodes` por alto grado de
acoplamiento. Documentar estos hubs es el invariante que enforça `alignment_checker.py`
(Fase 2): lo que es arquitectónicamente central debe estar descrito aquí, con `[[enlaces]]`
que el linter resuelve contra los ids del grafo (alias ergonómicos, Fase 2b).

> Alcance honesto: este doc cubre los 14 god_nodes *documentables* (se excluyen los
> artefactos mecánicos de graphify: el import `ast` y las constantes `*_py_path` de cada
> módulo, que son alto-grado por mecanismo, no por centralidad). Los `entry_points` (todo
> `main()`) no se documentan aquí: tener `main()` no es criticidad.

---

## 1. `protocol_engine/` — Motor de reglas del protocolo

El paquete que carga y resuelve las reglas/mandatos del protocolo agent-agnóstico.

- **[[engine_init]]** — inicialización del paquete `protocol_engine`: punto de entrada del
  motor de reglas; expone el namespace que el resto del sistema importa.
- **[[knowledge_loader_get_project_insights]]** — `knowledge_loader.get_project_insights() -> dict[str, str]`:
  reúne los insights vivos del proyecto (estado, aprendizajes) que alimentan el contexto del
  agente. Alto fan-in porque varios consumidores lo invocan para situarse.

## 2. `scripts/core_utils.py` — Utilidades compartidas

Módulo de utilidades transversales; god_node por construcción (casi todo el árbol lo importa).

- **[[core_utils]]** — el módulo: single source de helpers de proceso y entorno.
- **[[run_command]]** — `run_command(...)`: envoltura única de subprocess para ejecutar
  comandos de forma controlada (todos los callers pasan listas; `shell=False`, ver d7/B602).
  Centralizar aquí evita `os.system`/`shell=True` dispersos (S7 Anti-Shell).
- **[[setup_windows_utf8]]** — `setup_windows_utf8() -> None`: fuerza la consola a UTF-8 en
  Windows (evita `UnicodeEncodeError` cp1252 en emojis/acentos de los reportes y hooks).

## 3. `scripts/protocol_cli.py` — Cliente CLI agnóstico

La fachada de línea de comandos del protocolo (`ProtocolClient`), entrada privilegiada
unificada para agentes (Claude/Gemini/Codex).

- **[[protocol_cli]]** — el módulo del cliente CLI.
- **[[protocolclient_run]]** — `ProtocolClient.run(argv) -> int`: dispatch principal de
  subcomandos del protocolo; convierte `argv` en la acción gobernada correspondiente.
- **[[log_evidence]]** — `ProtocolClient.log_evidence(...)`: registra evidencia empírica
  (S9 Logging Mandatorio / B7 Anti-Triunfalismo: verdad basada en logs, no en optimismo).

## 4. `scripts/run_security_audit_12d.py` — Auditor 12D (gatekeeper primario)

El auditor forense de 12 dimensiones; gate primario antes de cada commit (S1 Rigor 12D).

- **[[security_audit_12d]]** — el módulo del auditor.
- **[[deepforensicauditor_run]]** — `DeepForensicAuditor.run() -> bool`: ejecuta la pasada
  única sobre `AuditContext` (file_list + AST una sola vez) recorriendo el REGISTRY de
  dimensiones D1–D14 y emite el veredicto APPROVED/REJECTED.

## 5. `scripts/validate_external_audit_phases.py` — Validador de auditoría externa

Verifica que una auditoría exterior cumplió sus fases (0–6) con evidencia real, sin saltarse
la purga ni declarar verdes ceremoniales.

- **[[validate_external_audit]]** — `validate_external_audit(target_root, results_dir) -> list[str]`:
  orquestador que corre las fases 0–6 y devuelve la lista de errores (vacía = aprobado).
- **[[validate_phase_0]]** — `validate_phase_0(target_root, results_dir) -> list[str]`:
  valida la Fase 0 (purga previa real: que los controles legacy no sigan activos).
- **[[validate_external_audit]]** y las fases comparten dos helpers de alto fan-in:
  - **[[missing_files]]** — `_missing_files(results_dir, names)`: detecta artefactos de
    evidencia ausentes (un reporte de fase incompleto no es un verde).
  - **[[phases_read_text]]** — `_read_text(path)`: lectura tolerante de los artefactos de
    evidencia que casi todas las fases consumen.

---

**Mantenimiento:** si un símbolo deja de ser god_node (refactor que baja su grado) o aparece
uno nuevo, `alignment_checker` lo reportará. Con el gate activo
(`.protocol/align_gate.enabled`), un god_node crítico nuevo sin entrada aquí **rompe el
commit** — actualiza este mapa, no silencies el linter.
