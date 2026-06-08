# S17: Version Sync — Anti-Drift Mandate

**Source:** PROTOCOL_SYSTEM.md (v0.5, universal)
**Authority:** LEVEL_2/M1 (Fundamentals)
**Severity:** 🟠 HIGH

---

## Definition

**Verify `.version` in .agent_state.json matches current CoderCerberus version (v0.5).**

Drift between agent state and GS rules = unverifiable execution.

---

## Why

Agent assumptions must match GS authority. Version mismatch means outdated rules being enforced.

---

## Rules

1. **Session start:** Check `.agent_state.json` version
2. **If mismatch:** Stop, re-read GS/Governance/
3. **Update state:** Set `.version = "v0.5"`
4. **Proceed:** Aligned with current rules

---

## Checking

```bash
cat .agent_state.json | grep version
# Should show: "version": "v0.5"
```

---

## Enforcement

- **Manual discipline:** Startup ritual (part of S21 pre-check)
- **S2:** Brain-First (SPEC.md version matches)

---

## Related

- **S2:** Brain-First (SPEC.md authority)
- **LEVEL_2/M1:** Fundamentals (startup ritual)
