# S18: Token Optimization — Prevent 3 Critical Leaks

**Source:** PROTOCOL_SYSTEM.md (v0.5, universal)
**Authority:** LEVEL_5/M2 (Leaks_Solutions)
**Severity:** 🟡 MEDIUM

---

## Definition

Avoid three token leaks:

1. **Duplication:** Same data repeated across messages
2. **Re-reading:** Fetching same file 3+ times per session
3. **Untracked growth:** Large context with no compression strategy

---

## Why

Token budget is finite. Leaks = wasted cost + slower responses.

---

## Leak Patterns & Fixes

### Leak #1: Duplication
```
❌ Bad: Read file, summarize it, read it again
✅ Good: Read once, cache result, reference by path
```

### Leak #2: Re-reading
```
❌ Bad: grep finds 50 matches, Read all 50 files
✅ Good: Read 3-5 most relevant, check if answer is there first
```

### Leak #3: Context Growth
```
❌ Bad: 200-message conversation, no summary
✅ Good: Every 50 messages, compress prior context (keep task state only)
```

---

## Monitoring

- **Token counter:** At turn end, estimate cost
- **Compression point:** If >30 messages, consider summary
- **Reuse pattern:** "I just read X in message #5, skipping re-read"

---

## Related

- **S13:** Prompt Caching (API-level optimization)
- **LEVEL_5/M2:** Leaks_Solutions (token accounting)
