"""Las premisas sobre las que se descartaron tres fichas siguen siendo ciertas.

Una ficha descartada (`void_wontfix`) se sostiene en un hecho del proyecto. Estos tests lo miden, para
que el dia que deje de ser cierto el descarte se reabra solo:

  - HARVEST-DeusData-codebase-memory-mcp: red_python no analiza codigo fuente (borra DIRECTORIOS vacios).
  - HARVEST-MadScientist-HN-mapper: red_python no construye ningun grafo de dependencias.
  - TASK-001: ningun archivo del proyecto cita la regla SP-011 de Cerberus que exigia el renombrado.
"""

import ast
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
EXCLUIDOS = {"tests", "archive", "deprecated", "build", "dist", "__pycache__", ".venv", "venv", "Wiki", "tasks", "docs"}
ANALISIS_DE_CODIGO = {"ast", "libcst", "tokenize", "lib2to3", "parso", "jedi", "rope"}
GRAFOS = {"networkx", "graphlib", "igraph", "graph_tool"}


def _modulos_del_producto() -> list[Path]:
    return [p for p in RAIZ.rglob("*.py") if not EXCLUIDOS & set(p.relative_to(RAIZ).parts)]


def _importados(ruta: Path) -> set[str]:
    nombres: set[str] = set()
    for nodo in ast.walk(ast.parse(ruta.read_text(encoding="utf-8"))):
        if isinstance(nodo, ast.Import):
            nombres |= {a.name.split(".")[0] for a in nodo.names}
        elif isinstance(nodo, ast.ImportFrom) and nodo.module:
            nombres.add(nodo.module.split(".")[0])
    return nombres


def _usan(prohibidos: set[str]) -> dict[str, list[str]]:
    return {
        str(p.relative_to(RAIZ)): sorted(hallados)
        for p in _modulos_del_producto() if (hallados := _importados(p) & prohibidos)
    }


def test_el_detector_ve_un_import_prohibido(tmp_path):
    ejemplo = tmp_path / "x.py"
    ejemplo.write_text("import ast\nfrom networkx import Graph\n", encoding="utf-8")
    assert _importados(ejemplo) == {"ast", "networkx"}


def test_red_python_no_analiza_codigo_fuente():
    assert {p.name for p in _modulos_del_producto()} >= {"core.py", "filters.py", "red.py"}, "el test dejo de mirar"
    assert _usan(ANALISIS_DE_CODIGO) == {}
    assert "directorios vac" in (RAIZ / "SPEC.md").read_text(encoding="utf-8").lower()


def test_red_python_no_construye_grafos_de_dependencias():
    assert {p.name for p in _modulos_del_producto()} >= {"core.py", "filters.py", "red.py"}, "el test dejo de mirar"
    assert _usan(GRAFOS) == {}


def test_ningun_archivo_del_proyecto_cita_la_regla_sp_011_de_cerberus():
    patron = re.compile(r"SP-011|Cerberus governance")
    citan = [
        str(p.relative_to(RAIZ))
        for p in list(RAIZ.glob("*.md")) + list(RAIZ.glob("*.py")) + list((RAIZ / "docs").rglob("*.md"))
        if patron.search(p.read_text(encoding="utf-8", errors="replace"))
    ]
    assert citan == [], f"vuelve a citarse la doctrina retirada: {citan}"
    # control: la busqueda no esta vacia por construccion, la propia ficha cerrada SI la cita
    assert patron.search((RAIZ / "tasks" / "done" / "TASK-001.md").read_text(encoding="utf-8"))
