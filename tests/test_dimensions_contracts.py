from __future__ import annotations

import json

import dimensions
from dimensions.base import Dimension, Finding, Status
from dimensions.context import AuditContext
from dimensions.d3_dead_code import D3DeadCode
from dimensions.d7_security import D7Security
from dimensions.d11_dependency import D11Dependency
from dimensions.d13_observable import (
    D13Observable,
    D13Report,
    DecisionLogger,
    DivergenceDetector,
    count_tokens,
    estimate_cost,
    _parse_line,
)
from dimensions.d14_discourse_rigor import (
    D14DiscourseRigor,
    DiscourseMetric,
    DiscourseValidator,
)


def test_dimensions_registry_and_base_contract():
    names = {type(item).__name__ for item in dimensions.REGISTRY}
    assert {
        "D3DeadCode",
        "D7Security",
        "D11Dependency",
        "D13Observable",
        "D14DiscourseRigor",
    } <= names

    finding = Finding("D1", "blocked")
    assert finding.is_blocking() is True
    assert Status.PASS.value == "PASS"
    assert isinstance(dimensions.REGISTRY[0], Dimension)


def test_audit_context_caches_files_and_ast(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    (project / "keep.py").write_text("x = 1\n", encoding="utf-8")
    excluded = project / "deprecated"
    excluded.mkdir()
    (excluded / "skip.py").write_text("x = 2\n", encoding="utf-8")
    pycache = project / "__pycache__"
    pycache.mkdir()
    (pycache / "skip.py").write_text("x = 3\n", encoding="utf-8")
    good = project / "good.py"
    good.write_text("value = 1\n", encoding="utf-8")
    bad = project / "bad.py"
    bad.write_text("def broken(:\n", encoding="utf-8")

    ctx = AuditContext(project)
    files = ctx.py_files()
    assert [p.name for p in files] == ["bad.py", "good.py", "keep.py"]
    assert ctx.py_files() is files
    assert ctx.ast_of(good) is ctx.ast_of(good)
    assert ctx.ast_of(bad) is None


def test_d3_dead_code_reports_missing_tools_and_matches_output(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    scripts = root / "scripts"
    scripts.mkdir(parents=True)
    (scripts / "file.py").write_text("value = 1\n", encoding="utf-8")
    ctx = AuditContext(root)
    d3 = D3DeadCode()

    monkeypatch.setattr("dimensions.d3_dead_code.shutil.which", lambda name: "")
    findings = d3.audit(ctx)
    assert len(findings) == 2
    assert all(f.status is Status.UNAVAILABLE for f in findings)

    monkeypatch.setattr("dimensions.d3_dead_code.shutil.which", lambda name: "tool")

    class Result:
        stdout = "scripts/file.py:1: F401 imported but unused\nunused function file.py"

    monkeypatch.setattr(
        "dimensions.d3_dead_code.subprocess.run", lambda *a, **k: Result()
    )
    findings = d3.audit(ctx)
    assert any("ruff" in f.message for f in findings)
    assert any("vulture" in f.message for f in findings)


def test_d7_security_regex_and_bandit_paths(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    scripts = root / "scripts"
    scripts.mkdir(parents=True)
    (scripts / "danger.py").write_text('password = "secret1234"\n', encoding="utf-8")
    ctx = AuditContext(root)
    d7 = D7Security()

    monkeypatch.setattr(
        "dimensions.d7_security.importlib.util.find_spec", lambda name: None
    )
    findings = d7.audit(ctx)
    assert any("Credenciales hardcodeadas" in f.message for f in findings)
    assert any(f.status is Status.UNAVAILABLE for f in findings)

    monkeypatch.setattr(
        "dimensions.d7_security.importlib.util.find_spec", lambda name: object()
    )

    class Result:
        stdout = json.dumps(
            {
                "results": [
                    {
                        "issue_severity": "HIGH",
                        "test_id": "B001",
                        "filename": str(scripts / "danger.py"),
                        "line_number": 1,
                        "issue_text": "bad pattern",
                    }
                ]
            }
        )

    monkeypatch.setattr(
        "dimensions.d7_security.subprocess.run", lambda *a, **k: Result()
    )
    findings = d7.audit(ctx)
    assert any("bandit B001 HIGH" in f.message for f in findings)


def test_d11_dependency_handles_trivy_and_pypi(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    root.mkdir()
    (root / "requirements.txt").write_text("demo==1.0.0\n", encoding="utf-8")
    ctx = AuditContext(root)
    d11 = D11Dependency()

    monkeypatch.setattr("dimensions.d11_dependency._find_trivy", lambda: "")
    findings = d11._trivy(ctx)
    assert findings[0].status is Status.UNAVAILABLE

    class Result:
        returncode = 0
        stdout = json.dumps(
            {
                "Results": [
                    {
                        "Target": ".",
                        "Vulnerabilities": [
                            {
                                "VulnerabilityID": "CVE-1",
                                "PkgName": "demo",
                                "InstalledVersion": "1.0.0",
                                "FixedVersion": "1.0.1",
                            }
                        ],
                    }
                ]
            }
        )
        stderr = ""

    monkeypatch.setattr("dimensions.d11_dependency._find_trivy", lambda: "trivy")
    monkeypatch.setattr(
        "dimensions.d11_dependency.subprocess.run", lambda *a, **k: Result()
    )
    findings = d11._trivy(ctx)
    assert any("VT-112 CRITICAL" in f.message for f in findings)

    class Response:
        def read(self):
            return json.dumps(
                {
                    "info": {"version": "1.2.0"},
                    "releases": {"1.0.0": [{"yanked": True}]},
                }
            ).encode("utf-8")

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    monkeypatch.setattr(
        "dimensions.d11_dependency.urllib.request.urlopen", lambda *a, **k: Response()
    )
    findings = d11._pypi(ctx)
    assert any(f.status is Status.FAIL for f in findings)


def test_d13_observable_observes_and_reports(tmp_path, monkeypatch):
    transcript = tmp_path / "transcript.jsonl"
    transcript.write_text(
        "\n".join(
            [
                json.dumps(
                    {"type": "assistant", "message": {"usage": {"output_tokens": 10}}}
                ),
                json.dumps({"isCompactSummary": True, "type": "user"}),
                json.dumps(
                    {"type": "assistant", "message": {"usage": {"output_tokens": 7}}}
                ),
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr("dimensions.d13_observable.tiktoken", None)
    assert count_tokens(str(transcript)) == 0
    assert estimate_cost(1500) == 0.003
    assert _parse_line("not json") is None

    detector = DivergenceDetector()
    detector.can_do.add("scan")
    detector.cannot_do.add("delete")
    assert detector.check("scan")["allowed"] is True
    assert detector.check("delete")["allowed"] is False

    logger = DecisionLogger(log_dir=str(tmp_path / "logs"))
    decision_id = logger.log_decision("agent", "decide", "reason", "action", "ok")
    assert decision_id

    report = D13Report(max_decisions=5)
    monkeypatch.setattr(
        report, "_load_token_data", lambda: {"TOTAL": {"tokens": 1, "cost_usd": 0.001}}
    )
    monkeypatch.setattr(report, "_load_recent_decisions", lambda: [{"id": decision_id}])
    data = report.generate_json()
    assert data["tokens"]["TOTAL"]["tokens"] == 1

    obs = D13Observable()
    result = obs.observe_session(str(transcript))
    assert result == {"assistant_messages": 1, "output_tokens": 7}


def test_d14_discourse_validator_and_hook_response():
    validator = DiscourseValidator(response="This works because it is clear [1].")
    metrics = validator.validate()
    assert metrics["status"] in {"PASS", "WARN"}
    assert isinstance(validator.metrics, DiscourseMetric)

    bad = DiscourseValidator(response="maybe perhaps kind of vague")
    bad_metrics = bad.validate()
    assert bad_metrics["status"] == "FAIL"

    hook = D14DiscourseRigor()
    findings = hook.audit_response("maybe perhaps kind of vague", threshold=0.9)
    assert findings and findings[0].status in {Status.WARN, Status.FAIL}
