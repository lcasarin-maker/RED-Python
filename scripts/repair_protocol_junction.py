#!/usr/bin/env python3
"""repair_protocol_junction.py v1.0 — Sprint 3.9 (PASO 3).

Auto-repara el binding `.protocol-core` de los satélites. El modelo es **junction**
(directory junction → raíz viva de Cerberus, derivada de `__file__`). Reemplaza el
modelo subtree-pull (S19: sin puentes). Idempotente y seguro: NUNCA borra un
directorio real con contenido del usuario; solo actúa sobre junctions colgantes,
con target equivocado o ausentes.

Causa raíz reparada: los junctions apuntaban a `D:\\AI\\Cerberus\\rules` (inexistente)
tras reorganizar Cerberus → enforcement muerto en los 17 satélites.
"""

import argparse
import json
import logging
import os
import stat
import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

logger = logging.getLogger("repair_protocol_junction")
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

_LINK_NAME = ".protocol-core"
_REGISTRY = _ROOT / ".protocol" / "metadata" / "REGISTRY.json"


def canonical_core_root() -> Path:
    """Raíz viva de Cerberus, derivada de la ubicación de este script (auto-heal)."""
    return _ROOT


def classify(
    listed: bool,
    is_junction: bool,
    target: str | None,
    core: Path,
    has_scripts: bool,
) -> str:
    """Clasificación PURA del estado de `.protocol-core` (testeable sin junctions reales)."""
    if not listed:
        return "missing"
    if not is_junction:
        return "not_junction"
    if target is None:
        return "broken"
    if Path(target).resolve() != Path(core).resolve():
        return "wrong_target"
    return "ok" if has_scripts else "broken"


def repair_action(status: str) -> str:
    """Decisión PURA. `not_junction` (dir real) → jamás tocar (Angry Path B3)."""
    if status == "ok":
        return "noop"
    if status == "not_junction":
        return "skip_unsafe"
    return "repair"  # missing | broken | wrong_target


def _is_junction(p: Path) -> bool:
    try:
        st = os.lstat(p)
    except OSError:
        return False
    tag = getattr(st, "st_reparse_tag", 0)
    return bool(tag == getattr(stat, "IO_REPARSE_TAG_MOUNT_POINT", -1))


def _readlink_safe(p: Path) -> str | None:
    try:
        return os.readlink(p)
    except OSError:
        return None


def junction_status(satellite: Path, core: Path) -> str:
    """Reúne los probes reales del FS y delega en `classify`."""
    jp = Path(satellite) / _LINK_NAME
    parent = jp.parent
    listed = parent.is_dir() and jp.name in os.listdir(parent)
    if not listed:
        return classify(False, False, None, core, False)
    is_j = _is_junction(jp)
    target = _readlink_safe(jp) if is_j else None
    if target is not None:
        target = target.replace("\\\\?\\", "")
    has_scripts = (jp / "scripts" / "protocol_cli.py").exists()
    return classify(True, is_j, target, core, has_scripts)


def _remove_junction(jp: Path) -> None:
    """Borra SOLO el link (rmdir no sigue el reparse). Nunca borra el target."""
    try:
        os.rmdir(jp)
    except OSError:
        subprocess.run(["cmd", "/c", "rmdir", str(jp)], capture_output=True)


def repair_junction(satellite: Path, core: Path, dry_run: bool = False) -> dict:
    """Repara idempotentemente el junction de un satélite. Devuelve dict de estado."""
    satellite = Path(satellite)
    status = junction_status(satellite, core)
    action = repair_action(status)
    result = {"satellite": str(satellite), "status": status, "action": action}
    logger.info("%s → status=%s action=%s", satellite.name, status, action)
    if action != "repair" or dry_run:
        return result
    jp = satellite / _LINK_NAME
    if jp.name in os.listdir(jp.parent):
        _remove_junction(jp)
    cp = subprocess.run(
        ["cmd", "/c", "mklink", "/J", str(jp), str(core)],
        capture_output=True,
        text=True,
    )
    result["mklink_rc"] = cp.returncode
    result["verified_ok"] = junction_status(satellite, core) == "ok"
    logger.info("   mklink rc=%s verified_ok=%s", cp.returncode, result["verified_ok"])
    return result


def _registry_satellites() -> list[dict]:
    data = json.loads(_REGISTRY.read_text(encoding="utf-8"))
    return data.get("projects", [])


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Repara junction .protocol-core (Sprint 3.9)")
    ap.add_argument("--repo-root", help="Reparar un solo satélite (ruta)")
    ap.add_argument("--all", action="store_true", help="Reparar todos los del REGISTRY con .git")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)
    core = canonical_core_root()

    targets: list[Path] = []
    if args.repo_root:
        targets = [Path(args.repo_root)]
    elif args.all:
        for proj in _registry_satellites():
            p = Path(proj["path"])
            if p.resolve() == core.resolve():
                continue
            if not (p / ".git").exists():
                logger.warning("%s → SIN .git, se omite", proj.get("name", p.name))
                continue
            targets.append(p)
    else:
        ap.error("usa --repo-root <ruta> o --all")

    results = [repair_junction(t, core, dry_run=args.dry_run) for t in targets]
    bad = [r for r in results if r["action"] == "repair" and not r.get("verified_ok", True)]
    unsafe = [r for r in results if r["action"] == "skip_unsafe"]
    logger.info(
        "RESUMEN: %d objetivos | %d reparados-ok | %d skip_unsafe | %d fallidos",
        len(results),
        sum(1 for r in results if r.get("verified_ok")),
        len(unsafe),
        len(bad),
    )
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
