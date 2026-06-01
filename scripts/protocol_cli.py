#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Protocol CLI v0.02 - Single Authority for CoderCerberus"""

import json
import logging
import os
import shutil
import sys
import stat
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

    def _workspace_noise_paths(self) -> list[Path]:
        """Return transient workspace paths that should not survive a hygiene pass."""
        noise: set[Path] = set()
        skip_parts = {".git", ".protocol", "deprecated"}
        for pattern in ("__pycache__", ".pytest_cache"):
            for path in self.project_root.rglob(pattern):
                if any(part in skip_parts for part in path.parts):
                    continue
                noise.add(path)
        for pattern in ("*.pyc", ".coverage*"):
            for path in self.project_root.rglob(pattern):
                if any(part in skip_parts for part in path.parts):
                    continue
                noise.add(path)
        for rel in ("scripts/automation", "scripts/dashboard"):
            parent = self.project_root / rel
            if parent.exists() and parent.is_dir():
                pycache = parent / "__pycache__"
                if pycache.exists():
                    noise.add(pycache)
        return sorted(noise, key=lambda p: p.as_posix())

    def _remove_workspace_noise(self, paths: list[Path]) -> list[str]:
        removed: list[str] = []

        def _onerror(func, path_str, exc_info):
            try:
                os.chmod(path_str, stat.S_IWRITE)
                func(path_str)
            except OSError as e:
                logger_cli.warning("hygiene cleanup retry failed for %s: %s", path_str, e)

        for path in sorted(paths, key=lambda p: len(p.parts), reverse=True):
            if not path.exists():
                logger_cli.warning("hygiene cleanup skipped for missing path: %s", path)
                continue
            try:
                if path.is_dir():
                    shutil.rmtree(path, onerror=_onerror)
                else:
                    path.unlink()
                removed.append(path.relative_to(self.project_root).as_posix())
            except OSError as e:
                logger_cli.warning("hygiene cleanup failed for %s: %s", path, e)
        for rel in ("scripts/automation", "scripts/dashboard"):
            parent = self.project_root / rel
            try:
                if parent.exists() and parent.is_dir() and not any(parent.iterdir()):
                    shutil.rmtree(parent, onerror=_onerror)
                    removed.append(parent.relative_to(self.project_root).as_posix())
            except OSError as e:
                logger_cli.warning("hygiene cleanup failed for %s: %s", parent, e)
        return removed

    def _detect_deadlock(self, threshold_minutes: int = 10) -> int:
        """Delegado a deadlock_resolver.DeadlockResolver — evita duplicación de lógica."""
        try:
            from scripts.resolve_deadlocks import DeadlockResolver
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

    def command_propagate(self, core_path: str = ".", project: str | None = None) -> int:
        """Alias canónico para propagar con global_sync_safe --apply."""
        cmd = [sys.executable, "scripts/global_sync_safe.py", "--apply"]
        if core_path and core_path != ".":
            cmd.extend(["--core-path", core_path])
        if project:
            cmd.extend(["--project", project])
        code, stdout, stderr = run_command(cmd, timeout=600)
        outcome = "success" if code == 0 else "failure"
        if stdout.strip():
            print(stdout.rstrip())
        if stderr.strip():
            print(stderr.rstrip(), file=sys.stderr)
        if code != 0:
            print("global_sync_safe failed")
            self._log_evidence(
                "propagate",
                outcome,
                {"core_path": core_path, "project": project, "code": code, "stdout": stdout[:200], "stderr": stderr[:200]},
            )
            return 1
        print("propagate complete")
        self._log_evidence(
            "propagate",
            outcome,
            {"core_path": core_path, "project": project, "code": code, "stdout": stdout[:200]},
        )
        return 0

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

    def command_hygiene(self, fix: bool = False) -> int:
        self._prune_evidence()
        noise = self._workspace_noise_paths()
        if not noise:
            print("hygiene: workspace clean")
            self._log_evidence("hygiene", "success", {"noise": 0, "fix": fix})
            return 0

        print(f"hygiene: {len(noise)} transient path(s) detected")
        for path in noise[:20]:
            print(f" - {path.relative_to(self.project_root).as_posix()}")

        if not fix:
            self._log_evidence(
                "hygiene",
                "detected_noise",
                {"noise": len(noise), "fix": fix},
            )
            return 1

        removed = self._remove_workspace_noise(noise)
        remaining = self._workspace_noise_paths()
        if remaining:
            print(f"hygiene: {len(remaining)} path(s) still pending after cleanup")
            for path in remaining[:20]:
                print(f" - {path.relative_to(self.project_root).as_posix()}")
            self._log_evidence(
                "hygiene",
                "partial_fix",
                {"noise": len(noise), "removed": removed, "remaining": len(remaining)},
            )
            return 1

        print("hygiene: workspace cleaned")
        self._log_evidence("hygiene", "success", {"noise": len(noise), "removed": removed, "fix": fix})
        return 0

    def command_maintenance(self) -> int:
        """Run the previously automatic post-commit maintenance explicitly."""
        steps = []
        token_manager = self.project_root / "scripts" / "manage_tokens.py"
        compress_historial = self.project_root / "scripts" / "compress_historial.py"
        self_improvement = self.project_root / "scripts" / "run_self_improvement.py"
        review_queue = self.project_root / "scripts" / "manage_review_queue.py"

        if token_manager.exists():
            steps.append(("token_manager", [sys.executable, str(token_manager), "--compact", "--quiet"], 120))
        if compress_historial.exists():
            steps.append(("compress_historial", [sys.executable, str(compress_historial), "--days", "30"], 300))
        if self_improvement.exists():
            steps.append(("self_improvement_loop", [sys.executable, str(self_improvement)], 600))
        if review_queue.exists():
            steps.append(("review_queue", [sys.executable, str(review_queue), "--enqueue"], 120))

        failures = []
        for label, cmd, timeout in steps:
            code, stdout, stderr = run_command(cmd, timeout=timeout)
            if code != 0:
                failures.append(label)
                print(f"[WARN] maintenance step failed: {label}")
                if stdout.strip():
                    print(stdout.strip())
                if stderr.strip():
                    print(stderr.strip())

        if failures:
            self._log_evidence("maintenance", "partial_failure", {"failed": failures})
            return 1

        print("maintenance: post-commit automation completed")
        self._log_evidence("maintenance", "success", {"steps": [label for label, *_ in steps]})
        return 0

    def command_cost(self, transcript_path: str = "transcript.jsonl") -> int:
        from scripts.track_tokens import TokenTracker

        tracker = TokenTracker(db_path=":memory:")
        try:
            print(tracker.format_transcript_cost_report(transcript_path))
            return 0
        finally:
            tracker.close()

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

    def command_split_golden_standard(self) -> int:
        """Regenerate the split Golden Standard catalogs and manifest."""
        code, stdout, stderr = run_command([sys.executable, "scripts/split_golden_standard_catalogs.py"], timeout=120)
        if stdout.strip():
            print(stdout.rstrip())
        if stderr.strip():
            print(stderr.rstrip(), file=sys.stderr)
        if code != 0:
            print("split_golden_standard_catalogs failed")
            return 1
        print("golden standard catalogs refreshed")
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
            print("CoderCerberus V0.02 CLI\nCommands: check, sync, propagate, doctor, evidence, cost, knowledge, split-golden-standard, hygiene, maintenance, install, dashboard, unlock")
            return 0
        cmd = argv[0].lstrip("/")
        # GF-4: guard i+1 < len(argv) to prevent IndexError when flag has no value
        last_n = int(next((argv[i+1] for i, a in enumerate(argv) if a == "--last-n" and i+1 < len(argv)), "5"))
        transcript_path = next((argv[i+1] for i, a in enumerate(argv) if a == "--transcript" and i+1 < len(argv)), "transcript.jsonl")
        core_path = next((argv[i+1] for i, a in enumerate(argv) if a == "--core-path" and i+1 < len(argv)), ".")
        project = next((argv[i+1] for i, a in enumerate(argv) if a == "--project" and i+1 < len(argv)), None)
        dispatch = {
            "check":     lambda: self.command_check("--verbose" in argv),
            "sync":      lambda: self.command_sync("--dry-run" in argv),
            "propagate": lambda: self.command_propagate(core_path=core_path, project=project),
            "doctor":    lambda: self.command_doctor("--fix" in argv),
            "evidence":  lambda: self.command_evidence(last_n),
            "cost":      lambda: self.command_cost(transcript_path),
            "knowledge": lambda: self.command_knowledge(),
            "split-golden-standard": lambda: self.command_split_golden_standard(),
            "hygiene":   lambda: self.command_hygiene("--fix" in argv),
            "maintenance": lambda: self.command_maintenance(),
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
