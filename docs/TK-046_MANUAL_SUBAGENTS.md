# TK-046: Sub-agents - Why It Is NOT Automatable

**Architecture decision:** Sub-agents require strategic judgment and cannot be automated.

---

## The Problem

**Scenario:** The user needs deep exploration that consumes 50K+ tokens.

❌ **Option 1: Automate (DOES NOT WORK)**
```
IF large_exploration THEN spawn_subagent
```
**Problem:** When is it "large"? Always delegate? Never?
- Sub-agent overhead: initialization, context, synthesis
- Sometimes the exploration yields insights the user needs to see
- The decision is **contextual, not metric-based**

✅ **Option 2: Manual (CORRECT)**
```
User: "Research X"
Claude: "This is a large investigation. Do you want a sub-agent?"
User: YES -> spawn | NO -> direct exploration
```

---

## Why It Cannot Be Automated

### 1. **Strategic Decision, Not Tactical**

| Aspect | Automatable | Not automatable |
|---|---|---|
| Thinking mode | ✅ (technical) | — |
| Model routing | ✅ (complexity) | — |
| Tool truncation | ✅ (bytes) | — |
| **Sub-agents** | ❌ | ✅ (context) |

Sub-agents are not a "token-saving technique" - they are a **workflow decision**.

### 2. **Context Is Opaque**

Questions only the user can answer:
- Do you need to see the research process?
- Is a final summary enough?
- Could the exploration generate insights?
- Is it critical for the decision?

**Example 1:**
```
User: "Check whether our API is secure"
Claude (automatic): spawn subagent
Problem: The user wanted to see the security findings, not just "Result: secure"
```

**Example 2:**
```
User: "Give me a summary of ML trends"
Claude (automatic): direct exploration
Problem: 60K tokens spent when a sub-agent would have been enough
```

### 3. **Overhead vs Savings**

```
Sub-agent COSTS:
- Context initialization
- Result synthesis
- Context switching

Sub-agent BENEFITS:
- Token isolation (does not drag the main chat)
- Possible parallelization
- Context cleanup

The balance is CONTEXTUAL, not automatic.
```

### 4. **Conflict with Autonomy**

If we automate:
```
Claude ALWAYS delegates large explorations
→ User loses visibility
→ We lose opportunities for insights
→ Claude acts without permission
```

This violates:
- **B8: Anti-deriva** (secondary decisions without approval)
- **B1: Failure doctrine** (assuming it will work without validating)

---

## When to Use Sub-Agents (Manual)

✅ **USE a sub-agent if:**
- Exploration > 30K estimated tokens
- The user only needs the final summary
- The research runs in parallel to the main task
- You need to isolate context for parallelization

❌ **DO NOT USE if:**
- The user explicitly said "research with me"
- The exploration could reveal plan changes
- < 10K estimated tokens (overhead is not worth it)
- The decision depends on how the result is reached

---

## Implementation: Manual Suggestion

**Best practice: Claude suggests, user decides**

```python
# Pseudo-code
if exploration_size > 30000:
    print("⚠️ This is a large investigation (30K+ tokens).")
    print("Options:")
    print("  1. Use sub-agent (final summary)")
    print("  2. Direct exploration (I see the full process)")
    # User chooses
```

**No automatic code - clear UX instead.**

---

## Conclusion

| Phase | TK | Automation | Reason |
|---|---|---|---|
| 1 | 044-050 | ✅ 5/5 | Tactical (tokens, models, output) |
| 2 | 048 | ✅ 1/1 | Detect plan (clear pattern) |
| **Manual** | **046** | ❌ 0/1 | **Strategic decision (context)** |

**TK-046 is CLOSED as MANUAL.**

It is not missing implementation - it is the correct architectural decision.

---

**Documented:** 2026-06-02 | **Status:** MANUAL (by design)
