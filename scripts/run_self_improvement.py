#!/usr/bin/env python3
"""
run_self_improvement.py v1.1 — CoderCerberus Gap Detector

Ejecuta run_security_audit_12d + verify_chaos_robustness + run_compliance_tests UNA VEZ y documenta gaps en HISTORIAL.md.
NO modifica codigo. NO es un loop infinito. Requiere aprobacion humana para actuar.

Usage:
  python scripts/run_self_improvement.py            # Run once, write to HISTORIAL.md
  python scripts/run_self_improvement.py --verbose  # Con detalles en stdout
  python scripts/run_self_improvement.py --dry-run  # Solo imprime, no escribe
"""

import logging
import subprocess
import sys
from pathlib import Path
from datetime import datetime

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from scripts.core_utils import setup_windows_utf8, get_historical_path
from scripts.manage_tokens import OutputCompressor

setup_windows_utf8()
logger = logging.getLogger("self_improvement_loop")
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


class SelfImprovementLoop:
    """Detector de gaps: ejecuta auditoria → documenta hallazgos → espera aprobacion humana."""

    def __init__(self, root: Path = None, dry_run: bool = False, verbose: bool = False):
        self.root = root or Path.cwd()
        self.dry_run = dry_run
        self.verbose = verbose

    def _run_script(self, script: str, extra_args: list = None) -> tuple:
        """Ejecuta un script y retorna (returncode, stdout, stderr)."""
        cmd = [sys.executable, f"scripts/{script}"] + (extra_args or [])
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True,
                encoding="utf-8", errors="ignore", cwd=str(self.root)
            )
            # TK-023/TK-024: el stdout capturado puede ser enorme. Se conserva completo
            # para la extracción de gaps, pero el log verbose usa la versión densa
            # (uso real de OutputCompressor — no un import-teatro para pasar TK-023).
            if self.verbose and OutputCompressor.should_compress(result.stdout):
                compact, used = OutputCompressor.process_output(result.stdout)
                logger.info("%s: salida %s (%d→%d tokens aprox)", script,
                            "comprimida" if used else "intacta",
                            OutputCompressor.estimate_tokens(result.stdout),
                            OutputCompressor.estimate_tokens(compact))
            return result.returncode, result.stdout, result.stderr
        except OSError as e:
            logger.error("No se pudo ejecutar %s: %s", script, e)
            return 1, "", str(e)

    def _extract_fail_lines(self, stdout: str) -> list:
        """Extrae líneas de error de la ÚLTIMA iteración de run_security_audit_12d (deduplicado)."""
        # run_security_audit_12d puede repetir hasta 5 iteraciones — tomar solo la última
        sections = stdout.split("=== ITERACIÓN")
        last_section = sections[-1] if sections else stdout
        lines = []
        seen = set()
        in_fail = False
        for line in last_section.splitlines():
            stripped = line.strip()
            if stripped.startswith("[FAIL]"):
                in_fail = True
                if stripped not in seen:
                    seen.add(stripped)
                    lines.append(stripped)
            elif stripped.startswith("[PASS]"):
                in_fail = False
            elif in_fail and stripped and stripped not in seen:
                seen.add(stripped)
                lines.append(f"    {stripped}")
        return lines

    def run_audit(self) -> tuple:
        """Auditoria 12D completa. Retorna (aprobado, gaps_list)."""
        code, stdout, _ = self._run_script("run_security_audit_12d.py")
        approved = code == 0
        gaps = self._extract_fail_lines(stdout) if not approved else []
        return approved, gaps

    def run_resilience(self) -> tuple:
        """Chaos Robustness Engine. Retorna (certificado, gaps_list)."""
        code, stdout, _ = self._run_script("verify_chaos_robustness.py")
        certified = code == 0
        gaps = [line.strip() for line in stdout.splitlines() if "[FAIL" in line]
        return certified, gaps

    def run_suite(self) -> tuple:
        """Suite run_compliance_tests. Retorna (todo_ok, gaps_list)."""
        code, stdout, _ = self._run_script("run_compliance_tests.py")
        all_ok = code == 0
        gaps = [line.strip() for line in stdout.splitlines()
                if "FAILED" in line or "ERROR" in line]
        return all_ok, gaps

    def _build_report(self, audit_ok, audit_gaps, chaos_ok, chaos_gaps,
                      suite_ok, suite_gaps) -> str:
        """Construye entrada de HISTORIAL.md con hallazgos del loop."""
        ts = datetime.now().isoformat(timespec="seconds")
        clean = audit_ok and chaos_ok and suite_ok
        status_label = "✅ LIMPIO" if clean else "⚠️  GAPS DETECTADOS"

        report = ["\n---", f"## LOOP [{ts}] {status_label}"]

        if audit_gaps:
            report.append("**Gaps run_security_audit_12d (12 dominios):**")
            report.extend(f"  {g}" for g in audit_gaps)
        if chaos_gaps:
            report.append("**Fallos verify_chaos_robustness:**")
            report.extend(f"  {g}" for g in chaos_gaps)
        if suite_gaps:
            report.append("**Fallos run_compliance_tests:**")
            report.extend(f"  {g}" for g in suite_gaps)

        if clean:
            report.append("**Resultado:** Sistema inexpugnable — cero gaps. No se requiere acción.")
        else:
            total = len(audit_gaps) + len(chaos_gaps) + len(suite_gaps)
            report.append(f"**Acción requerida ({total} gap(s)):** "
                          "Revisar gaps anteriores y aprobar correcciones.")

        return "\n".join(report)

    def run(self) -> int:
        """Orquesta el loop completo. Retorna 0 si limpio, 1 si hay gaps."""
        logger.info("🔄 Self-Improvement Loop iniciando...")

        audit_ok, audit_gaps = self.run_audit()
        chaos_ok, chaos_gaps = self.run_resilience()
        suite_ok, suite_gaps = self.run_suite()

        all_ok = audit_ok and chaos_ok and suite_ok
        all_gaps = audit_gaps + chaos_gaps + suite_gaps

        report = self._build_report(
            audit_ok, audit_gaps, chaos_ok, chaos_gaps, suite_ok, suite_gaps
        )

        if self.verbose or self.dry_run:
            print(report)

        if not self.dry_run:
            historial = get_historical_path(self.root)
            try:
                with open(historial, 'a', encoding='utf-8') as f:
                    f.write(report + "\n")
                logger.info("✅ Findings escritos en HISTORIAL.md")
            except OSError as e:
                logger.error("No se pudo escribir en HISTORIAL.md: %s", e)

        if all_ok:
            logger.info("✅ LOOP COMPLETO: Cerberus inexpugnable — 0 gaps detectados.")
        else:
            logger.warning("⚠️  LOOP COMPLETO: %d gap(s) detectado(s) — ver HISTORIAL.md",
                           len(all_gaps))

        return 0 if all_ok else 1


def main():
    dry_run = "--dry-run" in sys.argv
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    loop = SelfImprovementLoop(dry_run=dry_run, verbose=verbose)
    return loop.run()


if __name__ == "__main__":
    sys.exit(main())
