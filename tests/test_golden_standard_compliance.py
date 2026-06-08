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
from protocol_engine import (
    get_golden_catalog_paths,
    get_golden_standard_root,
    load_golden_standard_audit,
    load_golden_standard_catalogs,
)

_ROOT = Path(__file__).resolve().parent.parent


class TestGoldenStandardCompliance(unittest.TestCase):
    """Oráculo adversarial verifying 100% mapping of Golden Standard flaws to physical tests."""

    @classmethod
    def setUpClass(cls):
        cls.json_path = _ROOT / ".protocol" / "metadata" / "golden_standard_audit.json"
        # GS migró a repo independiente en 2026-06-04 — usar knowledge_loader para resolver
        cls.manifest_path = get_golden_standard_root() / "golden_standard.yaml"
        cls.catalog_paths = get_golden_catalog_paths()
        cls.catalogs = load_golden_standard_catalogs()
        cls.audit_db = load_golden_standard_audit()

    def test_audit_db_is_memoized(self):
        """C1 (VC-048): load_golden_standard_audit memoiza — dos llamadas devuelven el
        MISMO objeto (antes del caché construía un dict nuevo cada vez)."""
        first = load_golden_standard_audit()
        second = load_golden_standard_audit()
        self.assertIs(first, second)
        self.assertGreater(len(first), 0)

    def _extract_all_library_ids(self) -> set:
        """Parse the split catalogs and extract all defined flaw IDs in real-time."""
        ids = set()
        for config in self.catalogs.values():
            if isinstance(config, dict) and "items" in config:
                for item in config["items"]:
                    ids.add(item["id"])
        return ids

    def test_database_exists_and_parseable(self):
        """Verify that the JSON audit database exists and is valid JSON."""
        self.assertTrue(
            self.json_path.exists(),
            "golden_standard_audit.json does not exist in .protocol/metadata/",
        )
        # Validate file size (not empty)
        file_size = self.json_path.stat().st_size
        self.assertGreater(file_size, 100, "golden_standard_audit.json too small to be real")

        try:
            with open(self.json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.assertIsInstance(data, dict, "JSON root is not a dictionary")
            # Validate non-empty dictionary
            self.assertGreater(len(data), 0, "golden_standard_audit.json is empty dict")
        except json.JSONDecodeError as exc:
            self.fail(f"Failed to parse golden_standard_audit.json: {exc}")

    def test_manifest_is_split_and_resolves_catalogs(self):
        """The manifest must exist and point to the split catalogs."""
        self.assertTrue(
            self.manifest_path.exists(), "golden_standard.yaml manifest does not exist"
        )
        # Validate manifest has content
        manifest_size = self.manifest_path.stat().st_size
        self.assertGreater(manifest_size, 100, "golden_standard.yaml exists but is empty or too small")

        self.assertIn("tokenomics", self.catalogs)
        self.assertIn("testing_vices", self.catalogs)
        self.assertIn("coding_vices", self.catalogs)
        self.assertIn("project_insights", self.catalogs)
        for name, path in self.catalog_paths.items():
            self.assertTrue(path.exists(), f"Catalog {name} does not exist at {path}")
            # Validate each catalog has content
            catalog_size = path.stat().st_size
            self.assertGreater(catalog_size, 50, f"Catalog {name} exists but is empty or too small")

    def test_zero_missing_gaps_coverage(self):
        """Dynamic coverage gate: asserts that 100% of defined Golden Standard flaw IDs exist in the database."""
        defined_ids = self._extract_all_library_ids()
        self.assertGreater(
            len(defined_ids),
            0,
            "No flaw IDs were extracted from Golden Standard markdown files.",
        )

        with open(self.json_path, "r", encoding="utf-8") as f:
            database = json.load(f)

        missing_ids = defined_ids - set(database.keys())
        self.assertEqual(
            len(missing_ids),
            0,
            f"Gaps detected! The following flaw IDs are defined in the libraries but missing in the audit database: {sorted(missing_ids)}",
        )

    def test_catalog_id_formats(self):
        """Ensure that every item id in the catalogs matches the required prefix formats."""
        pattern = re.compile(r"^(?:VT-|VC-|TK-|TK-F)\d+$")
        for name, config in self.catalogs.items():
            if isinstance(config, dict) and "items" in config:
                for item in config["items"]:
                    flaw_id = item["id"]
                    self.assertTrue(
                        pattern.match(flaw_id),
                        f"Invalid flaw ID format: '{flaw_id}' in catalog '{name}'",
                    )

    def test_cognitive_density_and_completeness(self):
        """Asserts that all mapped entries have fully populated, high-density mitigation actions."""
        database = self.audit_db

        for flaw_id, entry in database.items():
            # Verify basic structure
            for field in (
                "id",
                "title",
                "category",
                "symptom",
                "cause",
                "solution",
                "status",
                "action",
                "validating_mechanism",
            ):
                self.assertIn(
                    field, entry, f"Missing field '{field}' in entry for {flaw_id}"
                )
                val = entry[field]
                self.assertTrue(
                    val and str(val).strip(),
                    f"Field '{field}' in entry for {flaw_id} is empty or a placeholder",
                )

            # Verify status is one of the valid statuses
            self.assertIn(
                entry["status"],
                ("PREVENTED", "REMEDIATED", "AUDITED", "NOT_APPLICABLE", "DOC_ONLY"),
                f"Invalid status '{entry['status']}' in entry for {flaw_id}",
            )
            if entry["validating_mechanism"] == "DOC_ONLY":
                self.assertIn(
                    entry.get("downstream_verification"),
                    ("none", "required"),
                    f"DOC_ONLY entry {flaw_id} must preserve downstream_verification",
                )

    def test_doc_only_entries_preserve_downstream_verification(self):
        """DOC_ONLY entries must keep the consumer-contract bifurcation alive."""
        doc_only = {
            flaw_id: entry
            for flaw_id, entry in self.audit_db.items()
            if entry["validating_mechanism"] == "DOC_ONLY"
        }
        self.assertGreater(
            len(doc_only),
            0,
            "Expected at least one DOC_ONLY entry in the normalized audit database.",
        )
        for flaw_id, entry in doc_only.items():
            self.assertIn(
                "downstream_verification",
                entry,
                f"DOC_ONLY entry {flaw_id} lost downstream_verification during ingestion",
            )
            self.assertIn(
                entry["downstream_verification"],
                ("none", "required"),
                f"Invalid downstream_verification for DOC_ONLY entry {flaw_id}",
            )

    def test_physical_validation_exists(self):
        """Oráculo verification: ensures that the validating test or checker function named in each entry exists physically."""
        database = self.audit_db

        # Collect all python files in tests/ and scripts/ to scan for test function signatures
        tests_dir = _ROOT / "tests"
        scripts_dir = _ROOT / "scripts"

        all_py_files = list(tests_dir.glob("**/*.py")) + list(
            scripts_dir.glob("**/*.py")
        )

        file_contents = {}
        for py_file in all_py_files:
            try:
                file_contents[py_file.name] = py_file.read_text(
                    encoding="utf-8", errors="ignore"
                )
            except OSError as exc:
                import logging

                logging.debug("Skipped unreadable file: %s", exc)

        # Scan for the physical existence of each validating mechanism
        for flaw_id, entry in database.items():
            mech = entry["validating_mechanism"]
            if mech == "DOC_ONLY":
                continue

            # 1. If it is a method on DeepForensicAuditor, check it directly
            if hasattr(DeepForensicAuditor, mech):
                self.assertTrue(
                    callable(getattr(DeepForensicAuditor, mech)),
                    f"Validating mechanism '{mech}' on DeepForensicAuditor is not callable for flaw {flaw_id}",
                )
                continue

            # 2. Otherwise, check if it's a test function or function name defined physically in python files
            found = False
            # Check for: def mech(
            for file_name, text in file_contents.items():
                if f"def {mech}" in text:
                    found = True
                    break

            self.assertTrue(
                found,
                f"Vaporware test detected! Flaw {flaw_id} maps to validating mechanism '{mech}', but it does not exist physically in scripts/ or tests/.",
            )


if __name__ == "__main__":
    unittest.main()
