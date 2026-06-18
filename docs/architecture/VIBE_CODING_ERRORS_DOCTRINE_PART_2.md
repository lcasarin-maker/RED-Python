# Vibe Coding Errors Doctrine - Part 2

This continuation focuses on the operational ways vibe coding turns into durable debt.

## 1. Fluff and redundancy

Repeated conversational padding wastes context and weakens the instructions. Shorter, denser,
and more structured prompts outperform long, polite, vague ones.

## 2. Memory and state

If state is not explicit, the model will re-learn it repeatedly. Persistent files, checkpoints,
and strict session summaries reduce waste and drift.

## 3. Cache cliffs

Long pauses between steps destroy cached context and make the next step expensive. The workflow
should minimize idle gaps and maximize state reuse.

## 4. Architecture over prose

Prompt engineering helps, but architecture is the main savings lever. Filtering, indexing,
compression, and strict routing reduce token waste more than decorative instruction text.

## 5. Final recommendations

- Keep state external and explicit.
- Keep instructions short and enforced.
- Keep logs compressed.
- Keep tests real.
- Keep the system honest.
