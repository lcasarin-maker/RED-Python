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
        # Skip reconfiguration during pytest to avoid capture buffer issues
        if os.getenv("PYTEST_CURRENT_TEST"):
            # No-op on Windows to avoid pytest capture buffer issues
            # Previously attempted to reconfigure stdout/stderr for UTF-8; this caused
            # "underlying buffer has been detached" errors during pytest teardown.
            # The default Python streams already handle UTF-8 on modern Windows,
            # so we safely skip any reconfiguration.
            return
        try:
            if getattr(sys.stdout, "_vibecoderproof_utf8_wrapped", False):
                return
            sys.stdout.reconfigure(encoding="utf-8", errors="ignore")
            sys.stderr.reconfigure(encoding="utf-8", errors="ignore")
            setattr(sys.stdout, "_vibecoderproof_utf8_wrapped", True)
            setattr(sys.stderr, "_vibecoderproof_utf8_wrapped", True)
        except Exception:
            pass

def run_command(command: Union[List[str], str], timeout: int = 30, cwd: Union[str, Path] = None) -> Tuple[int, str, str]:
    """
    Executes a shell command or list of arguments securely with standard UTF-8 capturing.

    Inputs:
        - command (Union[List[str], str]): The command to execute.
        - timeout (int): Maximum execution time in seconds.
        - cwd (Union[str, Path]): Optional working directory.
    Outputs:
        - Tuple[int, str, str]: Returns (returncode, stdout, stderr).
    Contract: Runs a subprocess with standard capturing and timeout handling. Prevents hanging processes.
    """
    try:
        is_shell = isinstance(command, str)
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',
            timeout=timeout,
            shell=is_shell,
            cwd=cwd
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

def get_centralized_version() -> str:
    """
    Reads the current version from the centralized VERSION.txt file in the root.
    """
    version_file = Path(__file__).parent.parent / "VERSION.txt"
    if version_file.exists():
        return version_file.read_text(encoding='utf-8').strip()
    return "UNKNOWN"

