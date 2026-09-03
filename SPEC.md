---
spec_version: 2
id: red_python
kind: research
owner: lcasarin@gmail.com
runtime: null
scaffold: {name: simplecode, mode: vendored}
ledger: ledger/entries
gate_level: legacy-baseline
---

> **Front-matter tipado anadido el 2026-09-02** (canon de la flota, DGX-424). **El cuerpo
> de abajo NO se toco**: se conserva palabra por palabra.
>
> Falta la seccion `## Requirements` con requisitos EARS y su `verify:`, y falta a
> proposito: **la escribe quien conoce este repo**. Redactarla desde fuera seria elegir
> el comando facil de pasar en vez del que importa, que es el fraude que el canon existe
> para impedir. `gate_level: legacy-baseline` declara honestamente que hay deuda
> historica aceptada, en vez de un gate estricto con excepciones invisibles.

# 🧠 SPEC.md — The Brain of RED-Python
**Status:** 💎 SINGLE SOURCE OF TRUTH | Version: v1.0

---

## 0. Objective

**Mission**: Let a user find and safely remove empty directories on their filesystem, from the GUI or the CLI, without ever deleting a directory that holds real data.

## Purpose
RED-Python (Remove Empty Directories) is a desktop utility and CLI tool that scans a filesystem tree, identifies directories that are empty or contain only ignorable files (hidden, system, zero-byte, or filter-matched), and removes them under explicit user control.

## Why now
Empty directories accumulate silently after installers, build tooling, and file-sync clients run their course, cluttering the filesystem with no automated, safe way to reclaim it. RED-Python exists to close that gap without risking real data.

## Who is the user
A Windows desktop user cleaning up their own filesystem, interactively (GUI) or via scripted/scheduled scans (CLI `--scan`).

## In scope
- Scanning a filesystem tree for empty or ignorable-only directories.
- Deleting/moving matched directories under an explicit delete mode chosen by the user.
- Configurable filter rules (regex, wildcard, exact match) and protected-directory exclusions.
- Windows Explorer context-menu integration.
- GUI (Tkinter) and CLI (`--scan`) entry points.

## Out of scope
- Non-Windows shell integration.
- Deleting directories that contain any file not covered by the configured ignore rules.
- Cloud storage or network filesystem-specific handling.

## Constraints
Python version: 3.11+
Deployment target: local desktop (Windows), packaged via PyInstaller (`red.spec`).

## ADRs
| ADR | Decision | Status |
| --- | --- | --- |
| 0001 | Tkinter for the GUI (stdlib, no extra runtime dependency) | Accepted |
| 0002 | Daemon threads for scan/clean to keep the UI responsive | Accepted |

## Risks
| Risk | Likelihood | Mitigation |
| --- | --- | --- |
| Deleting a directory that turns out not to be empty | Low | Emptiness check re-validated immediately before removal; ignorable-file allowlist is conservative by default |
| Windows Registry corruption from context-menu install | Low | Registry writes scoped to a single `Directory\shell\RED-Python` key, with an explicit uninstall path |

## Acceptance Criteria
- `pytest` passes with the full test suite.
- `simplecode spec check` passes.
- Scanning and cleaning never remove a directory containing a non-ignorable file.

---

## 🏗️ ARCHITECTURE AND PURPOSE
This repository contains **RED-Python** (Remove Empty Directories). It is a desktop utility and CLI tool for finding and safely removing empty directories on a user's filesystem.

## 🎨 SYSTEM PATTERNS (Design Philosophy)
1. **Safety First:** Directories are only removed if they are truly empty or contain only ignorable files (like hidden files or empty files, per user configuration).
2. **Dual Mode:** The application can run as a graphical user interface (GUI) or as a command-line interface (CLI) with the `--scan` flag.
3. **Shell Integration:** RED-Python can integrate with the Windows context menu, allowing users to right-click a folder in Explorer and select "Remove Empty Directories".
4. **Daemon Threads:** Scanning and cleaning operations run in background threads to keep the UI responsive.

## 🦴 ARCHITECTURAL COMPONENTS

The core application logic is split into several focused modules:

1. **`red.py`**: The main entry point. Routes execution to the CLI or the GUI depending on arguments.
2. **`app.py`**: The Tkinter-based Graphical User Interface. Handles user interactions, settings, and progress reporting.
3. **`core.py`**: Contains the `Scanner` and `Cleaner` logic which traverse the filesystem and handle removals.
4. **`filters.py`**: A dedicated module for evaluating file and directory exclusion rules (regex, wildcards, exact matches).
5. **`config.py`**: Manages the persistence of user settings (e.g., `delete_mode`, `filter_rules`, `protected_dirs`) in a JSON file.
6. **`shell_integration.py`**: Provides the Windows Registry hooks to add RED-Python to the Explorer context menu.

### Administrative / Governance Scripts
- **`scripts/satellite_governance.py`**: Audits and manages repository rules.
- **`scripts/validate_retrospective.py`**: Validates the schema of post-session retrospectives in `HISTORIAL.md`.

### Testing
- **`tests/`**: Pytest test suite covering UI smoke tests, core behavior, filter rules, CLI parsing, and shell integration.

---

## 🛡️ WHITELIST (War Inventory)
Only the following key operational paths exist and are governed in this repository:

1. `red.py`
2. `app.py`
3. `core.py`
4. `config.py`
5. `filters.py`
6. `shell_integration.py`
7. `scripts/satellite_governance.py`
8. `scripts/validate_retrospective.py`
9. `tests/test_config_and_bootstrap.py`
10. `tests/test_filters.py`
11. `tests/test_gui_smoke.py`
12. `tests/test_main_cli.py`
13. `tests/test_red_core_behaviour.py`
14. `tests/test_regla_21_retrospective.py`
15. `tests/test_satellite_governance.py`
16. `tests/test_shell_and_app.py`
17. `tests/test_test_surface.py`
18. `tests/conftest.py`
19. `docs/`
20. `Wiki/`
21. `SPEC.md`
22. `README.md`
