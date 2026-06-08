#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera dimension_registry.json: ledger committeado de qué dimensión está
cableada a qué canal (gate/hook), con binario disponible y test real-repo.

Deriva la verdad del repo (no la fabrica): satélites por glob, binarios por
escaneo de fuente, wiring por grep del gate, dims del monolito por sus métodos
audit_dN. El test de frescura regenera en memoria y compara (snapshot)."""
import json
import logging
import re
import shutil
import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
from scripts.core_utils import setup_windows_utf8, write_json_atomic  # noqa: E402

setup_windows_utf8()
logger = logging.getLogger("generate_dimension_registry")

HOOK_DIMS = {"d13", "d14"}  # auditan al agente, no al repo (canal hook runtime)
KNOWN_BINARIES = ("bandit", "semgrep", "trivy", "vulture", "ruff", "pip-audit")
MONOLITH = _ROOT / "scripts" / "run_security_audit_12d.py"
GATE_FILES = (MONOLITH, _ROOT / "scripts" / "run_compliance_tests.py")
REGISTRY_PATH = _ROOT / "dimension_registry.json"


def _git_sha() -> str:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=_ROOT,
            capture_output=True,
            text=True,
            timeout=10,
        )
        return out.stdout.strip() or "unknown"
    except (OSError, subprocess.SubprocessError) as exc:
        logger.warning("_git_sha: no se pudo resolver HEAD: %s", exc)
        return "unknown"


def _binary_on_path(name: str) -> bool:
    """which() aumentado con rutas persistentes (pipx ~/.local/bin, winget)."""
    if shutil.which(name):
        return True
    extra = [
        Path.home() / ".local" / "bin",
        Path.home() / "AppData" / "Local" / "Microsoft" / "WinGet" / "Links",
    ]
    for base in extra:
        if any((base / cand).exists() for cand in (f"{name}.exe", name)):
            return True
    # WinGet instala el binario bajo Packages/<id>/ sin shim en Links (p.ej. trivy).
    pkgs = Path.home() / "AppData" / "Local" / "Microsoft" / "WinGet" / "Packages"
    if pkgs.exists() and next(pkgs.glob(f"*/**/{name}.exe"), None):
        return True
    return False


def _scan_binaries(src: str) -> list:
    found = {b for b in KNOWN_BINARIES if re.search(rf'["\']{re.escape(b)}["\']', src)}
    return sorted(found)


def _is_wired(dim_id: str) -> bool:
    """¿Algún archivo del gate importa/llama al satélite dN_*?"""
    pat = re.compile(rf"\b(import|from)\s+\S*{dim_id}_\w+|{dim_id}_\w+\.")
    for gf in GATE_FILES:
        if gf.exists() and pat.search(gf.read_text(encoding="utf-8", errors="replace")):
            return True
    return False


def _test_audits_real_repo(test_file: Path) -> bool:
    if not test_file.exists():
        return False
    src = test_file.read_text(encoding="utf-8", errors="replace")
    uses_fixture = "tmp_path" in src or "mock" in src.lower()
    hits_real = bool(
        re.search(r'check_path\s*=\s*["\']\.|Path\(__file__\)|_ROOT|PROJECT_ROOT', src)
    )
    return hits_real and not uses_fixture


def _satellite_impls() -> dict:
    """Una implementación 'enhanced' por dimensión (agrega micro-scripts dN_*)."""
    impls = {}
    for f in sorted((_ROOT / "scripts").glob("d*.py")):
        m = re.match(r"(d\d+)_", f.name)
        if not m:
            continue
        dim_id = m.group(1)
        src = f.read_text(encoding="utf-8", errors="replace")
        e = impls.setdefault(
            dim_id,
            {
                "source": [],
                "kind": "enhanced",
                "wired": _is_wired(dim_id),
                "requires_binaries": set(),
                "binary_available": None,
                "test_file": None,
                "test_audits_real_repo": False,
            },
        )
        e["source"].append(f"scripts/{f.name}")
        e["requires_binaries"].update(_scan_binaries(src))
        tf = _ROOT / "tests" / f"test_{f.stem}.py"
        if tf.exists():
            e["test_file"] = f"tests/{tf.name}"
            e["test_audits_real_repo"] = _test_audits_real_repo(tf)
    for e in impls.values():
        reqs = sorted(e.pop("requires_binaries"))
        e["requires_binaries"] = reqs
        e["binary_available"] = all(_binary_on_path(b) for b in reqs) if reqs else True
        e["source"] = ", ".join(e["source"])
    return impls


def _hook_caller_exists(module_stem: str) -> bool:
    """¿Algún script (p.ej. discourse_hook.py) importa el módulo de la dimensión?
    Para dims de canal hook, eso = tiene caller runtime => cableada de verdad."""
    pat = re.compile(rf"dimensions\.{re.escape(module_stem)}\b")
    for f in (_ROOT / "scripts").glob("*.py"):
        if pat.search(f.read_text(encoding="utf-8", errors="replace")):
            return True
    return False


def _package_impls() -> dict:
    """Dimensiones migradas al paquete dimensions/ (cableadas al gate vía REGISTRY,
    que run() recorre). Deriva de REGISTRY: imposible reportar una dim que el gate
    no corra, ni omitir una que sí."""
    try:
        from dimensions import REGISTRY
    except ImportError as exc:
        logger.warning("_package_impls: REGISTRY no importable: %s", exc)
        return {}
    impls = {}
    for dim in REGISTRY:
        module = type(dim).__module__  # "dimensions.d3_dead_code"
        rel = module.replace(".", "/") + ".py"
        src_path = _ROOT / rel
        src = (
            src_path.read_text(encoding="utf-8", errors="replace")
            if src_path.exists()
            else ""
        )
        tf = _ROOT / "tests" / f"test_{module.split('.')[-1]}.py"
        reqs = _scan_binaries(src)
        # gate: run() recorre REGISTRY => cableada. hook: cableada si un script-hook
        # importa el módulo (caller runtime real, p.ej. discourse_hook.py para d14).
        stem = module.split(".")[-1]
        wired = True if dim.channel == "gate" else _hook_caller_exists(stem)
        impls[dim.id] = {
            "source": rel,
            "kind": "package",
            "wired": wired,
            "requires_binaries": reqs,
            "binary_available": all(_binary_on_path(b) for b in reqs) if reqs else True,
            "test_file": f"tests/{tf.name}" if tf.exists() else None,
            "test_audits_real_repo": _test_audits_real_repo(tf),
        }
    return impls


def _gate_impls() -> dict:
    """Implementación inline del monolito (cableada al gate por construcción)."""
    src = MONOLITH.read_text(encoding="utf-8", errors="replace")
    ids = sorted(
        {m.group(1) for m in re.finditer(r"def audit_(d\d+)_", src)},
        key=lambda x: int(x[1:]),
    )
    return {
        d: {
            "source": "scripts/run_security_audit_12d.py",
            "kind": "inline",
            "wired": True,
            "requires_binaries": [],
            "binary_available": True,
            "test_file": None,
            "test_audits_real_repo": True,
        }
        for d in ids
    }


def build_registry() -> dict:
    gate, sat, pkg = _gate_impls(), _satellite_impls(), _package_impls()
    dims = {}
    for dim_id in sorted(set(gate) | set(sat) | set(pkg), key=lambda x: int(x[1:])):
        impls = [i for i in (gate.get(dim_id), sat.get(dim_id), pkg.get(dim_id)) if i]
        # fully_wired: el enforcement *previsto* está cableado. El módulo del paquete
        # (migración real) tiene prioridad; si no, enhanced; si no, inline legacy.
        intended = pkg.get(dim_id) or sat.get(dim_id) or gate.get(dim_id)
        dims[dim_id] = {
            "channel": "hook" if dim_id in HOOK_DIMS else "gate",
            "fully_wired": intended["wired"] and intended["binary_available"],
            "has_dual_impl": dim_id in gate and dim_id in sat,
            "implementations": impls,
        }
    return {
        "generated_from_git_sha": _git_sha(),
        "dimension_count": len(dims),
        "fully_wired_count": sum(1 for d in dims.values() if d["fully_wired"]),
        "dimensions": dims,
    }


def main() -> int:
    registry = build_registry()
    write_json_atomic(REGISTRY_PATH, registry)
    logger.info(
        "dimension_registry.json: %d dims, %d fully-wired",
        registry["dimension_count"],
        registry["fully_wired_count"],
    )
    print(json.dumps(registry, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
