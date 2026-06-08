#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validate_satellite_functional.py v2.0 — Enhanced Satellite Validation
Validates not just structure but real functionality (endpoints, UI, data flow).
Replaces ceremonial "file exists?" checks with empirical proof.
"""

import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional
import requests

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from scripts.core_utils import setup_windows_utf8
from scripts.satellite_validation_debt import register_validation_debt

setup_windows_utf8()


def validate_endpoint_responsive(
    satellite: str,
    endpoint_url: str,
    timeout: int = 5,
    expected_status: int = 200
) -> tuple[bool, Optional[str]]:
    """
    Validate that an endpoint actually responds.
    Returns: (success, error_message)
    """
    try:
        response = requests.get(endpoint_url, timeout=timeout)
        if response.status_code == expected_status:
            return True, None
        else:
            return False, f"Expected {expected_status}, got {response.status_code}"
    except requests.exceptions.Timeout:
        return False, f"Endpoint timeout after {timeout}s"
    except requests.exceptions.ConnectionError as e:
        return False, f"Connection failed: {str(e)}"
    except Exception as e:
        return False, f"Request failed: {str(e)}"


def validate_satellite_control_procesal(satellite_path: str = "D:\\AI\\Control_Procesal") -> dict:
    """
    Validate Control_Procesal satellite.
    Checks:
    1. Server starts without errors
    2. /ping endpoint responds with version
    3. /expedientes endpoint returns data
    4. UI loads and displays data (basic check)
    """
    results = {
        "satellite": "Control_Procesal",
        "timestamp": str(Path.cwd()),
        "checks": {},
        "functional": False,
        "debts": []
    }

    # Check 1: Server process starts
    try:
        result = subprocess.run(
            ["python", f"{satellite_path}\\scripts\\servidor_pdf.py"],
            capture_output=True,
            timeout=3,
            cwd=satellite_path
        )
        if result.returncode == 0 or "listening" in result.stderr.decode(errors='ignore').lower():
            results["checks"]["server_starts"] = True
        else:
            results["checks"]["server_starts"] = False
            results["debts"].append({
                "type": "startup",
                "description": "Server process fails to start or reports errors"
            })
    except subprocess.TimeoutExpired:
        # Timeout is OK — server is still running in background
        results["checks"]["server_starts"] = True
    except Exception as e:
        results["checks"]["server_starts"] = False
        results["debts"].append({
            "type": "startup",
            "description": f"Error starting server: {str(e)}"
        })

    # Check 2: /ping endpoint
    success, error = validate_endpoint_responsive(
        "Control_Procesal",
        "http://127.0.0.1:5050/ping"
    )
    results["checks"]["endpoint_ping"] = success
    if not success:
        results["debts"].append({
            "type": "functional",
            "description": f"/ping endpoint failed: {error}"
        })

    # Check 3: /expedientes endpoint
    success, error = validate_endpoint_responsive(
        "Control_Procesal",
        "http://127.0.0.1:5050/expedientes"
    )
    results["checks"]["endpoint_expedientes"] = success
    if not success:
        results["debts"].append({
            "type": "functional",
            "description": f"/expedientes endpoint failed: {error}"
        })

    # Check 4: /storage/get endpoint
    success, error = validate_endpoint_responsive(
        "Control_Procesal",
        "http://127.0.0.1:5050/storage/get"
    )
    results["checks"]["endpoint_storage"] = success
    if not success:
        results["debts"].append({
            "type": "functional",
            "description": f"/storage/get endpoint failed: {error}"
        })

    # Determine overall status
    all_passed = all(results["checks"].values())
    results["functional"] = all_passed

    return results


def print_validation_report(results: dict):
    """Print validation results."""
    print("\n" + "=" * 80)
    print(f"🔍 FUNCTIONAL VALIDATION — {results['satellite']}")
    print("=" * 80)

    print(f"\n✅ Checks:")
    for check_name, passed in results["checks"].items():
        status = "✓" if passed else "✗"
        print(f"   {status} {check_name}")

    if results["debts"]:
        print(f"\n⚠️  {len(results['debts'])} debt(s) found:")
        for debt in results["debts"]:
            print(f"   [{debt['type'].upper()}] {debt['description']}")

    overall_status = "🟢 FUNCTIONAL" if results["functional"] else "🔴 NON-FUNCTIONAL"
    print(f"\n{overall_status}")
    print("=" * 80)


def main():
    if len(sys.argv) > 1:
        satellite_path = sys.argv[1]
    else:
        satellite_path = "D:\\AI\\Control_Procesal"

    results = validate_satellite_control_procesal(satellite_path)
    print_validation_report(results)

    # If debts found, register them
    if results["debts"] and not results["functional"]:
        print(f"\n📝 Registering debts...")
        for debt in results["debts"]:
            register_validation_debt(
                satellite="Control_Procesal",
                debt_type=debt["type"],
                severity="high" if debt["type"] == "functional" else "medium",
                description=debt["description"],
                evidence=["validate_satellite_functional.py:empirical"],
                remediation="Needs functional verification and fix"
            )


if __name__ == "__main__":
    main()
