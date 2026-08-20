# 🧠 SPEC.md — The Brain of RED-Python
**Status:** 💎 SINGLE SOURCE OF TRUTH | Version: v1.0

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
