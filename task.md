# Task List
- [ ] Review and improve `scripts/core_utils.py` `get_centralized_version` handling.
- [ ] Implement robust `_extract_version` logic if not present, or adjust test expectations.
- [ ] Ensure all manifest files (`AGENT.md`, `PROTOCOL_SYSTEM.md`, `PROTOCOL_BEHAVIOR.md`, `.agent_state.json`) contain a version line parsable by `_extract_version`.
- [ ] Add missing version entries to manifests where absent.
- [ ] Update `tests/goldmine/tests/test_v55_rigor.py` if necessary to match version format.
- [ ] Run `pytest -q` and verify zero failures.
- [ ] Update `STATUS.md` (field 6) with next steps.
- [ ] Update `HISTORIAL.md` with detailed entry for this fixing session.
- [ ] Auto-commit changes if >3 files modified.
