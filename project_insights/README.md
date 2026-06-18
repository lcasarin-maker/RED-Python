# Project Insights — Transitional Learning Pipeline

**Scope:** project-specific learnings, candidate patterns, operational insights.
**Not part of Golden Standard pure knowledge.**

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
| **RAW** | Captured from project | Analyze: actionable? falsifiable? reusable? |
| **ANALYSIS** | Under review | Promote, archive, or keep local |
| **PROMOTED** | Accepted upstream | Assign to CC doctrine or GS |
| **ARCHIVED** | Not useful / superseded | Document reason and close |

---

## Canonical Ingestion (Required)

When promoting a PI to GS:

1. **Normalize** the statement.
2. **Verify falsifiability**.
3. **Assign an upstream target**.
4. **Update the receiving doctrine**.
5. **Record the promotion in `PI-promotion.yaml`**.
6. **Archive the original PI**.

---

## Avoid

- Treating PI as "GS staging" when the pattern is still local.
- Keeping dead PIs (archive or delete)
- Tool/vendor recommendations in PI (they're refs, not principles)
- Project-specific dates/names in final GS content

**GS is truth. PI is laboratory. CC is the filter.**
