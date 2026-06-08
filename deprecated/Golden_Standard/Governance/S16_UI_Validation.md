# S16: UI Validation — No Internal Testing of Usability

**Source:** GLOBAL_LEARNING.md (2026-05-20 Gemini incident)
**Authority:** LEVEL_3/M2 (Angry_Path_Testing)
**Severity:** 🔴 CRITICAL

---

## Definition

**NEVER validate UI/UX usability internally.** 

Agent cannot see browser, cannot see rendered output, cannot test visual correctness. Any internal validation is hallucination.

---

## Why

2026-05-20 incident: Gemini claimed "Human Test Passed" for HTML file in environment with no visualization capability (headless terminal).

Agents are blind. Ask humans.

---

## Rules

**PROHIBITED:**
- ❌ "UI looks good based on code"
- ❌ "I tested visually and it works"
- ❌ "Screenshot would show success"
- ❌ Internal simulation of browser behavior

**MANDATORY:**
- ✅ Ask human explicitly: "Open file [X] and confirm [Y] works"
- ✅ Wait for human verification
- ✅ Document human confirmation in HISTORIAL.md

---

## Pattern

```
Bad: "The UI should render correctly based on my CSS."
Good: "Can you open profile.html and confirm the form displays correctly?"
```

---

## Exceptions

None. Agents cannot validate UI.

---

## Related

- **S23:** Test Purity (no theater)
- **LEVEL_3/M2:** Angry Path Testing (external oracles)

