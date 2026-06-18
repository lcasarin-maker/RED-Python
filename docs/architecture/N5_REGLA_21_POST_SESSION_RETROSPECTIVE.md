# RULE #21 - Post-session retrospective checklist

**Inspiration:** [timothyjrainwater-lab/multi-agent-coordination-framework](https://github.com/timothyjrainwater-lab/multi-agent-coordination-framework) - "Post-Debrief Retrospective"
**Adoption:** 2026-05-17 Phase 9 (enforcement tier 3 - test-enforced)

---

## What it is

Make a mandatory retrospective at the end of every session. Before context is closed
(COMPACT/CLEAR), the agent answers 5 structured questions. Output must be JSON-parseable
and embedded in `HISTORIAL.md`.

## Mandatory retrospective template

Each session must include a section like this in `HISTORIAL.md`:

```markdown
## SESSION [DATE] - [AGENT_NAME]

### RETROSPECTIVE

**JSON:**
```json
{
  "session_date": "2026-05-17T20:15:33Z",
  "agent": "Claude",
  "project": "Protocolo Agentes",
  "answers": {
    "q1_learning": "What did you learn that was not obvious?",
    "q2_violation": "What rule did you violate, if any? Or NONE.",
    "q3_next_agent": "What should the next agent know?",
    "q4_protocol_gap": "What is missing in AGENT_SAFETY.md or AGENT_ONBOARDING.md?",
    "q5_token_efficiency": {
      "efficient": true,
      "estimate_tokens": 50000,
      "actual_tokens": 45000,
      "note": "Brief reason why it was or was not efficient"
    }
  }
}
```

### The 5 required questions

**Q1: What did you learn that was not obvious?**
- 1-3 sentences.
- Scope: protocol lessons, patterns, gaps.

**Q2: What rule did you violate, if any?**
- Answer: `RULE #X - description` or `NONE`.
- If there was a violation, explain how it was detected and resolved.

**Q3: What should the next agent know?**
- Context that is not already in `STATUS.md` field 6.
- Include subtle state, conflicts, shortcuts, landmines, and human preferences.

**Q4: What is missing in AGENT_SAFETY.md or AGENT_ONBOARDING.md?**
- The missing instruction or guardrail that would have prevented confusion.

**Q5: Was the token budget efficient?**
- Answer:

```json
{
  "efficient": true,
  "estimate_tokens": 50000,
  "actual_tokens": 48500,
  "note": "COMPACT executed at message 45. Summary took 2K tokens. Overall efficiency 97%."
}
```

---

## HISTORIAL.md integration

After each task, before COMPACT/CLEAR, the agent must append:

```markdown
## SESSION 2026-05-17 PART 7 - PHASE 1 IMPLEMENTATION

**Task:** Create RULE #21 + RULE #22

**Changes:**
- N5_REGLA_21_POST_SESSION_RETROSPECTIVE.md (created)
- SOURCES_OF_TRUTH.md (created)
- AGENT.md (updated)
- tests/test_regla_21_retrospective.py (created)

**Documentation:** Changes in CLAUDE.md, AGENT_ONBOARDING.md linked

**Status:** COMPLETE

### RETROSPECTIVE

**JSON:**
```json
{
  "session_date": "2026-05-17T20:15:33Z",
  "agent": "Claude",
  "project": "Protocolo Agentes",
  "answers": {
    "q1_learning": "RULE #21 adds documentation overhead but detects gaps earlier.",
    "q2_violation": "NONE",
    "q3_next_agent": "Update RULE #22 whenever a new rule appears or authority changes.",
    "q4_protocol_gap": "AGENT_ONBOARDING.md does not mention JSON-parseable retrospectives.",
    "q5_token_efficiency": {
      "efficient": true,
      "estimate_tokens": 40000,
      "actual_tokens": 38500,
      "note": "No COMPACT was needed."
    }
  }
}
```
```

---

## Git hook enforcement

The pre-push hook must verify that the latest session in `HISTORIAL.md` includes a
`RETROSPECTIVE` section with valid JSON and the five required answers.

---

## Spirit of Rule #21

- Mandatory.
- Structured.
- Machine-readable.
- Actionable.
- Small overhead.
