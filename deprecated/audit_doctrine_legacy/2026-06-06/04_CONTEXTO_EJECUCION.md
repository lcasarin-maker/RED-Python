# 04 - Execution context

## 0. Load order

Always load these files in this order:

1. `00_CONSTITUCION_CERBERUS.md`
2. `01_AUDITORIA_LOCAL.md`
3. `02_AUDITORIA_REPOSITORIOS.md`
4. `03_EVOLUCION_GOLDEN_STANDARD.md`
5. `04_CONTEXTO_EJECUCION.md`

After loading them, run the full audit without asking for confirmation between phases,
unless there is a real technical blocker.

## 0B. Pre-S5 contract

Before opening Sprint 5, confirm and document:

1. Active debt is zero for the live tree.
2. `00 audit/results/` is historical reference only.
3. All predictable questions are grouped into a single pass before a long run.
4. The root is clean at the end of the audit.

## 0C. Current live closure

For this project version (v0.5, 2026-06-05):

1. `docs/sprint3_4_triage_giants.md` is the active sprint triage document.
2. `implementation_plan.md` was retired from the root.
3. `00 audit/results/` remains historical reference only.
4. The live verifier is still `python scripts/run_security_audit_12d.py`.
5. Cerberus and the Golden Standard are separate repositories.
6. Active scripts: 60+.
7. The local and GS phases must remain separate.

---

## 1. Target project

```text
D:\AI\Cerberus
```

> The previous path `D:\GoogleDrive\AI\Cerberus` is obsolete.

---

## 2. Golden Standard target

```text
D:\AI\VibeCoding_GoldenStandard\golden_standard.yaml   <- executable rules
D:\AI\VibeCoding_GoldenStandard\Wiki\                  <- navigable documentation
  ├── Domains\D1.md ... D12.md
  ├── Vices\TK-*.md / VC-*.md
  └── Project_Insights\PI-*.md
```

---

## 3. Specific objectives of this run

1. Run adversarial audit of the local project.
2. Audit external GitHub repositories.
3. Ensure everything in Golden Standard is properly regulated and executable.
4. Detect technical debt.
5. Detect architectural debt.
6. Verify Set and Forget autonomy.
7. Validate whether the current implementation is the best fit.
8. Evaluate whether components should be JSON, YAML, SQLite, index, skill, agent, library, pipeline, or declarative rule.
9. Propose executable integration without contaminating Golden Standard.
10. Decide `APPROVED` or `REJECTED`.
11. Refresh the project state and leave the exact path for the next sprint.

---

## 4. Intervention policy

- Do not ask for confirmation between phases.
- Group predictable questions before a long run.
- Execute all phases in sequence unless there is a real technical blocker.
- If a blocker appears: record it, explain its impact, continue the unblocked phases.

---

## 5. Target repositories

See the repository list in the original file.

---

## 6. Final report

The final report must include:

- Executive risk translation.
- Clean code map and topology.
- Cross-check against Golden Standard.
- 12D audit.
- Architectural adequacy audit.
- External repository audit.
- Proposed Golden Standard blocks.
- Executable integration strategy.
- Corrections applied.
- Final governance status.
- Deferred backlog.

---

## 7. Final criterion

The agent must deliver a complete result.
Do not split the audit unless there is a material technical blocker.
Do not ask for confirmation between phases.
Do not declare `APPROVED` if there is even one critical violation or material architectural debt.
