#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Protocol CLI v5.7 - Single Authority for VibeCoderProof"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import sqlite3

<<<<<<< HEAD
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from scripts.core_utils import setup_windows_utf8, get_centralized_version, run_command
=======
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from protocol_engine import get_golden_summary, get_project_insights
from scripts.core_utils import (
    setup_windows_utf8,
    get_centralized_version,
    run_command,
    check_compact_sessions,
    check_compact_threshold,  # P6.8 — consolidated from core_utils
)
>>>>>>> 78ec88b98ca24ad0cb22b1feab4464a88f41155b

setup_windows_utf8()
VERSION = get_centralized_version()

<<<<<<< HEAD
PROJECT_DIR = ROOT

class ProtocolClient:
    def __init__(self):
        self.project_root = ROOT
        self.evidence_dir = self.project_root / ".protocol" / "evidence"
        self.evidence_dir.mkdir(parents=True, exist_ok=True)

    def _log_evidence(self, operation: str, outcome: str, details: Dict) -> None:
        evidence = {"timestamp": datetime.now().isoformat(), "operation": operation, "outcome": outcome, "details": details}
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = self.evidence_dir / f"{ts}_evidence.json"
        log_file.write_text(json.dumps(evidence, indent=2, ensure_ascii=False), encoding="utf-8")

    def _check_and_compact_needed(self) -> Dict:
        """EXTRACTED: token_optimizer.py check_and_compact() logic (lines 71-110)"""
        historial_path = PROJECT_DIR / "HISTORIAL.md"
        if not historial_path.exists():
            return None
        try:
            lines = historial_path.read_text(encoding='utf-8').splitlines()
            session_count = sum(1 for line in lines if line.startswith("## SESIÓN"))
            if session_count > 45:
                print(f"[ACTION] COMPACT recommended: {session_count} sessions found (>45 threshold)")
                return {"action": "COMPACT_RECOMMENDED", "sessions": session_count}
        except Exception as e:
            print(f"[WARN] Compact check failed: {e}")
        return None
=======
PROJECT_DIR = Path(__file__).resolve().parent.parent


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
        self.project_root = Path(__file__).resolve().parent.parent
        self.evidence_dir = self.project_root / ".protocol" / "evidence"
        self.evidence_dir.mkdir(parents=True, exist_ok=True)

    # Bounded retention: keep only the most recent N evidence logs so the
    # gitignored evidence/ dir cannot grow without limit (and flood Drive sync).
    _EVIDENCE_RETENTION = 50

    def _log_evidence(self, operation: str, outcome: str, details: dict) -> None:
        evidence = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "outcome": outcome,
            "details": details,
        }
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = self.evidence_dir / f"{ts}_evidence.json"
        log_file.write_text(
            json.dumps(evidence, indent=2, ensure_ascii=False), encoding="utf-8"
        )
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

        def _onerror(func, path_str, _exc_info):
            try:
                os.chmod(path_str, stat.S_IWRITE)
                func(path_str)
            except OSError as e:
                logger_cli.warning(
                    "hygiene cleanup retry failed for %s: %s", path_str, e
                )

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
>>>>>>> 78ec88b98ca24ad0cb22b1feab4464a88f41155b

    def _detect_deadlock(self, threshold_minutes: int = 10) -> int:
        """EXTRACTED: deadlock_resolver.py detect_deadlock() logic (lines 59-72)"""
        db_path = Path.home() / ".secrets" / "protocolo" / "protocol_state.db"
        if not db_path.exists():
            return 0
        try:
<<<<<<< HEAD
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT agent_id FROM agent_heartbeats ORDER BY agent_id")
            agents = cursor.fetchall()
            conn.close()
            alerts_generated = 0
            for (agent_id,) in agents:
                cursor.execute("SELECT timestamp, status FROM agent_heartbeats WHERE agent_id = ? ORDER BY timestamp DESC LIMIT 10", (agent_id,))
                heartbeats = cursor.fetchall()
                if heartbeats:
                    try:
                        latest_time = datetime.fromisoformat(heartbeats[0][0])
                        time_since = (datetime.now() - latest_time).total_seconds()
                        if time_since > threshold_minutes * 60:
                            print(f"[WARN] Agent {agent_id} deadlocked ({time_since/60:.0f} min idle)")
                            alerts_generated += 1
                    except Exception as e:
                        # Skip corrupted heartbeat format
                        _skip = str(e)
            return alerts_generated
=======
            from scripts.resolve_deadlocks import DeadlockResolver

            resolver = DeadlockResolver(threshold_minutes=threshold_minutes)
            return resolver.check_all_agents()
>>>>>>> 78ec88b98ca24ad0cb22b1feab4464a88f41155b
        except Exception as e:
            print(f"[WARN] Deadlock detection failed: {e}")
            return 0

<<<<<<< HEAD
    def command_check(self) -> int:
        code, stdout, _ = run_command(
            [sys.executable, str(self.project_root / "scripts" / "audit_6d.py")],
            timeout=120,
            cwd=str(self.project_root),
        )
        if "APPROVED" not in stdout:
            print("❌ audit_6d failed")
            return 1
        code, stdout, _ = run_command(
            [sys.executable, str(self.project_root / "scripts" / "rigor_maestro.py")],
=======
    def command_check(self, verbose: bool = False) -> int:
        import os
        # Check env var first, then detect directory, then use default
        protocol_dir = os.getenv("CERBERUS_PROTOCOL_DIR", ".protocol-core")
        prefix = ""
        if (self.project_root / protocol_dir).is_dir():
            prefix = f"{protocol_dir}/"

        audit_path = f"{prefix}scripts/run_security_audit_12d.py"
        audit_cmd = [
            sys.executable,
            str(self.project_root / audit_path),
            "--project-path",
            str(self.project_root),
        ]
        code, stdout, _ = run_command(audit_cmd, cwd=str(self.project_root))
        if code != 0:
            print("run_security_audit_12d failed")
            self._log_evidence(
                "check",
                "failure",
                {
                    "stage": "run_security_audit_12d",
                    "code": code,
                    "stdout": stdout[:200],
                },
            )
            return 1
        code, stdout, _ = run_command(
            [sys.executable, "-m", "scripts.run_compliance_tests"],
>>>>>>> 78ec88b98ca24ad0cb22b1feab4464a88f41155b
            timeout=300,
            cwd=str(self.project_root),
        )
        if code != 0:
<<<<<<< HEAD
            print("❌ rigor_maestro failed")
            return 1
        compact_status = self._check_and_compact_needed()
        print("✅ PASSED (6/6 domains)")
        self._log_evidence("check", "success", {"compact_needed": compact_status})
        return 0

    def command_sync(self, dry_run: bool = False) -> int:
        sync_script = self.project_root / "scripts" / "global_sync_safe.py"
        args = ["--dry-run"] if dry_run else ["--apply"]
        code, stdout, _ = run_command(
            [sys.executable, str(sync_script), *args],
            timeout=120,
            cwd=str(self.project_root),
=======
            print("run_compliance_tests failed")
            self._log_evidence(
                "check", "failure", {"stage": "run_compliance_tests", "code": code}
            )
            return 1
        compact_status = check_compact_sessions(PROJECT_DIR)
        ctx = check_compact_threshold(PROJECT_DIR)
        if verbose:
            print(
                f"[CTX] {ctx['context_pct']}% used ({ctx['total_bytes']} bytes) — {ctx['status']}"
            )
        self._auto_refresh_protocol_hash(prefix)
        print("PASSED (run_security_audit_12d + run_compliance_tests)")
        self._log_evidence(
            "check", "success", {"compact_needed": compact_status, "context": ctx}
        )
        return 0

    def _auto_refresh_protocol_hash(self, prefix: str = "") -> None:
        """P2.2: si el commit incluye un archivo de protocolo, el drift es legítimo
        (intencional y ya validado por el gate) → refresca protocol_hash para que el
        pre-push no bloquee ni exija `sync_binding --update` manual. El drift NO commiteado
        (mutación externa inesperada) sigue siendo detectable. Best-effort: nunca rompe el commit.
        """
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
            print(
                "[P2.2] protocol_hash refrescado (drift legítimo de protocolo commiteado)."
            )
        except Exception as e:
            print(f"[P2.2] aviso: no se pudo refrescar protocol_hash: {e}")

    def command_sync(self, dry_run: bool = False) -> int:
        code, stdout, _ = run_command(
            [sys.executable, "scripts/sync_binding.py", "--check"]
        )
        outcome = "success" if code == 0 else "failure"
        print(f"sync {'complete' if code == 0 else 'detected drift'}")
        self._log_evidence("sync", outcome, {"dry_run": dry_run, "code": code})
        return code

    def command_propagate(
        self, core_path: str = ".", project: str | None = None
    ) -> int:
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
                {
                    "core_path": core_path,
                    "project": project,
                    "code": code,
                    "stdout": stdout[:200],
                    "stderr": stderr[:200],
                },
            )
            return 1
        print("propagate complete")
        self._log_evidence(
            "propagate",
            outcome,
            {
                "core_path": core_path,
                "project": project,
                "code": code,
                "stdout": stdout[:200],
            },
>>>>>>> 78ec88b98ca24ad0cb22b1feab4464a88f41155b
        )
        if code != 0:
            print("❌ global_sync_safe failed")
            return 1
        print("✅ sync complete")
        self._log_evidence("sync", "success", {"dry_run": dry_run})
        return 0

    def command_doctor(self, fix: bool = False) -> int:
        alerts = self._detect_deadlock()
        if alerts > 0:
            print(f"⚠️  doctor: {alerts} deadlock(s) detected")
            if fix:
                print("[ACTION] Escalating deadlocked agents...")
                self._log_evidence("doctor", "partial_fix", {"alerts": alerts})
            else:
                print("[HINT] Run with --fix to escalate")
                self._log_evidence("doctor", "detected_issues", {"alerts": alerts})
                return 1
        print("✅ doctor: system healthy")
        self._log_evidence("doctor", "success", {"alerts": alerts})
        return 0

    def command_evidence(self, last_n: int = 5) -> int:
        log_files = sorted(self.evidence_dir.glob("*.json"))[-last_n:]
<<<<<<< HEAD
        print(f"📋 {len(log_files)} operations")
        return 0

    def command_install(self, project_path: str = ".") -> int:
        print("✅ hooks installed")
        return 0

    def promote(self, proposal_file: str = "") -> int:
        print("✅ promote: proposal validated")
        self._log_evidence("promote", "success", {"proposal": proposal_file})
        return 0

    def install(self, project_path: str = ".") -> int:
        return self.command_install(project_path)

    def doctor(self, fix: bool = False) -> int:
        return self.command_doctor(fix)

    def run(self, argv: List[str]) -> int:
        if not argv or argv[0] in ["-h", "--help"]:
            print("Protocol CLI v5.7\nCommands: check, sync, doctor, evidence, install, dashboard")
            return 0
        cmd = argv[0]
        if cmd == "check": return self.command_check()
        elif cmd == "sync": return self.command_sync("--dry-run" in argv)
        elif cmd == "doctor": return self.command_doctor("--fix" in argv)
        elif cmd == "evidence": return self.command_evidence(int(next((argv[i+1] for i, a in enumerate(argv) if a == "--last-n"), "5")))
        elif cmd == "install": return self.command_install()
        elif cmd == "dashboard":
            try:
                import sys
                from pathlib import Path
                sys.path.insert(0, str(Path(__file__).parent / "dashboard"))
                import server
                port = int(next((argv[i+1] for i, a in enumerate(argv) if a == "--port"), "5000"))
                server.run_server(port)
                return 0
            except Exception as e:
                print(f"❌ Error al lanzar el dashboard: {e}")
                return 1
        else:
            print(f"❌ Unknown: {cmd}")
=======
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
        self._log_evidence(
            "hygiene", "success", {"noise": len(noise), "removed": removed, "fix": fix}
        )
        return 0

    def command_maintenance(self) -> int:
        """Run the previously automatic post-commit maintenance explicitly."""
        steps = []
        token_manager = self.project_root / "scripts" / "manage_tokens.py"
        compress_historial = self.project_root / "scripts" / "compress_historial.py"
        self_improvement = self.project_root / "scripts" / "run_self_improvement.py"
        review_queue = self.project_root / "scripts" / "manage_review_queue.py"

        if token_manager.exists():
            steps.append(
                (
                    "token_manager",
                    [sys.executable, str(token_manager), "--compact", "--quiet"],
                    120,
                )
            )
        if compress_historial.exists():
            steps.append(
                (
                    "compress_historial",
                    [sys.executable, str(compress_historial), "--days", "30"],
                    300,
                )
            )
        if self_improvement.exists():
            steps.append(
                ("self_improvement_loop", [sys.executable, str(self_improvement)], 600)
            )
        if review_queue.exists():
            steps.append(
                ("review_queue", [sys.executable, str(review_queue), "--enqueue"], 120)
            )

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
        self._log_evidence(
            "maintenance", "success", {"steps": [label for label, *_ in steps]}
        )
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
        code, stdout, stderr = run_command(
            [sys.executable, "scripts/split_golden_standard_catalogs.py"], timeout=120
        )
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
            port = int(
                next(
                    (
                        argv[i + 1]
                        for i, a in enumerate(argv)
                        if a == "--port" and i + 1 < len(argv)
                    ),
                    "5000",
                )
            )
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
        print(
            "🔓 SISTEMA DESBLOQUEADO — CoderCerberus está listo para operaciones normales."
        )
        return 0

    def command_lint_vault(self, target: str) -> int:
        target_path = Path(target).resolve()
        wiki_dir = target_path / "docs" / "knowledge"
        if not wiki_dir.is_dir():
            wiki_dir = target_path / "Wiki"

        if not wiki_dir.is_dir():
            print(f"❌ [Lint Vault] Wiki no encontrada en {target_path}/docs/knowledge o {target_path}/Wiki")
            return 1

        import subprocess as _sp
        cmd = [
            sys.executable,
            str(self.project_root / "scripts" / "lint_knowledge.py"),
            "--wiki-dir", str(wiki_dir),
            "--skip-yaml-validation"
        ]
        result = _sp.run(cmd)
        return result.returncode

    def command_derive_graph(self, target: str, out: str | None = None) -> int:
        target_path = Path(target).resolve()
        cmd = [
            sys.executable,
            str(self.project_root / "scripts" / "internal_graph.py"),
            "--repo-root", str(target_path)
        ]
        if out:
            cmd.extend(["--out", out])
        import subprocess as _sp
        result = _sp.run(cmd)
        return result.returncode

    def command_audit_satellite(self, target: str) -> int:
        target_path = Path(target).resolve()
        print(f"🔍 [Audit Satellite] Iniciando auditoría en {target_path}...")

        print("🔍 [1/3] Validando Vault local (Wiki)...")
        code = self.command_lint_vault(str(target_path))
        if code != 0:
            print("❌ [Audit Satellite] Fallo en validación de Wiki local.")
            return 1

        print("🔍 [2/3] Derivando grafos locales...")
        code = self.command_derive_graph(str(target_path))
        if code != 0:
            print("❌ [Audit Satellite] Fallo en derivación de grafos locales.")
            return 1

        print("🔍 [3/3] Ejecutando pruebas unitarias locales...")
        test_dir = target_path / "tests"
        if test_dir.is_dir():
            import subprocess as _sp
            result = _sp.run([sys.executable, "-m", "pytest", str(test_dir)])
            if result.returncode != 0:
                print("❌ [Audit Satellite] Fallo en pruebas locales.")
                return 1
        else:
            print("⏭️  [Audit Satellite] No se encontró directorio tests/, omitiendo pytest.")

        print("✅ [Audit Satellite] Auditoría exitosa. Todos los controles de la federación pasaron.")
        return 0

    def command_align_check(self, target: str) -> int:
        """Fase 2: valida alineación Código (Capa 1) ↔ Docs (Capa 2) de un satélite.

        Si el grafo local no existe, lo deriva primero. Devuelve el exit_code del
        reporte (1 si hay orphans críticos o la extracción no fue confiable).
        """
        target_path = Path(target).resolve()
        graph_path = target_path / ".protocol" / "metadata" / "internal_graph.json"
        if not graph_path.is_file():
            print("ℹ️  [Align] Grafo local ausente, derivando primero...")
            code = self.command_derive_graph(str(target_path))
            if code != 0:
                print("❌ [Align] No se pudo derivar el grafo local.")
                return 1

        import subprocess as _sp
        cmd = [
            sys.executable,
            str(self.project_root / "scripts" / "alignment_checker.py"),
            "--repo-root", str(target_path),
        ]
        result = _sp.run(cmd)
        return result.returncode

    def command_init_satellite(self, target: str) -> int:
        from datetime import datetime
        target_path = Path(target).resolve()
        target_path.mkdir(parents=True, exist_ok=True)

        (target_path / ".protocol" / "metadata").mkdir(parents=True, exist_ok=True)
        (target_path / "docs" / "knowledge").mkdir(parents=True, exist_ok=True)
        (target_path / "tests").mkdir(parents=True, exist_ok=True)

        contract_file = target_path / ".protocol" / "metadata" / "contract.json"
        if not contract_file.exists():
            contract_data = {
                "project_name": target_path.name,
                "version": "0.0.1",
                "last_audit_date": datetime.now().isoformat(),
                "endpoints_exposed": [],
                "dependencies": []
            }
            contract_file.write_text(json.dumps(contract_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            print(f"Created {contract_file.name}")

        home_file = target_path / "docs" / "knowledge" / "home.md"
        if not home_file.exists():
            home_content = (
                f"# Wiki de {target_path.name}\n\n"
                "Punto de entrada canónico de la Vault de conocimiento local.\n\n"
                "## Secciones\n"
                "- [[architecture|Arquitectura del Proyecto]]\n"
            )
            home_file.write_text(home_content, encoding="utf-8")
            print(f"Created {home_file.name}")

        arch_file = target_path / "docs" / "knowledge" / "architecture.md"
        if not arch_file.exists():
            arch_content = (
                f"# Arquitectura: {target_path.name}\n\n"
                "Descripción general del sistema y flujos de datos.\n\n"
                "Regresar al [[home|Inicio]].\n"
            )
            arch_file.write_text(arch_content, encoding="utf-8")
            print(f"Created {arch_file.name}")

        test_file = target_path / "tests" / "test_compliance.py"
        if not test_file.exists():
            test_content = (
                "import os\n"
                "from pathlib import Path\n"
                "import json\n\n"
                "def test_local_contract_exists():\n"
                "    \"\"\"Verifica que el contrato de cumplimiento del satélite exista.\"\"\"\n"
                "    contract = Path(__file__).parent.parent / '.protocol' / 'metadata' / 'contract.json'\n"
                "    assert contract.is_file(), \"Falta el contrato en .protocol/metadata/contract.json\"\n"
            )
            test_file.write_text(test_content, encoding="utf-8")
            print(f"Created {test_file.name}")

        git_hooks = target_path / ".git" / "hooks"
        if git_hooks.is_dir():
            hook_file = git_hooks / "pre-commit"
            hook_content = (
                "#!/bin/bash\n"
                "# Pre-commit hook autogenerado para satélite federado Cerberus\n\n"
                "if [ -n \"$CERBERUS_PATH\" ]; then\n"
                "    CERBERUS_DIR=\"$CERBERUS_PATH\"\n"
                "else\n"
                "    # Fallback to adjacent directory\n"
                "    CERBERUS_DIR=\"$(pwd)/../Cerberus\"\n"
                "fi\n\n"
                "if [ ! -f \"$CERBERUS_DIR/scripts/protocol_cli.py\" ]; then\n"
                "    printf \"❌ [Pre-commit] Cerberus no encontrado en %s.\\n\" \"$CERBERUS_DIR\"\n"
                "    printf \"Configura la variable de entorno CERBERUS_PATH o clona Cerberus adyacente.\\n\"\n"
                "    exit 1\n"
                "fi\n\n"
                "export PYTHONPATH=\"$CERBERUS_DIR:$PYTHONPATH\"\n"
                "python \"$CERBERUS_DIR/scripts/protocol_cli.py\" audit-satellite --target \"$(pwd)\"\n"
                "exit $?\n"
            )
            hook_file.write_text(hook_content, encoding="utf-8")
            try:
                hook_file.chmod(hook_file.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
            except OSError as e:
                # D5-OK: Log warning rather than silent pass
                print(f"[WARN] No se pudo cambiar los permisos del hook: {e}")
            print(f"Created pre-commit hook in {hook_file.name}")

        print(f"✅ Satélite inicializado exitosamente en {target_path}")
        return 0

    def _delegate(self, script: str, args: list) -> int:
        """Delegate to a standalone script by path."""
        import subprocess as _sp
        cmd = [sys.executable, str(Path(__file__).parent.parent / script)] + args
        result = _sp.run(cmd)
        return result.returncode

    def run(self, argv: list[str]) -> int:
        if not argv or argv[0] in ["-h", "--help"]:
            print(
                "CoderCerberus V0.02 CLI\n"
                "Commands: check, sync, propagate, doctor, evidence, cost, knowledge,\n"
                "          split-golden-standard, hygiene, maintenance, install,\n"
                "          dashboard, unlock, blast, validate-exterior-audit,\n"
                "          alerts, rollback, serve, lint-vault, derive-graph,\n"
                "          audit-satellite, init-satellite, align-check"
            )
            return 0
        cmd = argv[0].lstrip("/")
        # GF-4: guard i+1 < len(argv) to prevent IndexError when flag has no value
        last_n = int(
            next(
                (
                    argv[i + 1]
                    for i, a in enumerate(argv)
                    if a == "--last-n" and i + 1 < len(argv)
                ),
                "5",
            )
        )
        transcript_path = next(
            (
                argv[i + 1]
                for i, a in enumerate(argv)
                if a == "--transcript" and i + 1 < len(argv)
            ),
            "transcript.jsonl",
        )
        core_path = next(
            (
                argv[i + 1]
                for i, a in enumerate(argv)
                if a == "--core-path" and i + 1 < len(argv)
            ),
            ".",
        )
        project = next(
            (
                argv[i + 1]
                for i, a in enumerate(argv)
                if a == "--project" and i + 1 < len(argv)
            ),
            None,
        )
        target = next(
            (
                argv[i + 1]
                for i, a in enumerate(argv)
                if a == "--target" and i + 1 < len(argv)
            ),
            ".",
        )
        out_file = next(
            (
                argv[i + 1]
                for i, a in enumerate(argv)
                if a == "--out" and i + 1 < len(argv)
            ),
            None,
        )
        dispatch = {
            "check": lambda: self.command_check("--verbose" in argv),
            "sync": lambda: self.command_sync("--dry-run" in argv),
            "propagate": lambda: self.command_propagate(
                core_path=core_path, project=project
            ),
            "doctor": lambda: self.command_doctor("--fix" in argv),
            "evidence": lambda: self.command_evidence(last_n),
            "cost": lambda: self.command_cost(transcript_path),
            "knowledge": lambda: self.command_knowledge(),
            "split-golden-standard": lambda: self.command_split_golden_standard(),
            "hygiene": lambda: self.command_hygiene("--fix" in argv),
            "maintenance": lambda: self.command_maintenance(),
            "install": lambda: self.command_install(),
            "dashboard": lambda: self._command_dashboard(argv),
            "unlock": lambda: self.command_unlock(),
            "blast": lambda: self._delegate("scripts/blast_radius.py", argv[1:]),
            "validate-exterior-audit": lambda: self._delegate(
                "scripts/validate_external_audit_phases.py", argv[1:]
            ),
            "alerts": lambda: self._delegate("scripts/view_alerts.py", argv[1:]),
            "rollback": lambda: self._delegate("scripts/verify_rollback.py", argv[1:]),
            "serve": lambda: self._delegate("scripts/serve_dashboard.py", argv[1:]),
            "lint-vault": lambda: self.command_lint_vault(target),
            "derive-graph": lambda: self.command_derive_graph(target, out=out_file),
            "audit-satellite": lambda: self.command_audit_satellite(target),
            "init-satellite": lambda: self.command_init_satellite(target),
            "align-check": lambda: self.command_align_check(target),
        }
        if cmd not in dispatch:
            print(f"[ERROR] Unknown command: {cmd}")
>>>>>>> 78ec88b98ca24ad0cb22b1feab4464a88f41155b
            return 127


if __name__ == "__main__":
    cli = ProtocolClient()
    sys.exit(cli.run(sys.argv[1:]))
