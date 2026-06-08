"""Tests para el linter de alineación Código (Capa 1) ↔ Docs (Capa 2)."""
from scripts.alignment_checker import (
    _is_documentable_symbol,
    align_gate_enabled,
    detect_code_orphans,
    detect_doc_orphans,
    gate_exit_code,
    generate_report,
)

_NS = ("scripts", "protocol_engine", "tests", "src", "app")


def test_code_orphan_god_node_fails():
    """Un god_node sin arista 'documents' es un orphan crítico (FAIL)."""
    layer1 = {"god_nodes": ["scripts_foo"], "entry_points": [], "extraction_status": "ok"}
    orphans = detect_code_orphans(layer1, documented=set())
    assert any(o["code_id"] == "scripts_foo" and o["severity"] == "FAIL" for o in orphans)


# --- Fase 2c-a: acotar "símbolo crítico" a god_nodes documentables ---

def test_py_path_artifact_not_critical():
    """Un god_node `*_py_path` (constante Path(__file__)) es artefacto mecánico, no API → no orphan."""
    layer1 = {"god_nodes": ["scripts_core_utils_py_path"], "entry_points": [], "extraction_status": "ok"}
    orphans = detect_code_orphans(layer1, documented=set())
    assert orphans == []


def test_external_module_not_critical():
    """Un god_node fuera de los namespaces del repo (p.ej. `ast` stdlib) no lo gobernamos → no orphan."""
    layer1 = {"god_nodes": ["ast"], "entry_points": [], "extraction_status": "ok"}
    orphans = detect_code_orphans(layer1, documented=set())
    assert orphans == []


def test_real_god_node_under_namespace_still_critical():
    """Un god_node real bajo namespace (incluso `protocol_engine_*`) sigue siendo crítico."""
    layer1 = {"god_nodes": ["protocol_engine_init"], "entry_points": [], "extraction_status": "ok"}
    orphans = detect_code_orphans(layer1, documented=set())
    assert any(o["code_id"] == "protocol_engine_init" for o in orphans)


def test_entry_points_not_critical():
    """entry_points (todo `_main`) ya NO son críticos: tener main() no es criticidad."""
    layer1 = {"god_nodes": [], "entry_points": ["scripts_foo_main"], "extraction_status": "ok"}
    orphans = detect_code_orphans(layer1, documented=set())
    assert orphans == []


def test_is_documentable_symbol_predicate():
    """El predicado puro: namespace-prefix sí, `_py_path` no, externo no."""
    assert _is_documentable_symbol("protocol_engine_init", _NS) is True
    assert _is_documentable_symbol("scripts_core_utils", _NS) is True
    assert _is_documentable_symbol("scripts_internal_graph_py_path", _NS) is False
    assert _is_documentable_symbol("ast", _NS) is False


def test_documented_god_node_passes():
    """Un god_node con arista 'documents' NO es orphan."""
    layer1 = {"god_nodes": ["scripts_foo"], "entry_points": [], "extraction_status": "ok"}
    orphans = detect_code_orphans(layer1, documented={"scripts_foo"})
    assert orphans == []


def test_doc_orphan_is_advisory_warn():
    """Doc huérfano (sin enlaces) → WARN advisory, NUNCA FAIL: un doc sin links es
    higiene, no falla de correctitud (la doctrina/reglas no referencian código)."""
    layer2 = {"nodes": [{"id": "payments", "label": "payments.md"}], "edges": []}
    orphans = detect_doc_orphans(layer2)
    assert any(o["doc_id"] == "payments" and o["severity"] == "WARN" for o in orphans)
    assert all(o["severity"] != "FAIL" for o in orphans)


def test_doc_orphan_arch_warns():
    """Doc de arquitectura sin enlaces → WARN (tolerado)."""
    layer2 = {"nodes": [{"id": "architecture", "label": "architecture.md"}], "edges": []}
    orphans = detect_doc_orphans(layer2)
    assert any(o["doc_id"] == "architecture" and o["severity"] == "WARN" for o in orphans)


def test_skip_align_excludes_doc():
    """Un nodo con skip_align=True se excluye del análisis de orphans."""
    layer2 = {"nodes": [{"id": "payments", "label": "payments.md", "skip_align": True}], "edges": []}
    orphans = detect_doc_orphans(layer2)
    assert orphans == []


def test_failed_extraction_aborts_not_green():
    """H2/H5: si Layer 1 falló la extracción, el reporte NO debe declarar 0 orphans.
    Debe abortar con exit_code=1 y status untrustworthy (no falso verde)."""
    layer1 = {"god_nodes": [], "entry_points": [], "extraction_status": "failed"}
    layer2 = {"nodes": [], "edges": []}
    report = generate_report(layer1, layer2)
    assert report["exit_code"] == 1
    assert report["status"] == "untrustworthy"


# --- Fase 2c-b: gate opt-in (anti-brick de satélites no documentados) ---

def test_gate_opt_in_blocks_only_when_enabled():
    """Con gate habilitado, un FAIL bloquea (exit 1); sin habilitar, advisory (exit 0)."""
    report = {"exit_code": 1}
    assert gate_exit_code(report, gate_enabled=True) == 1
    assert gate_exit_code(report, gate_enabled=False) == 0


def test_gate_green_report_exits_zero_regardless():
    """Un reporte verde (exit 0) sale 0 con o sin gate."""
    report = {"exit_code": 0}
    assert gate_exit_code(report, gate_enabled=True) == 0
    assert gate_exit_code(report, gate_enabled=False) == 0


def test_align_gate_marker_detection(tmp_path):
    """El marcador `.protocol/align_gate.enabled` activa el gate; ausente = advisory."""
    assert align_gate_enabled(tmp_path) is False
    (tmp_path / ".protocol").mkdir()
    (tmp_path / ".protocol" / "align_gate.enabled").write_text("", encoding="utf-8")
    assert align_gate_enabled(tmp_path) is True


def test_clean_alignment_is_green():
    """Sin orphans críticos → exit_code 0."""
    layer1 = {"god_nodes": ["scripts_foo"], "entry_points": [], "extraction_status": "ok"}
    layer2 = {
        "nodes": [{"id": "foo_doc", "label": "foo_doc.md"}],
        "edges": [{"source": "foo_doc", "target": "scripts_foo", "relation": "documents"}],
    }
    report = generate_report(layer1, layer2)
    assert report["exit_code"] == 0
    assert report["status"] == "checked"
