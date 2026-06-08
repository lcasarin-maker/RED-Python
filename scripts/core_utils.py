#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CORE UTILITIES v5.1 - Centralized Shared Logic
Provides unified mechanisms for encoding, subprocess execution, database schemas,
and standard operations to prevent code duplication across the Fortress.
"""

import sys
import subprocess
import os
import sqlite3
from typing import Tuple, List, Union, Any
from pathlib import Path

# Common Paths
ROOT_DIR = Path("D:/GoogleDrive/AI")
PROTOCOL_SOURCE = ROOT_DIR / "Coder Cerberus V0.1"


def setup_windows_utf8() -> None:
    """
    Enforces UTF-8 encoding for standard output and standard error streams on Windows platforms.

    Inputs: None
    Outputs: Modifies sys.stdout and sys.stderr.
    Contract: If the platform is Windows, re-wraps the standard streams to ensure UTF-8 compatibility.
    """
    if sys.platform == "win32":
<<<<<<< HEAD
        # Skip reconfiguration during pytest to avoid capture buffer issues
        if os.getenv("PYTEST_CURRENT_TEST"):
            # No-op on Windows to avoid pytest capture buffer issues
            # Previously attempted to reconfigure stdout/stderr for UTF-8; this caused
            # "underlying buffer has been detached" errors during pytest teardown.
            # The default Python streams already handle UTF-8 on modern Windows,
            # so we safely skip any reconfiguration.
=======
        # Skip only when THIS process's stdout is a pytest capture wrapper (not inherited env var).
        # PYTEST_CURRENT_TEST is inherited by child subprocesses, which should still configure UTF-8.
        if (
            os.getenv("PYTEST_CURRENT_TEST")
            and "EncodedFile" in type(sys.stdout).__name__
        ):
>>>>>>> 78ec88b98ca24ad0cb22b1feab4464a88f41155b
            return
        try:
            if getattr(sys.stdout, "_vibecoderproof_utf8_wrapped", False):
                return
            sys.stdout.reconfigure(encoding="utf-8", errors="ignore")
            sys.stderr.reconfigure(encoding="utf-8", errors="ignore")
<<<<<<< HEAD
            setattr(sys.stdout, "_vibecoderproof_utf8_wrapped", True)
            setattr(sys.stderr, "_vibecoderproof_utf8_wrapped", True)
        except Exception:
            pass
=======
            setattr(sys.stdout, "_cerberus_utf8_wrapped", True)
            setattr(sys.stderr, "_cerberus_utf8_wrapped", True)
        except Exception as e:
            _logger.debug(
                "setup_windows_utf8: could not tag streams (read-only env): %s", e
            )
>>>>>>> 78ec88b98ca24ad0cb22b1feab4464a88f41155b


def run_command(
    command: List[str], timeout: int = 30, cwd: Union[str, Path] = None
) -> Tuple[int, str, str]:
    """
    Executes a list of arguments securely (shell=False) with standard UTF-8 capturing.

    Inputs:
        - command (List[str]): The command argv as a list (shell=False; B602).
        - timeout (int): Maximum execution time in seconds.
        - cwd (Union[str, Path]): Optional working directory.
    Outputs:
        - Tuple[int, str, str]: Returns (returncode, stdout, stderr).
    Contract: Runs a subprocess with standard capturing and timeout handling. Prevents hanging processes.
    """
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            timeout=timeout,
            shell=False,  # nunca shell=True (B602): todos los callers pasan listas
            cwd=cwd,
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired as e:
        return -1, "", f"Command timed out after {timeout}s: {e}"
    except Exception as e:
        return -1, "", f"Execution error: {e}"


def setup_common_db(db_path: Path) -> Tuple[sqlite3.Connection, Any]:
    """
    Initializes a sqlite3 database and returns a connection and cursor.

    Inputs: db_path (Path): Path to the sqlite3 database file.
    Outputs: Tuple[sqlite3.Connection, Any]: Database connection and cursor.
    Contract: Ensures the parent directory exists, connects to the database, and enables row factory.
    """
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    return conn, cursor


def setup_alerts_db(cursor: Any) -> None:
    """Create alerts table if not exists."""
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            severity TEXT CHECK(severity IN ('info', 'warn', 'error')),
            type TEXT,
            message TEXT,
            agent_id TEXT
        )
        """
    )


def setup_token_events_db(cursor: Any) -> None:
    """Create token_events table if not exists.

    Columns:
        id INTEGER PRIMARY KEY AUTOINCREMENT
        agent_id TEXT
        session_id TEXT
        model TEXT
        tokens_estimated INTEGER
        tokens_actual INTEGER
        cost_actual REAL
        note TEXT
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    """
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS token_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id TEXT,
            session_id TEXT,
            model TEXT,
            tokens_estimated INTEGER,
            tokens_actual INTEGER,
            cost_actual REAL,
            note TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

<<<<<<< HEAD
=======

def setup_sessions_db(cursor: Any) -> None:
    """Create sessions, rule_violations, state_checkpoints, agent_heartbeats tables.

    Rescued from deprecated/scripts/init_db.py — complete observability schema.
    Safe to call multiple times (CREATE TABLE IF NOT EXISTS).
    GF-5 / VC-039 declared debt: schema defined, not yet wired to any runtime caller.
    Kept for future observability integration. Do not delete without grepping callers.
    """
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            agent_name TEXT,
            project_name TEXT,
            start_time TIMESTAMP,
            end_time TIMESTAMP,
            task_description TEXT,
            files_modified INTEGER,
            lines_changed INTEGER,
            status TEXT CHECK(status IN ('COMPLETED', 'BLOCKED', 'IN_PROGRESS')),
            token_budget_used INTEGER,
            token_budget_allocated INTEGER
        )
    """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS rule_violations (
            id TEXT PRIMARY KEY,
            session_id TEXT,
            rule_number INTEGER,
            violation_type TEXT,
            severity TEXT CHECK(severity IN ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW')),
            resolution_status TEXT,
            timestamp TIMESTAMP
        )
    """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS state_checkpoints (
            id TEXT PRIMARY KEY,
            session_id TEXT,
            project_name TEXT,
            files_snapshot TEXT,
            state_hash TEXT,
            conflict_detection BOOLEAN,
            timestamp TIMESTAMP
        )
    """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS agent_heartbeats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            agent_id TEXT,
            status TEXT CHECK(status IN ('alive', 'idle', 'working', 'blocked')),
            context_usage_percent REAL,
            token_usage_percent REAL,
            historial_last_modified DATETIME
        )
    """
    )


>>>>>>> 78ec88b98ca24ad0cb22b1feab4464a88f41155b
def get_centralized_version() -> str:
    """
    Reads the current version from the centralized VERSION.txt file in the root.
    """
    version_file = Path(__file__).parent.parent / "VERSION.txt"
    if version_file.exists():
        return version_file.read_text(encoding="utf-8").strip()
    return "UNKNOWN"

<<<<<<< HEAD
=======

def write_json_atomic(path, data, indent: int = 2) -> None:
    """VC-117: escritura atómica de estado crítico (JSON). Escribe a un temporal en el
    MISMO directorio y hace os.replace (atómico en el mismo filesystem). Un crash o kill
    a mitad de escritura NO deja el archivo destino corrupto ni vacío."""
    import json
    import tempfile

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(
        dir=str(path.parent), prefix="." + path.name + ".", suffix=".tmp"
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError as cleanup_exc:
            logging.debug(
                "write_json_atomic: no se pudo limpiar tmp %s: %s", tmp, cleanup_exc
            )
        raise


# ---------------------------------------------------------------------------
# P6.8 — Compact check helpers (pure read-only, no side effects).
# Shared between protocol_cli.py and any future consumers.
# Full compaction action lives in token_manager.TokenOptimizer.check_and_compact().
# ---------------------------------------------------------------------------

_COMPACT_SESSION_THRESHOLD = 45
_COMPACT_CONTEXT_FILES = ("HISTORIAL.md", "STATUS.md", "AGENT.md", "CLAUDE.md")
# File-size PROXY for compact trigger — NOT tokens, NOT context window.
# See TOKEN_BUDGET.md: context window = 200K tokens; session budget = 150K tokens (TOKEN_BUDGET).
_COMPACT_BYTES_LIMIT = 100_000


def get_historical_path(project_dir: Path) -> Path:
    """Returns the isolated HISTORIAL.md path. Wires it into .protocol-core/ if running in a satellite."""
    if (project_dir / ".protocol-core").exists():
        return project_dir / ".protocol-core" / "HISTORIAL.md"
    return project_dir / "HISTORIAL.md"


def get_state_json_path(project_dir: Path) -> Path:
    """Returns the isolated .agent_state.json path for satellite isolation."""
    if (project_dir / ".protocol-core").exists():
        return project_dir / ".protocol-core" / ".agent_state.json"
    return project_dir / ".agent_state.json"


def get_status_md_path(project_dir: Path) -> Path:
    """Returns the isolated STATUS.md path for satellite isolation."""
    if (project_dir / ".protocol-core").exists():
        return project_dir / ".protocol-core" / "STATUS.md"
    return project_dir / "STATUS.md"


def check_compact_sessions(
    project_dir: Path, threshold: int = _COMPACT_SESSION_THRESHOLD
):
    """Return result dict if HISTORIAL.md has >threshold sessions; else None. No side effects."""
    hp = get_historical_path(project_dir)
    if not hp.exists():
        return None
    try:
        lines = hp.read_text(encoding="utf-8", errors="ignore").splitlines()
        count = sum(
            1
            for ln in lines
            if ln.startswith("## SESIÓN") or ln.startswith("## SESSION")
        )
        if count > threshold:
            print(
                f"[ACTION] COMPACT recommended: {count} sessions found (>{threshold} threshold)"
            )
            return {"action": "COMPACT_RECOMMENDED", "sessions": count}
    except Exception as exc:
        _logger.warning("check_compact_sessions failed: %s", exc)
    return None


def check_compact_threshold(
    project_dir: Path, max_bytes: int = _COMPACT_BYTES_LIMIT
) -> dict:
    """Calculate context file sizes as %% of byte budget. Returns status dict. No side effects."""
    total = sum(
        (
            get_historical_path(project_dir).stat().st_size
            if f == "HISTORIAL.md"
            else (
                get_status_md_path(project_dir).stat().st_size
                if f == "STATUS.md"
                else (
                    (project_dir / f).stat().st_size
                    if (project_dir / f).exists()
                    else 0
                )
            )
        )
        for f in _COMPACT_CONTEXT_FILES
    )
    pct = min(round(total / max_bytes * 100, 1), 100.0)
    status = "SAFE" if pct < 70 else ("WARNING" if pct < 85 else "COMPACT_NOW")
    return {"context_pct": pct, "total_bytes": total, "status": status}
>>>>>>> 78ec88b98ca24ad0cb22b1feab4464a88f41155b
