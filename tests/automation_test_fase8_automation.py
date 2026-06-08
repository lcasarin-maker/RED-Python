#!/usr/bin/env python3
"""
TEST FASE 8 AUTOMATION — Valida RTK, Headspace, Session Export
"""

import subprocess
import sys


def test_rtk_module():
    """Test: RTK module loads and processes output"""
    from scripts.manage_tokens import OutputCompressor as RTKAutoCompress

    text = "hello world" * 100  # ~400 chars = ~100 tokens
    tokens = RTKAutoCompress.estimate_tokens(text)
    assert tokens > 0, "estimate_tokens failed"

    long_text = "x" * 5000  # ~1250 tokens
    assert RTKAutoCompress.should_compress(long_text), "should_compress failed"


def test_headspace_module():
    """Test: Headspace module loads and estimates context"""
    try:
        from scripts.trigger_context_compression import HeadspaceAutoTrigger

        trigger = HeadspaceAutoTrigger()

        # Test: context estimation (may be > 0 due to AGENT.md/CLAUDE.md in CWD)
        tokens = trigger.estimate_context_usage()
        assert isinstance(tokens, int), "estimate_context_usage failed"

        # Test: check report has required keys
        report = trigger.check()
        assert 0 <= report["context_percentage"] <= 100, "percentage out of range"

        # Test: threshold check
        assert isinstance(
            report["should_compress"], bool
        ), "should_compress must be bool"

        print("[PASS] headspace_auto_trigger module")
        pass
    except Exception as e:
        print(f"[FAIL] headspace_auto_trigger: {e}")
        assert False, "Headspace module failed"


def test_export_module():
    """Test: Session export module loads"""
    try:
        from scripts.export_retrospective import AutoExportRetrospective

        exporter = AutoExportRetrospective()

        # Test: DB setup
        exporter.setup_db()

        # Test: session extraction (may be None if HISTORIAL.md empty)
        session = exporter.extract_latest_session()
        # session can be None, that's ok

        print("[PASS] auto_export_retrospective module")
        pass
    except Exception as e:
        print(f"[FAIL] auto_export_retrospective: {e}")
        assert False, "Export module failed"


def test_compact_helper():
    """Test: Compact helper module loads"""
    from scripts.compact_automation_helper import CompactAutomationHelper

    helper = CompactAutomationHelper()

    assert hasattr(helper, "run_compress_historial"), "missing run_compress_historial"
    assert hasattr(helper, "run_headspace_trigger"), "missing run_headspace_trigger"
    assert hasattr(helper, "run_session_export"), "missing run_session_export"
    assert hasattr(helper, "auto_compact_prepare"), "missing auto_compact_prepare"


def test_cli_headspace():
    """Test: Headspace CLI works"""
    result = subprocess.run(
        ["python", "scripts/trigger_context_compression.py", "--check"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert (
        result.returncode == 0
    ), f"exit code {result.returncode}\nstderr: {result.stderr}"
    combined = result.stdout + result.stderr
    assert "Context" in combined or "[INFO]" in combined, f"missing output: {combined}"


def test_cli_export():
    """Test: Session export CLI works"""
    result = subprocess.run(
        ["python", "scripts/export_retrospective.py", "--auto"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert (
        result.returncode == 0
    ), f"exit code {result.returncode}\nstderr: {result.stderr}"
    output = result.stdout + result.stderr
    assert output.strip(), f"script produced no output: {output}"


if __name__ == "__main__":
    import os

    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    print("\n[TEST] FASE 8 AUTOMATION VALIDATION\n")

    results = {
        "rtk_module": test_rtk_module(),
        "headspace_module": test_headspace_module(),
        "export_module": test_export_module(),
        "compact_helper": test_compact_helper(),
        "headspace_cli": test_cli_headspace(),
        "export_cli": test_cli_export(),
    }

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    print(f"\n[SUMMARY] {passed}/{total} tests passed")

    if passed == total:
        print("[OK] FASE 8 automation ready for production")
        sys.exit(0)
    else:
        print("[FAIL] Some tests failed")
        sys.exit(1)
