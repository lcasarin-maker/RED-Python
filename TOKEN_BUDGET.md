# Token Budget Framework (CoderCerberus V0.02)

## Session Token Allocation

Every session operates within a structured budget to prevent silent context collapse:

```
Total Context Window: 200,000 tokens
├─ Base Context (immutable): 50,000 tokens
│  ├─ System prompt: ~10K
│  ├─ SPEC.md + AGENT.md + manifests: ~20K
│  ├─ Plan file (if applicable): ~10K
│  └─ Memory files: ~10K
│
├─ Working Space: 100,000 tokens
│  └─ Task implementation, tool calls, responses
│
└─ Headroom (safety margin): 20,000 tokens
   └─ Prevents silent collapse; compression checkpoint at 130K used
```

## Headroom Management Rules

| Tokens Remaining | Status | Action |
|---|---|---|
| > 20K | SAFE | Continue working normally |
| 20-30K | WARNING | Show warning; compress before next major operation |
| < 20K | HARD STOP | Stop immediately; compress + new session required |

## Token Tracking

### Per-Session Baseline
- Log starting usage: `echo "session_start_tokens: $(jq '.token_usage' .agent_state.json)" >> .protocol/logs/token_history.log`
- Track checkpoint: Every 10 commits or 30K tokens, log current usage
- Calculate used: `tokens_used = current_tokens - session_start_tokens`
- Calculate remaining: `headroom = 20000 - (total_tokens - base_context - working_used)`

### .agent_state.json Fields (Phase 0 Update)

```json
{
  "session_token_budget": {
    "session_start_tokens": 0,
    "base_context_tokens": 50000,
    "tokens_used_so_far": 0,
    "tokens_remaining_headroom": 20000,
    "compressions_this_session": [],
    "reversals_and_costs": [],
    "checkpoints": []
  }
}
```

## Compression Procedure

**When to trigger:** `tokens_used > 130000` (80% of 100K working space)

**Steps:**
1. Call `python scripts/compress_memory_context.py`
   - Output: JSON log of what was compressed (returned to stdout + logged)
   - Compression rate: estimate tokens saved

2. Update `.agent_state.json`:
   ```json
   {
     "compressions_this_session": [
       {
         "timestamp": "2026-05-20T14:35:00Z",
         "tokens_before": 145000,
         "tokens_after": 95000,
         "tokens_saved": 50000,
         "method": "aggressive"
       }
     ]
   }
   ```

3. Continue or escalate:
   - If tokens_after < 100K: continue working
   - If tokens_after >= 100K: escalate to user ("Context still high after compression; recommend new session")

## Reversal Cost Accounting

Every `git revert` logs its token cost:

```json
{
  "reversals_and_costs": [
    {
      "timestamp": "2026-05-20T14:20:00Z",
      "commit_reverted": "abc123def456",
      "reason": "test_failure|logic_error|encoding_issue",
      "estimated_tokens_wasted": 5000,
      "cumulative_waste_this_session": 15000
    }
  ]
}
```

**Escalation Trigger:** If `cumulative_waste > 30000` OR `reversal_count > 2` in same task:
- Log escalation to HISTORIAL.md with analysis
- Ask user: "3+ reversals detected. Tokens wasted: 30K+. Options: A) continue, B) Luis reviews architecture, C) different approach"

## Compression Command Reference

```bash
# Check current token usage
jq '.session_token_budget' .agent_state.json

# Run compression
python scripts/compress_memory_context.py

# View token history (export_retrospective.py writes session exports)
python scripts/export_retrospective.py --list 2>nul || echo "No export history yet"

# Estimate remaining
jq '.session_token_budget.tokens_remaining_headroom' .agent_state.json
```

## Why This Matters (B1: Assume Failure)

Silent context collapse causes:
1. Hallucinations (model doesn't know it ran out of space)
2. Truncated code (large files cut off mid-way)
3. Forgotten requirements (prior context evicted)
4. Repeated work (token exhaustion forces new session, restart from scratch)

This framework makes that **impossible** by making token accounting **visible and enforced**.

---

**Version:** v0.02 | **Effective:** 2026-05-20 | **Integration:** Phase 1 (protocol_cli.py will track these)
