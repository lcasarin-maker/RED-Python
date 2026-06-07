# RED-Python External Audit Contract

This document is the instruction for the external audit flow.
It is the source of truth for any review that tries to declare RED-Python externally audited.

## Hard rule

If any legacy control still exists in the active tree, it must be neutralized or moved to `deprecated/` before the repo can be considered externally audited.

## Phases

### Phase 0 - Repo profile and purge evidence

Required artifacts:

- `repo_profile.json`
- `legacy_controls_inventory.json`
- `privacy_check.md`
- `purge_plan.md`
- `phase_0_purge_result.md`

### Phase 1 - Contract declared or inferred

Required artifacts:

- `claims.json`
- `commands_detected.json`
- `CONTRATO_INFERIDO.md`
- `github_surface_check.md`

### Phase 2 - Operational reality

Required artifacts:

- `execution_log.txt`
- `ui_backend_trace.md`
- `human_flow_evidence.md`

### Phase 3 - Claims and evidence matrix

Required artifacts:

- `claim_matrix.csv`
- `evidence_index.json`

### Phase 4 - Mapping to the active contract

Required artifacts:

- `gs_mapping.json`
- `gs_gaps.md`

### Phase 5 - Adversarial checks

Required artifacts:

- `adversarial_findings.md`
- `theater_findings.md`

### Phase 6 - Verdict and remediation

Required artifacts:

- `verdict.md`
- `repair_plan.md`

## Output rule

The audit is not complete if the final verdict cannot show a real remediation plan and a clear path to closure.
