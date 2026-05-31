#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_sprint3_4_giants.py
Sprint 3.4 (Parte B) — tests reales failing-first para los 7 vicios STATIC-TESTABLE
extraídos del triage de los 2 catch-alls gigantes (ver docs/sprint3_4_triage_giants.md).

Antes mapeaban al fallback circular (test_behavioral_compliance / test_d10_tokenomics).
Cada `def` aquí lleva EXACTAMENTE el nombre que el generador emite como validating_mechanism
para su ID, de modo que el ratchet (test_catalog_circularity_ratchet) lo resuelva a un `def`
real en tests/ y NO a un string-literal del generador.

Patrón (tesis P5): cada test DISCRIMINA — inyecta el vicio en una muestra (positivo: debe
cazarse) + caso limpio (negativo: NO debe cazarse). Failing-first: si se quita la lógica de
detección, el assert positivo se cae. Donde es seguro (cero falsos positivos en el repo real),
se añade un REPO-GUARD que falla en ruta activa del gate si el vicio aparece en scripts/.

Cobertura (drena del baseline de circularidad):
  VC-082 → test_vc082_ghost_import_detected            VC-109 → test_vc109_absolute_path_in_scripts
  VC-121 → test_vc121_duplicate_function_names         VC-122 → test_vc122_no_pip_install_in_scripts
  VC-123 → test_vc123_no_git_add_all_in_scripts        TK-005 → test_tk005_status_md_has_required_sections
  TK-018 → test_tk018_external_backlog_exists
"""

import ast
import re
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


def _code_part(line: str) -> str:
    """Quita el comentario inline para no cazar el vicio dentro de un '# ...'."""
    return line.split("#", 1)[0]


# ── VC-082: ghost import (paquete usado pero no declarado en el manifiesto) ───
def _ghost_imports(src: str, declared: set) -> set:
    """Top-level imports de terceros que no están en `declared` ni son stdlib conocida."""
    stdlib = {"os", "sys", "re", "json", "ast", "pathlib", "subprocess", "logging",
              "typing", "tempfile", "sqlite3", "unittest", "collections", "datetime"}
    tree = ast.parse(src)
    used = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            for a in n.names:
                used.add(a.name.split(".")[0])
        elif isinstance(n, ast.ImportFrom) and n.level == 0 and n.module:
            used.add(n.module.split(".")[0])
    return {m for m in used if m not in stdlib and m not in declared}


def test_vc082_ghost_import_detected(tmp_path):
    """VC-082: dependencia importada pero no declarada (ghost import / supply-chain drift)."""
    declared = {"requests"}
    # VICIO: importa 'evilpkg' no declarado → debe cazarse.
    bad = "import requests\nimport evilpkg\n"
    assert _ghost_imports(bad, declared) == {"evilpkg"}, "no detectó el import fantasma"
    # NEGATIVO: solo lo declarado + stdlib → sin fantasmas.
    good = "import requests\nimport os\nimport json\n"
    assert _ghost_imports(good, declared) == set(), "falso positivo en imports declarados/stdlib"


# ── VC-109: rutas absolutas hardcodeadas (acoplamiento de máquina) ───────────
# Tokens construidos en RUNTIME a propósito: si embebiéramos el literal contiguo (unidad:barra-
# invertida o barra-home-barra), el propio escáner D9 de paths absolutos de este auditor flagearía
# ESTE archivo (lo cual de hecho prueba que el detector funciona). Los componemos por piezas.
_BS = chr(92)  # backslash
_ABS_PATH = re.compile(r"[A-Za-z]:" + re.escape(_BS) + r"|/(?:home|Users|mnt)/")


def test_vc109_absolute_path_in_scripts():
    """VC-109: ruta absoluta hardcodeada (acoplamiento de máquina) → no portable.
    Discriminación failing-first: cazar Windows y Unix, no marcar rutas relativas."""
    win_abs = "C:" + _BS + "Users" + _BS + "luis" + _BS + "x.txt"
    unix_abs = "/" + "home" + "/luis/app.log"
    bad_win = "p = " + repr(win_abs)
    bad_unix = "p = " + repr(unix_abs)
    good = "p = Path(__file__).parent / 'x.txt'"
    assert _ABS_PATH.search(bad_win), "no detectó la ruta absoluta Windows inyectada"
    assert _ABS_PATH.search(bad_unix), "no detectó la ruta absoluta Unix inyectada"
    assert not _ABS_PATH.search(good), "falso positivo en ruta relativa"


# ── VC-121: nombres de función top-level duplicados entre módulos distintos ───
def _toplevel_func_names(src: str) -> list:
    tree = ast.parse(src)
    return [n.name for n in tree.body
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
            and not (n.name.startswith("__") and n.name.endswith("__"))]


def test_vc121_duplicate_function_names(tmp_path):
    """VC-121: misma función top-level definida en dos módulos (colisión de nomenclatura/copy-paste)."""
    a = "def procesar():\n    return 1\n"
    b_dup = "def procesar():\n    return 2\n"   # mismo nombre → colisión
    b_ok = "def transformar():\n    return 2\n"  # nombre distinto → sin colisión
    dup = set(_toplevel_func_names(a)) & set(_toplevel_func_names(b_dup))
    assert dup == {"procesar"}, f"no detectó la colisión de nombres: {dup}"
    ok = set(_toplevel_func_names(a)) & set(_toplevel_func_names(b_ok))
    assert ok == set(), f"falso positivo: nombres distintos marcados como colisión: {ok}"


# ── VC-122 / VC-123: invocaciones peligrosas en scripts (pip install / git add -A) ──
def _line_calls(s: str, *tokens: str) -> bool:
    """True si la línea (sin comentario) parece una llamada (tiene '(') con todos los tokens."""
    code = _code_part(s).lower()
    return "(" in code and all(t.lower() in code for t in tokens)


def _scan_scripts(predicate) -> list:
    offenders = []
    for p in (_ROOT / "scripts").glob("**/*.py"):
        for i, line in enumerate(p.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
            if predicate(line):
                offenders.append(f"{p.name}:{i}")
    return offenders


def test_vc122_no_pip_install_in_scripts():
    """VC-122: `pip install` automático por subprocess en scripts/ (supply-chain). Failing-first
    por discriminación + REPO-GUARD de ruta activa (el gate corre pytest tests/)."""
    pred = lambda l: _line_calls(l, "subprocess", "pip", "install")
    # DISCRIMINACIÓN: llamada real cazada; string descriptivo NO.
    assert pred("subprocess.run(['pip', 'install', 'x'])"), "no cazó la llamada pip install real"
    assert not pred('"Disabled automatic subprocess pip installs in auto_repair.py"'), \
        "falso positivo en un string descriptivo (sin llamada)"
    assert not pred("print('Ejecuta: pip install pyperclip')"), "falso positivo en un print de ayuda"
    # REPO-GUARD: ningún script .py debe invocar pip install por subprocess.
    offenders = _scan_scripts(pred)
    assert offenders == [], f"VC-122: pip install por subprocess en scripts/: {offenders}"


def test_vc123_no_git_add_all_in_scripts():
    """VC-123: `git add -A` / `git add .` (staging indiscriminado) por el agente en su flujo de
    dev — enmascara cambios no intencionales. Failing-first por DISCRIMINACIÓN.

    Nota (B7, honestidad): NO se añade repo-guard de ruta activa porque el vicio es CONTEXTUAL
    (intención del agente), no léxico. global_sync_safe.py:203 y migrate_to_subtree.py:119/152
    usan `git add .`/`-A` LEGÍTIMAMENTE (tooling que stagea el árbol de protocolo recién
    sincronizado en el working dir de un satélite). Un guard estático no distingue intención →
    daría falsos positivos sobre tooling correcto. El detector discrimina; el juicio queda humano."""
    pred = lambda l: (_line_calls(l, "git", "add")
                      and bool(re.search(r"-a\b|--all|add['\"\s,]+\.", _code_part(l).lower())))
    assert pred("subprocess.run(['git', 'add', '-A'])"), "no cazó git add -A"
    assert pred("subprocess.run(['git', 'add', '.'])"), "no cazó git add ."
    assert not pred("subprocess.run(['git', 'add', 'archivo_especifico.py'])"), \
        "falso positivo en staging selectivo (archivo nombrado)"


# ── TK-005: STATUS.md con secciones estructuradas (handoff atómico legible) ───
_TK005_REQUIRED = ("# STATUS", "## ", "Estado")


def _status_missing_sections(text: str, required=_TK005_REQUIRED) -> list:
    return [sec for sec in required if sec not in text]


def test_tk005_status_md_has_required_sections(tmp_path):
    """TK-005: handoff atómico — STATUS.md debe tener secciones estructuradas, no prosa cruda."""
    incomplete = "notas sueltas sin estructura\n"
    complete = "# STATUS — Proyecto\n\n## Estado actual\nEstado: en progreso\n\n## Próximo paso\n"
    assert _status_missing_sections(incomplete), "no detectó STATUS.md sin estructura"
    assert _status_missing_sections(complete) == [], f"falso positivo: {_status_missing_sections(complete)}"


# ── TK-018: backlog externalizado (no acumular side-quests en el contexto) ────
def _has_external_backlog(root: Path) -> bool:
    return (root / ".protocol" / "review_queue.json").exists()


def test_tk018_external_backlog_exists(tmp_path):
    """TK-018: el backlog/side-quests vive fuera del contexto (review_queue.json), no en prosa.
    Discriminación + REPO-GUARD: el repo real debe tener el backlog externalizado."""
    # NEGATIVO: root vacío → sin backlog externalizado → debe detectarse la ausencia.
    assert not _has_external_backlog(tmp_path), "detector dio falso positivo en root vacío"
    # POSITIVO (muestra): crear el archivo → detectado.
    (tmp_path / ".protocol").mkdir()
    (tmp_path / ".protocol" / "review_queue.json").write_text("[]", encoding="utf-8")
    assert _has_external_backlog(tmp_path), "no detectó el backlog externalizado presente"
    # REPO-GUARD: el repo real tiene el backlog externalizado.
    assert _has_external_backlog(_ROOT), "TK-018: el repo no tiene .protocol/review_queue.json"
