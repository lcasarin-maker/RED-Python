# Cerberus prompt execution order README

**Active protocol version:** v0.5 | **Updated:** 2026-06-06

## Scope of this package

`00 audit/` contains only live doctrine in three pillars:

1. What Cerberus is.
2. How to audit inward.
3. How to audit satellite projects outward.

## Live files

```text
00_CONSTITUCION_CERBERUS.md
01_AUDITORIA_LOCAL.md
05_AUDITORIA_EXTERIOR_CONTRACT_FIRST.md
```

## Load order

Load the files in this order:

```text
1. 00_CONSTITUCION_CERBERUS.md
2. 01_AUDITORIA_LOCAL.md
3. 05_AUDITORIA_EXTERIOR_CONTRACT_FIRST.md
```

## Logic

- `00_CONSTITUCION_CERBERUS.md` contains the permanent rules.
- `01_AUDITORIA_LOCAL.md` audits Cerberus itself.
- `05_AUDITORIA_EXTERIOR_CONTRACT_FIRST.md` defines the methodology for auditing
  outward-facing projects, starting from declared or inferred contract, human-like
  validation, GS mapping, and a remediation plan.

## What does not live here

- Golden Standard doctrine: GS is a separate repo.
- External repository mining: historical work was already digested in the GS Wiki.
- Run outputs: archived under `deprecated/audits_legacy/<date>/`.

## Operating rule

After loading the three files, run the audit without asking for confirmation between
phases, unless there is a real technical blocker.

If a predictable doubt exists before a long run, group it with the rest in one pass.

- If `00 audit/` topology changes, update `scripts/run_security_audit_12d.py`
  in the same change set.

## Clean-start rule

- Do not consult previous results unless the user asks for a historical comparison.
- Runs should write output outside this package.
