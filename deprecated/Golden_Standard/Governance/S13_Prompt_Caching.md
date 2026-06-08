# S13: Prompt Caching — Token Optimization

**Source:** PROTOCOL_SYSTEM.md (v0.5, universal)
**Authority:** LEVEL_5/M1 (Diagnostics)
**Severity:** 🟡 MEDIUM

---

## Definition

Prompt caching is enabled automatically by the API for all claude-* models.

First message: ~1200 tokens (cache write). Second+ messages: ~120 tokens (cache reuse, −90% cost).

---

## Why

Cost and latency. Cached context enables longer conversations without token bloat.

---

## How to Optimize

1. **Put stable content first:** AGENT.md, SPEC.md, golden-standard rules
2. **Vary queries second:** User messages, current task
3. **API handles caching:** No manual action needed

---

## Monitoring

- **First message cost:** Higher (cache warmup)
- **Subsequent messages:** 120 tokens paid (90% savings)
- **Cache TTL:** 5 minutes default

---

## Related

- **LEVEL_5/M1:** Diagnostics (token accounting)
- **S18:** Token Optimization (leak prevention)
