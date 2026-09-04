"""Tests de scripts/graph_report.py (TASK-RED-01).

Nunca contra ~/projects real: cada test construye su propia flota sintetica
en tmp_path. El caso mas importante (test_no_importa_modulos_del_satelite)
prueba la garantia central del ticket -- un satelite con un import roto no
puede tumbar el diagnostico de la flota, porque el diagnostico nunca
ejecuta su codigo.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import graph_report as gr


def _satelite(root: Path, nombre: str, hook=False, auditor=False, tests=False) -> Path:
    d = root / nombre
    (d / ".git").mkdir(parents=True)
    if hook:
        (d / ".pre-commit-config.yaml").write_text("repos: []\n", encoding="utf-8")
    if auditor:
        (d / "gates").mkdir()
        (d / "gates" / "algo.py").write_text("# gate\n", encoding="utf-8")
    if tests:
        (d / "tests").mkdir()
        (d / "tests" / "test_algo.py").write_text("def test_x(): pass\n", encoding="utf-8")
    return d


def test_scan_satellite_lee_los_tres_indicadores(tmp_path):
    d = _satelite(tmp_path, "completo", hook=True, auditor=True, tests=True)
    salud = gr.scan_satellite(d)
    assert salud.has_hook and salud.has_auditor and salud.has_tests
    assert salud.adoption_pct == 100
    assert salud.adoption_label == "full"


def test_scan_satellite_sin_nada(tmp_path):
    d = _satelite(tmp_path, "vacio")
    salud = gr.scan_satellite(d)
    assert not (salud.has_hook or salud.has_auditor or salud.has_tests)
    assert salud.adoption_pct == 0
    assert salud.adoption_label == "none"


def test_scan_satellite_parcial(tmp_path):
    d = _satelite(tmp_path, "parcial", hook=True, tests=True)
    salud = gr.scan_satellite(d)
    assert salud.adoption_label == "partial"
    assert salud.adoption_pct == 67


def test_hook_vacio_no_cuenta_como_hook(tmp_path):
    """Un archivo de 0 bytes no es un pre-commit real -- solo su presencia
    nominal no basta."""
    d = tmp_path / "s"
    (d / ".git").mkdir(parents=True)
    (d / ".pre-commit-config.yaml").write_text("", encoding="utf-8")
    assert gr._has_hook(d) is False


def test_gates_vacio_no_cuenta_como_auditor(tmp_path):
    d = tmp_path / "s"
    (d / "gates").mkdir(parents=True)
    assert gr._has_auditor(d) is False


def test_scan_fleet_ignora_directorios_sin_git(tmp_path):
    _satelite(tmp_path, "real", hook=True)
    (tmp_path / "no_es_repo").mkdir()  # sin .git
    resultado = gr.scan_fleet(tmp_path)
    assert [s.name for s in resultado] == ["real"]


def test_scan_fleet_directorio_ausente_no_falla(tmp_path):
    assert gr.scan_fleet(tmp_path / "no-existe") == []


def test_no_importa_modulos_del_satelite(tmp_path, monkeypatch):
    """La garantia central: un satelite cuyo codigo lanza al importarse NO
    debe poder tumbar el diagnostico de flota. Se prueba poniendo un .py
    que falla al importar en el path y confirmando que scan_fleet ni
    siquiera lo toca (solo mira el filesystem)."""
    d = _satelite(tmp_path, "satelite_roto", hook=True)
    (d / "modulo_que_explota.py").write_text("raise RuntimeError('boom')\n", encoding="utf-8")
    resultado = gr.scan_fleet(tmp_path)  # no debe lanzar RuntimeError
    assert resultado[0].name == "satelite_roto"
    assert resultado[0].has_hook is True


def test_render_markdown_agrupa_por_adopcion(tmp_path):
    salud = [
        gr.SatelliteHealth("a", True, True, True),
        gr.SatelliteHealth("b", True, False, False),
        gr.SatelliteHealth("c", False, False, False),
    ]
    salida = gr.render_markdown(salud)
    assert "Full adoption (1/3)" in salida
    assert "Partial adoption (1/3)" in salida
    assert "No adoption (1/3)" in salida
    assert "**a**" in salida and "**b**" in salida and "**c**" in salida


def test_to_fleet_catalog_rows_forma_compatible():
    salud = [gr.SatelliteHealth("x", True, False, True)]
    filas = gr.to_fleet_catalog_rows(salud)
    assert filas == [
        {"name": "x", "has_hooks": True, "has_gates_auditor": False, "has_tests": True, "adoption_pct": 67}
    ]


def test_main_escribe_json_si_se_pide(tmp_path):
    _satelite(tmp_path, "s1", hook=True, auditor=True, tests=True)
    salida_json = tmp_path / "out.json"
    rc = gr.main(["--projects-dir", str(tmp_path), "--json", str(salida_json)])
    assert rc == 0
    assert salida_json.is_file()
    import json
    datos = json.loads(salida_json.read_text(encoding="utf-8"))
    assert datos[0]["name"] == "s1"
    assert datos[0]["adoption_pct"] == 100
