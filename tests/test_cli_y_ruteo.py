"""`red.py --scan` entra al modo CLI y escanea las rutas pedidas.

SPEC: "Dual Mode: ... GUI or CLI with the `--scan` flag" y "`red.py`: routes execution to the CLI or the GUI".
Se ejecuta `red.py` como proceso, que es como lo lanza el menu contextual de Windows.
"""

import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def test_scan_por_cli_encuentra_la_carpeta_vacia_y_no_la_llena(tmp_path):
    (tmp_path / "vacia").mkdir()
    (tmp_path / "llena").mkdir()
    (tmp_path / "llena" / "dato.txt").write_text("contenido real", encoding="utf-8")
    salida = tmp_path / "resultado.txt"

    hecho = subprocess.run(
        [sys.executable, str(RAIZ / "red.py"), "--scan", str(tmp_path), "--dry-run", "--export", str(salida)],
        cwd=RAIZ, capture_output=True, text=True, timeout=60, check=False,
    )

    assert hecho.returncode == 0, hecho.stderr
    lineas = salida.read_text(encoding="utf-8").splitlines()
    assert any(l_.startswith("empty\t") and l_.endswith("vacia") for l_ in lineas), lineas
    assert not any(l_.endswith("llena") for l_ in lineas), lineas
    assert (tmp_path / "vacia").exists(), "--dry-run no debe borrar nada"


def test_scan_por_cli_con_una_ruta_inexistente_falla_sin_abrir_la_gui(tmp_path):
    hecho = subprocess.run(
        [sys.executable, str(RAIZ / "red.py"), "--scan", str(tmp_path / "no_existe"), "--dry-run"],
        cwd=RAIZ, capture_output=True, text=True, timeout=60, check=False,
    )
    assert hecho.returncode != 0
    assert "invalid or missing path" in hecho.stderr
