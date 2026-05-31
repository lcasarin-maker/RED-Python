"""
test_golden_standard_compliance.py — Dynamic Golden Standard compliance verification.
Ensures that all 275+ flaws defined in the libraries have documented actions and physical tests.
"""
# -*- coding: utf-8 -*-

import re
import json
import unittest
from pathlib import Path
from scripts.run_security_audit_12d import DeepForensicAuditor

_ROOT = Path(__file__).resolve().parent.parent

class TestGoldenStandardCompliance(unittest.TestCase):
    """Oráculo adversarial verifying 100% mapping of Golden Standard flaws to physical tests."""

    @classmethod
    def setUpClass(cls):
        cls.json_path = _ROOT / ".protocol" / "metadata" / "golden_standard_audit.json"
        cls.yaml_path = _ROOT / "Golden_Standard" / "golden_standard.yaml"

    def _extract_all_library_ids(self) -> set:
        """Parse the centralized YAML and extract all defined flaw IDs in real-time."""
        import yaml
        ids = set()
        if not self.yaml_path.exists():
            return ids
        
        with open(self.yaml_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
            
        row_re = re.compile(r"^\s*\|\s*(?P<id>(?:VT|VC|TK-F|TK)-\d+)\s*\|")
        for key in ("testing_vices_details", "coding_vices_details", "tokenomics_details"):
            block = config.get(key, "")
            for line in block.splitlines():
                m = row_re.match(line)
                if m:
                    ids.add(m.group("id").strip())
        return ids


    def test_database_exists_and_parseable(self):
        """Verify that the JSON audit database exists and is valid JSON."""
        self.assertTrue(self.json_path.exists(), "golden_standard_audit.json does not exist in .protocol/metadata/")
        try:
            with open(self.json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.assertIsInstance(data, dict, "JSON root is not a dictionary")
        except json.JSONDecodeError as exc:
            self.fail(f"Failed to parse golden_standard_audit.json: {exc}")

    def test_zero_missing_gaps_coverage(self):
        """Dynamic coverage gate: asserts that 100% of defined Golden Standard flaw IDs exist in the database."""
        defined_ids = self._extract_all_library_ids()
        self.assertGreater(len(defined_ids), 0, "No flaw IDs were extracted from Golden Standard markdown files.")

        with open(self.json_path, "r", encoding="utf-8") as f:
            database = json.load(f)

        missing_ids = defined_ids - set(database.keys())
        self.assertEqual(
            len(missing_ids), 0,
            f"Gaps detected! The following flaw IDs are defined in the libraries but missing in the audit database: {sorted(missing_ids)}"
        )

    def test_listed_tokenomics_ids_have_detail_rows(self):
        """Sprint 3.1: todo ID en la lista `tokenomics:` DEBE tener fila de tabla en
        `tokenomics_details`. Los IDs fantasma (listados pero sin fila) son invisibles al
        generador de cobertura → falso '0 gaps'. Es TK-043/PI-007 (huérfanos de catálogo)
        ocurriendo dentro del propio catálogo. Falla HOY con TK-044/TK-045."""
        import yaml
        with open(self.yaml_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        listed = config.get("tokenomics", [])
        details = config.get("tokenomics_details", "")
        phantom = sorted(
            tid for tid in listed
            if not re.search(rf"\|\s*{re.escape(tid)}\s*\|", details)
        )
        self.assertEqual(
            phantom, [],
            f"IDs fantasma en `tokenomics:` sin fila en tokenomics_details: {phantom}"
        )

    def test_cognitive_density_and_completeness(self):
        """Asserts that all mapped entries have fully populated, high-density mitigation actions."""
        with open(self.json_path, "r", encoding="utf-8") as f:
            database = json.load(f)

        for flaw_id, entry in database.items():
            # Verify basic structure
            for field in ("id", "title", "category", "symptom", "cause", "solution", "status", "action", "validating_mechanism"):
                self.assertIn(field, entry, f"Missing field '{field}' in entry for {flaw_id}")
                val = entry[field]
                self.assertTrue(val and str(val).strip(), f"Field '{field}' in entry for {flaw_id} is empty or a placeholder")
            
            # Verify status is one of the valid statuses
            self.assertIn(
                entry["status"], ("PREVENTED", "REMEDIATED", "AUDITED", "NOT_APPLICABLE", "DOC_ONLY"),
                f"Invalid status '{entry['status']}' in entry for {flaw_id}"
            )

    def test_physical_validation_exists(self):
        """Oráculo verification: ensures that the validating test or checker function named in each entry exists physically."""
        with open(self.json_path, "r", encoding="utf-8") as f:
            database = json.load(f)

        # Collect all python files in tests/ and scripts/ to scan for test function signatures
        tests_dir = _ROOT / "tests"
        scripts_dir = _ROOT / "scripts"
        
        all_py_files = list(tests_dir.glob("**/*.py")) + list(scripts_dir.glob("**/*.py")) + [_ROOT / "auto_repair.py"]
        
        file_contents = {}
        for py_file in all_py_files:
            try:
                file_contents[py_file.name] = py_file.read_text(encoding="utf-8", errors="ignore")
            except OSError as exc:
                import logging
                logging.debug("Skipped unreadable file: %s", exc)

        # Scan for the physical existence of each validating mechanism
        for flaw_id, entry in database.items():
            mech = entry["validating_mechanism"]
            
            # 1. If it is a method on DeepForensicAuditor, check it directly
            if hasattr(DeepForensicAuditor, mech):
                self.assertTrue(
                    callable(getattr(DeepForensicAuditor, mech)),
                    f"Validating mechanism '{mech}' on DeepForensicAuditor is not callable for flaw {flaw_id}"
                )
                continue
            
            # 2. Otherwise, check if it's a test function or function name defined physically in python files
            found = False
            # Check for: def mech( or "mech" as string
            for file_name, text in file_contents.items():
                if f"def {mech}" in text or f"'{mech}'" in text or f'"{mech}"' in text:
                    found = True
                    break
            
            self.assertTrue(
                found,
                f"Vaporware test detected! Flaw {flaw_id} maps to validating mechanism '{mech}', but it does not exist physically in scripts/ or tests/."
            )

if __name__ == "__main__":
    unittest.main()
