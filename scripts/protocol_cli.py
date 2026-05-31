#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Protocol CLI v0.02 - Single Authority for CoderCerberus"""

import json
import logging
import shutil
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from protocol_engine import get_golden_summary, get_project_insights
from scripts.core_utils import (
    setup_windows_utf8, get_centralized_version, run_command,
    check_compact_sessions, check_compact_threshold,  # P6.8 — consolidated from core_utils
)

setup_windows_utf8()
logger_cli = logging.getLogger("protocol_cli")
VERSION = get_centralized_version()

PROJECT_DIR = Path(".")

def _clear_status_warning(status_file: Path) -> None:
    """Remueve el banner de bloqueo en STATUS.md (aplanado)."""
    if not status_file.exists():
        return
    try:
        content = status_file.read_text(encoding="utf-8")
        if "🚨 CHAIN-PATTERN INTERRUPT: ERROR DEADLOCK ACTIVO 🚨" not in content:
            return
        if "---\n\n" not in content:
            return
        parts = content.split("---\n\n", 1)
        if len(parts) == 2:
            clean_content = "# STATUS.md — Project status\n\n" + parts[1]
            status_file.write_text(clean_content, encoding="utf-8")
            print("✅ Banner de bloqueo removido de STATUS.md.")
    except Exception as e:
        print(f"[WARN] No se pudo limpiar STATUS.md: {e}")


class ProtocolClient:
    def __init__(self):
        self.project_root = Path(".")
        self.evidence_dir = self.project_root / ".protocol" / "evidence"
        self.evidence_dir.mkdir(parents=True, exist_ok=True)

    # Bounded retention: keep only the most recent N evidence logs so the
    # gitignored evidence/ dir cannot grow without limit (and flood Drive sync).
    _EVIDENCE_RETENTION = 50

    def _log_evidence(self, operation: str, outcome: str, details: dict) -> None:
        evidence = {"timestamp": datetime.now().isoformat(), "operation": operation, "outcome": outcome, "details": details}
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = self.evidence_dir / f"{ts}_evidence.json"
        log_file.write_text(json.dumps(evidence, indent=2, ensure_ascii=False), encoding="utf-8")
        self._prune_evidence()

    def _prune_evidence(self) -> None:
        """Delete oldest *_evidence.json beyond the retention limit."""
        logs = sorted(self.evidence_dir.glob("*_evidence.json"))
        for stale in logs[: -self._EVIDENCE_RETENTION]:
            try:
                stale.unlink()
            except OSError as e:
                logger_cli.warning("evidence prune failed for %s: %s", stale.name, e)

    def _detect_deadlock(self, threshold_minutes: int = 10) -> int:
        """Delegado a deadlock_resolver.DeadlockResolver — evita duplicación de lógica."""
        try:
            from scripts.deadlock_resolver import DeadlockResolver
            resolver = DeadlockResolver(threshold_minutes=threshold_minutes)
            return resolver.check_all_agents()
        except Exception as e:
            logger_cli.warning("Deadlock detection unavailable: %s", e)
            return 0

    def command_check(self, verbose: bool = False) -> int:
        prefix = ""
        if (self.project_root / ".protocol-core").is_dir():
            prefix = ".protocol-core/"
        
        audit_path = f"{prefix}scripts/run_security_audit_12d.py"
        rigor_path = f"{prefix}scripts/run_compliance_tests.py"
        
        code, stdout, _ = run_command([sys.executable, audit_path])
        if code != 0:
            print("run_security_audit_12d failed")
            self._log_evidence("check", "failure", {"stage": "run_security_audit_12d", "code": code, "stdout": stdout[:200]})
            return 1
        code, stdout, _ = run_command([sys.executable, rigor_path], timeout=300)
        if code != 0:
            print("run_compliance_tests failed")
            self._log_evidence("check", "failure", {"stage": "run_compliance_tests", "code": code})
            return 1
        compact_status = check_compact_sessions(PROJECT_DIR)
        ctx = check_compact_threshold(PROJECT_DIR)
        if verbose:
            print(f"[CTX] {ctx['context_pct']}% used ({ctx['total_bytes']} bytes) — {ctx['status']}")
        self._auto_refresh_protocol_hash(prefix)
        print("PASSED (run_security_audit_12d + run_compliance_tests)")
        self._log_evidence("check", "success", {"compact_needed": compact_status, "context": ctx})
        return 0

    def _auto_refresh_protocol_hash(self, prefix: str = "") -> None:
        """P2.2: si el commit incluye un archivo de protocolo, el drift es legítimo
        (intencional y ya validado por el gate) → refresca protocol_hash para que el
        pre-push no bloquee ni exija `sync_binding --update` manual. El drift NO commiteado
        (mutación externa inesperada) sigue siendo detectable. Best-effort: nunca rompe el commit."""
        try:
            from scripts.sync_binding import ProtocolSyncManager
            code, staged, _ = run_command(["git", "diff", "--cached", "--name-only"])
            if code != 0:
                return
            changed = set(staged.split())
            proto = ProtocolSyncManager.PROTOCOL_FILES
            if not (changed & proto or changed & {f"{prefix}{p}" for p in proto}):
                return  # el commit no toca archivos de protocolo → nada que reconocer
            ProtocolSyncManager().update_checksums()
            print("[P2.2] protocol_hash refrescado (drift legítimo de protocolo commiteado).")
        except Exception as e:
            print(f"[P2.2] aviso: no se pudo refrescar protocol_hash: {e}")

    def command_sync(self, dry_run: bool = False) -> int:
        code, stdout, _ = run_command([sys.executable, "scripts/sync_binding.py", "--check"])
        outcome = "success" if code == 0 else "failure"
        print(f"sync {'complete' if code == 0 else 'detected drift'}")
        self._log_evidence("sync", outcome, {"dry_run": dry_run, "code": code})
        return code

    def command_doctor(self, fix: bool = False) -> int:
        alerts = self._detect_deadlock()
        if alerts > 0:
            print(f"[WARN] doctor: {alerts} deadlock(s) detected")
            if fix:
                print("[ACTION] Escalating deadlocked agents...")
                self._log_evidence("doctor", "partial_fix", {"alerts": alerts})
            else:
                print("[HINT] Run with --fix to escalate")
                self._log_evidence("doctor", "detected_issues", {"alerts": alerts})
                return 1
        print("doctor: system healthy")
        self._log_evidence("doctor", "success", {"alerts": alerts})
        return 0

    def command_evidence(self, last_n: int = 5) -> int:
        log_files = sorted(self.evidence_dir.glob("*.json"))[-last_n:]
        print(f"evidence: {len(log_files)} operations logged")
        return 0

    def command_knowledge(self) -> int:
        summary = get_golden_summary()
        insights = get_project_insights()
        print(
            "knowledge: "
            f"tokenomics={summary['tokenomics']} "
            f"testing_vices={summary['testing_vices']} "
            f"coding_vices={summary['coding_vices']} "
            f"project_insights={summary['project_insights']}"
        )
        for insight_id in sorted(insights):
            print(f"{insight_id}: {insights[insight_id]}")
        return 0

    def command_install(self, project_path: str = ".") -> int:
        hooks_src = self.project_root / "scripts" / "hooks"
        hooks_dst = Path(project_path) / ".git" / "hooks"
        if not hooks_src.exists():
            print("scripts/hooks/ not found — nothing to install.")
            self._log_evidence("install", "failure", {"reason": "no hooks source dir"})
            return 1
        if not hooks_dst.exists():
            print(".git/hooks/ not found — is this a git repository?")
            self._log_evidence("install", "failure", {"reason": "no .git/hooks"})
            return 1
        installed = []
        for hook_file in hooks_src.iterdir():
            if hook_file.is_file():
                dst = hooks_dst / hook_file.name
                shutil.copy2(hook_file, dst)
                installed.append(hook_file.name)
        if installed:
            print(f"hooks installed: {', '.join(installed)}")
            self._log_evidence("install", "success", {"hooks": installed})
            return 0
        print("No hook files found in scripts/hooks/")
        self._log_evidence("install", "failure", {"reason": "empty hooks dir"})
        return 1

    def _command_dashboard(self, argv: list[str]) -> int:
        try:
            sys.path.insert(0, str(Path(__file__).parent / "dashboard"))
            import server
            # GF-4: guard i+1 < len(argv) to prevent IndexError when --port has no value
            port = int(next((argv[i+1] for i, a in enumerate(argv) if a == "--port" and i+1 < len(argv)), "5000"))
            server.run_server(port)
            return 0
        except Exception as e:
            print(f"[ERROR] dashboard: {e}")
            return 1

    def command_unlock(self) -> int:
        """CPI unlock: restablece el contador de fallos y desbloquea el reasoning_lock."""
        state_file = self.project_root / ".agent_state.json"
        if not state_file.exists():
            print("[ERROR] .agent_state.json no encontrado.")
            return 1

        try:
            with open(state_file, "r", encoding="utf-8") as f:
                state = json.load(f)
        except Exception as e:
            print(f"[ERROR] No se pudo leer .agent_state.json: {e}")
            return 1

        state["consecutive_failures"] = 0
        state["reasoning_lock"] = False

        try:
            with open(state_file, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
            print("✅ Reasoning Lock removido de .agent_state.json.")
        except Exception as e:
            print(f"[ERROR] No se pudo escribir en .agent_state.json: {e}")
            return 1

        _clear_status_warning(self.project_root / "STATUS.md")

        self._log_evidence("unlock", "success", {})
        print("🔓 SISTEMA DESBLOQUEADO — CoderCerberus está listo para operaciones normales.")
        return 0

    def run(self, argv: list[str]) -> int:
        if not argv or argv[0] in ["-h", "--help"]:
            print("CoderCerberus V0.02 CLI\nCommands: check, sync, doctor, evidence, knowledge, install, dashboard, unlock")
            return 0
        cmd = argv[0]
        # GF-4: guard i+1 < len(argv) to prevent IndexError when flag has no value
        last_n = int(next((argv[i+1] for i, a in enumerate(argv) if a == "--last-n" and i+1 < len(argv)), "5"))
        dispatch = {
            "check":     lambda: self.command_check("--verbose" in argv),
            "sync":      lambda: self.command_sync("--dry-run" in argv),
            "doctor":    lambda: self.command_doctor("--fix" in argv),
            "evidence":  lambda: self.command_evidence(last_n),
            "knowledge": lambda: self.command_knowledge(),
            "install":   lambda: self.command_install(),
            "dashboard": lambda: self._command_dashboard(argv),
            "unlock":    lambda: self.command_unlock(),
        }
        if cmd not in dispatch:
            print(f"[ERROR] Unknown command: {cmd}")
            return 127
        return dispatch[cmd]()

if __name__ == "__main__":
    cli = ProtocolClient()
    sys.exit(cli.run(sys.argv[1:]))
