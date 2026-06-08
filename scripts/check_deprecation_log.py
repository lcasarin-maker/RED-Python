#!/usr/bin/env python3
"""check_deprecation_log.py — S24 Anti-Deprecación-Precipitada enforcement.

Verifica que todo archivo recientemente añadido a deprecated/ tenga entrada
en DEPRECATION_LOG.md. Usado como gate en pre-commit y en auditoría D1.

Exit 0: OK — todos los archivos deprecados están justificados.
Exit 1: BLOQUEADO — hay archivos en deprecated/ sin entrada en el log.
"""
import logging
import subprocess
import sys
from pathlib import Path

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(message)s")

ROOT = Path(__file__).resolve().parent.parent
DEPRECATION_LOG = ROOT / "DEPRECATION_LOG.md"
DEPRECATED_DIR = ROOT / "deprecated"


def _get_staged_deprecated_files() -> list[str]:
    """Devuelve archivos staged bajo deprecated/ (para uso en pre-commit)."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=A"],
            capture_output=True, text=True, cwd=ROOT, timeout=10,
        )
        return [f for f in result.stdout.splitlines() if f.startswith("deprecated/")]
    except Exception as exc:
        logger.error("[D5] git diff falló: %s", exc)
        return []


def _log_entries() -> set[str]:
    """Extrae nombres de archivo mencionados en DEPRECATION_LOG.md."""
    if not DEPRECATION_LOG.exists():
        return set()
    text = DEPRECATION_LOG.read_text(encoding="utf-8")
    entries = set()
    for line in text.splitlines():
        if line.startswith("### ["):
            # Formato: ### [YYYY-MM-DD] nombre.ext → deprecated/ruta/nombre.ext
            parts = line.split("→")
            if len(parts) >= 2:
                entries.add(parts[-1].strip())
            if len(parts) >= 1:
                # también el nombre original
                src = parts[0].split("]", 1)[-1].strip()
                entries.add(src)
    return entries


def validate_staged(strict: bool = True) -> int:
    """Valida archivos staged. Retorna 0=OK, 1=BLOQUEADO."""
    staged = _get_staged_deprecated_files()
    if not staged:
        logger.info("[S24] Sin archivos nuevos en deprecated/ — OK")
        return 0

    log_entries = _log_entries()
    violations = []
    for path in staged:
        filename = Path(path).name
        if not any(filename in entry or path in entry for entry in log_entries):
            violations.append(path)

    if violations:
        logger.error("[S24] BLOQUEADO — archivos en deprecated/ sin entrada en DEPRECATION_LOG.md:")
        for v in violations:
            logger.error("  - %s", v)
        logger.error("[ESTADO] Commit bloqueado hasta documentar la deprecación.")
        logger.error("[ACCIÓN] Actualizar DEPRECATION_LOG.md con entrada para cada archivo listado.")
        logger.error("[ACCIÓN] Formato: ### [YYYY-MM-DD] origen → %s", violations[0])
        return 1

    logger.info("[S24] Todos los archivos en deprecated/ están justificados en DEPRECATION_LOG.md — OK")
    return 0


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "staged"
    if mode in ("--help", "-h"):
        print("Uso: check_deprecation_log.py [staged]\nValida que archivos staged en deprecated/ tienen entrada en DEPRECATION_LOG.md.")
        sys.exit(0)
    if mode == "staged":
        sys.exit(validate_staged())
    else:
        logger.error("[ERROR] Modo desconocido: %s. Usar: staged", mode)
        sys.exit(1)
