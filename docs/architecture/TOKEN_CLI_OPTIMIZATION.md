# Token CLI Optimization

This document captures the recommended token-optimized CLI workflow for autonomous work.

## Goals

- Reduce unnecessary input tokens.
- Reduce verbose output tokens.
- Keep the execution loop dense and actionable.
- Avoid re-reading large context blobs.

## Recommended flow

1. Read only the relevant file fragments.
2. Prefer command summaries over full dumps.
3. Cache stable context.
4. Compress long logs.
5. Re-run only the minimum checks needed to prove behavior.

## CLI rules

- Prefer short commands.
- Prefer structured output.
- Avoid large unfiltered logs unless they are required for evidence.
- Fail fast on missing context.

## Output discipline

- Summaries should be short and evidence-backed.
- Repeated context should be compacted.
- Avoid conversational filler.

## Operational pattern

| Situation | Recommended action |
|---|---|
| Need to orient | read the minimum file set |
| Need to verify | run the smallest proving command |
| Need evidence | capture only the relevant log slice |
| Need follow-up | reuse the previous checkpoint |

## Takeaway

The CLI should act like a precision instrument, not a transcript generator.
