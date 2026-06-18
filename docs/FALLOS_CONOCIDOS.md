# KNOWN_FAILURES.md — Confirmed Bugs in Core Scripts
**Status:** ACTIVE | **Source:** `deprecated/docs/Fallos Concretos.md` audit | **Rescue date:** 2026-05-24

These are concrete failures, not theoretical ones. Each has an exact location in the code.

---

## ACTIVE FAILURES (10 confirmed)

> Scope note: F1, F4, and F10 are historical references to the previous auditor and the previous expanded auditor.
> Those executables no longer exist in the active Cerberus tree; they are kept here only for traceability.

### F1 - D7 Code Completeness not implemented
- **Status:** Historical. The previous auditor no longer exists in the active tree.
- **Symptom:** `rg D7` appears only in `HISTORIAL.md`, not in active legacy scripts.
- **Impact:** It was a real gap in the old version; today it remains only as documentation.
- **Required fix:** None in the active tree. Keep historical traceability only.

### F2 - Historical auditor: 88 validates a section, not compliance
- **Symptom:** The historical auditor verified that `SPEC.md` contained a section, not that the project complied with that specification.
- **Impact:** `SPEC.md` can be empty or stale and the auditor still passes.
- **Required fix:** Validate minimum content per section, not just the presence of a heading.

### F3 - Historical auditor: 102 validates docstrings by count, not quality
- **Symptom:** The historical implementation counted docstrings, but did not verify that the functions were connected, used, or correct.
- **Impact:** Dead code with docstrings passes the audit.
- **Required fix:** Cross-check documented functions against called/tested functions.

### F4 - Historical auditor: 164 detects textual "try" (false positive)
- **Status:** Historical. The referenced implementation no longer exists in the active tree.
- **Symptom:** The text detector searched for `"try"` to validate error handling. A useless `try` (`try: pass`) still passed.
- **Impact:** It was a real false positive in the old version.
- **Required fix:** None in the active tree.

### F5 - Historical expanded auditor: 89 uses protocol tests, not project tests
- **Symptom:** It ran the base protocol tests but did not require project-specific tests or a real startup proof.
- **Impact:** A project with no tests passes if the protocol has tests.
- **Required fix:** Detect and execute the audited project’s `tests/`.

### F6 - Historical expanded auditor: 125 skips human validation if the UI did not change
- **Symptom:** It only required human validation if UI files changed in the current commit.
- **Impact:** An already broken UI that did not change in this commit passed without review.
- **Required fix:** Periodic human validation, not only delta-based validation.

### F7 - `check_empirical_proof.py:98` accepts JSON without verifying the screenshot
- **Symptom:** Line 98 accepts recent JSON evidence, but does not validate that the screenshot/log matches the current code or proves the full flow.
- **Impact:** Evidence from a previous session passes as proof of the current session.
- **Required fix:** Validate the screenshot timestamp against the last commit timestamp.

### F8 - `validate_chunking.py:67` does not detect files that are "full but dead"
- **Symptom:** Line 67 protects against truncation, but not against complete files that do not execute any functional behavior.
- **Impact:** A file with 200 lines of placeholders passes.
- **Required fix:** Verify that main functions are called, not only defined.

### F9 - Tests use `assertIn` on text, not real execution
- **Symptom:** The tests in `tests/` validate that strings like `"MANDATO S1"` exist, not that the mandates actually run.
- **Impact:** Audited form, ignored substance. Security theater.
- **Required fix:** Tests must invoke the function and verify the effect, not search for text.

### F10 - CLI bug: `--project-path` not supported in the historical auditor
- **Status:** Historical. The old entrypoint no longer exists; the active auditor is `scripts/run_security_audit_12d.py`.
- **Symptom:** The historical CLI failed because it interpreted `--project-path` as a folder name.
- **Impact:** It was a real bug in the old CLI.
- **Required fix:** None in the active tree.

---

## FIX STATUS

| Failure | Priority | Status |
|-------|-----------|--------|
| F9 (assertIn theater) | CRITICAL | PENDING |
| F1 (D7 not implemented) | HIGH | HISTORICAL |
| F4 (textual try) | HIGH | HISTORICAL |
| F10 (CLI bug) | HIGH | HISTORICAL |
| F2 (SPEC.md section) | MEDIUM | PENDING |
| F5 (protocol tests vs project tests) | MEDIUM | PENDING |
| F6 (partial UI validation) | MEDIUM | PENDING |
| F3 (docstring count) | LOW | PENDING |
| F7 (stale evidence) | LOW | PENDING |
| F8 (dead files) | LOW | PENDING |

---

**Rule:** Before marking any failure as RESOLVED, a terminal log must demonstrate the fix.
**Anti-pattern:** Do not change the test so it passes - change the code so the test is right.
