# CODE_MAP - Core module map for Cerberus

## RED-Python satellite contract

This satellite exposes a smaller audit surface centered on the `dimensions/` package.
The contract below is the minimum wiring CC needs to understand the satellite's audit model.

- **[[dimensions_init]]** - package entry point and registry for the satellite audit dimensions.
- **[[dimensions_base]]** - base contract for `Status`, `Finding`, and the `Dimension` protocol.
- **[[dimensions_base_finding]]** - the `Finding` data model used by the audit dimensions.
- **[[dimensions_context]]** - `AuditContext`, the cached file/AST walk shared by the dimensions.

This map describes the **critical code surface** of Cerberus: the symbols that the internal graph
(`internal_graph.py` layer 1, via graphify) marks as `god_nodes` because of high coupling.
Documenting these hubs is the invariant that enforces `alignment_checker.py` (Phase 2): what is
architecturally central must be described here, with `[[links]]` that the linter resolves against
graph IDs (ergonomic aliases, Phase 2b).

> Honest scope: this doc covers the 14 *documentable* god_nodes. Mechanical graphify artifacts
> such as the `ast` import and the `*_py_path` constants are excluded because they are high-degree
> by mechanism, not by centrality. `entry_points` (`main()`) are not documented here: having
> `main()` does not make a symbol critical.

---

## 1. `protocol_engine/` - Protocol rules engine

The package that loads and resolves the rules/mandates of the agent-agnostic protocol.

- **[[engine_init]]** - `protocol_engine` package initialization; the rules engine entry point.
- **[[knowledge_loader_get_project_insights]]** - `knowledge_loader.get_project_insights() -> dict[str, str]`:
  collects the live project insights (state, learnings) used to orient the agent. High fan-in because
  multiple consumers call it to get context.

## 2. `scripts/core_utils.py` - Shared utilities

Cross-cutting utility module; a god_node by construction because most of the tree imports it.

- **[[core_utils]]** - the module itself: single source of process and environment helpers.
- **[[run_command]]** - `run_command(...)`: the single subprocess wrapper for controlled command
  execution (all callers pass lists; `shell=False`, see d7/B602). Centralizing this avoids
  `os.system` / `shell=True` sprawl (S7 Anti-Shell).
- **[[setup_windows_utf8]]** - `setup_windows_utf8() -> None`: forces UTF-8 on Windows consoles
  and avoids `UnicodeEncodeError` from emoji/accents in reports and hooks.

## 3. `scripts/protocol_cli.py` - Agnostic CLI client

The command-line facade for the protocol (`ProtocolClient`), a unified entry point for agents
(Claude/Gemini/Codex).

- **[[protocol_cli]]** - the client module.
- **[[protocolclient_run]]** - `ProtocolClient.run(argv) -> int`: main dispatch for protocol
  subcommands; converts `argv` into the governed action.
- **[[log_evidence]]** - `ProtocolClient.log_evidence(...)`: records empirical evidence
  (S9 Mandatory Logging / B7 Anti-Triumphalism: truth based on logs, not optimism).

## 4. `scripts/run_security_audit_12d.py` - 12D auditor (primary gatekeeper)

The forensic 12-dimensional auditor; the primary gate before every commit (S1 12D rigor).

- **[[security_audit_12d]]** - the auditor module.
- **[[deepforensicauditor_run]]** - `DeepForensicAuditor.run() -> bool`: runs the single pass
  over `AuditContext` (file list + AST only once), walks REGISTRY dimensions D1-D14, and emits
  APPROVED / REJECTED.

## 5. `scripts/validate_external_audit_phases.py` - External audit validator

Verifies that an external audit completed its phases (0-6) with real evidence, without skipping
the purge or declaring ceremonial greens.

- **[[validate_external_audit]]** - `validate_external_audit(target_root, results_dir) -> list[str]`:
  orchestrates phases 0-6 and returns the error list (empty = approved).
- **[[validate_phase_0]]** - `validate_phase_0(target_root, results_dir) -> list[str]`:
  validates Phase 0 (real pre-purge: that legacy controls are no longer active).
- **[[missing_files]]** - `_missing_files(results_dir, names)`: detects missing evidence artifacts.
- **[[phases_read_text]]** - `_read_text(path)`: tolerant reading used by most phases.

---

## Maintenance

If a symbol stops being a god_node or a new one appears, `alignment_checker` will report it.
With the gate enabled (`.protocol/align_gate.enabled`), a new critical god_node without an entry
here breaks the commit. Update this map instead of silencing the linter.
