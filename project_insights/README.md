# Project Insights — Transitional Learning Pipeline

**Scope:** Project-specific learnings, candidate patterns, operational insights.
**NOT part of Golden Standard pure knowledge.**

---

## Pipeline

```
raw/             (inputs, no analysis yet)
  ├── PI-001_learning.md
  ├── PI-009_debt_zero.md
  └── ...

analysis/        (where does this belong?)
  ├── PI-001_analysis.md  → "Tool recommendation, goes to @ref"
  ├── PI-009_analysis.md  → "Principle, promote to VC-XXX"
  └── ...

.archive/        (historical, superseded, decision log)
  ├── PI-003_archived_reason.md
  └── ...

PI-promotion.yaml (active transformations)
```

---

## States

| State | Meaning | Action |
|-------|---------|--------|
| **RAW** | Captured from project | Analyze: actionable? Falsifiable? Agnos? |
| **ANALYSIS** | Under review | Promote, Archive, or Extend |
| **PROMOTED** | Accepted to GS | Assigned to VC-XXX or Principle update |
| **ARCHIVED** | Not useful / superseded | Document reason, close |

---

## Canonical Ingestion (Required)

When promoting a PI to GS:

1. **Normalize** (remove project names, dates, team refs)
2. **Verify Falsifiability** (can we test/hook this?)
3. **Assign ID** (VC-XXX, TK-XXX, TV-XXX, or Principle level)
4. **Update GS/** (create/extend pattern file)
5. **Record in PI-promotion.yaml** (trace)
6. **Archive original PI** (keep for audit trail)

---

## Avoid

- Treating PI as "GS staging" (GS is pure, PI is ephemeral)
- Keeping dead PIs (archive or delete)
- Tool/vendor recommendations in PI (they're refs, not principles)
- Project-specific dates/names in final GS content

**GS is truth. PI is laboratory.**
