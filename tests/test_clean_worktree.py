"""Tests del sprint VC-141: idempotencia de hooks + detector de working tree limpio."""
import json

import scripts.verify_protocol_adoption as vpa
import scripts.check_clean_worktree as ccw
from scripts.check_clean_worktree import worktree_is_clean


def test_escape_env_allows(monkeypatch):
    """El escape consciente CERBERUS_ALLOW_PARTIAL=1 omite la verificación (exit 0)."""
    monkeypatch.setenv("CERBERUS_ALLOW_PARTIAL", "1")
    assert ccw.main([]) == 0  # argv explícito: aísla de los flags de pytest


def test_clean_passes():
    """Porcelain vacío → working tree limpio."""
    clean, dirty = worktree_is_clean("")
    assert clean is True
    assert dirty == []


def test_dirty_blocks_with_filelist():
    """Cualquier línea de porcelain → sucio, con la lista de archivos eludidos."""
    porcelain = " M scripts/foo.py\n?? nuevo.py\n"
    clean, dirty = worktree_is_clean(porcelain)
    assert clean is False
    assert "scripts/foo.py" in dirty
    assert "nuevo.py" in dirty


def test_staged_only_is_clean():
    """Archivos completamente staged (2ª columna en blanco) no ensucian el tree."""
    # 'A  x' = added+staged sin cambios en working tree → limpio para el commit.
    clean, dirty = worktree_is_clean("A  staged_file.py\n")
    assert clean is True


def test_adoption_date_stable_when_unchanged(tmp_path, monkeypatch):
    """VC-141 (idempotencia): si el estado de adopción de un proyecto no cambia,
    `adoption_verified_date` NO debe reescribirse. Evita churn de timestamps que
    ensucia el working tree en cada commit."""
    reg = tmp_path / "REGISTRY.json"
    reg.write_text(
        json.dumps({"projects": [{"name": "P", "path": str(tmp_path), "status": "active"}]}),
        encoding="utf-8",
    )
    monkeypatch.setattr(vpa, "REGISTRY_PATH", reg)
    monkeypatch.setattr(
        vpa,
        "_check_project",
        lambda p: {"hook": True, "auditor": True, "tests": True, "path_missing": False},
    )

    vpa.run(write=True)
    first = json.loads(reg.read_text(encoding="utf-8"))["projects"][0]["adoption_verified_date"]
    vpa.run(write=True)
    second = json.loads(reg.read_text(encoding="utf-8"))["projects"][0]["adoption_verified_date"]
    assert first == second  # estado igual → fecha intacta
