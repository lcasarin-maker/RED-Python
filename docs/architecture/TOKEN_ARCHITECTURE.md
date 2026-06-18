# Token Architecture

This document describes how Cerberus reduces token waste in autonomous AI workflows.

## 1. Problem statement

Large-language-model workflows waste most of their tokens in orientation, repeated reads,
and verbose summaries rather than productive work. Token management is therefore an
operational constraint, not an aesthetic preference.

## 2. Main sources of waste

- Blind exploration of repositories.
- Re-reading the same files in the same session.
- Decorative prompt language.
- Overly long examples.
- Unbounded output verbosity.

## 3. Cost of the cache cliff

Idle periods invalidate the cache and turn a low-cost session into an expensive restart.
Long pauses between steps are therefore expensive.

## 4. Optimization strategy

| Level | Techniques | Input impact | Output impact | Risk |
|---|---|---|---|---|
| Prompt | strict XML, context delimiters, chain-of-density summaries, caveman mode | 40-60% | 80-90% | low |
| Architecture | model cascading, command proxies, AST indexing, explicit prompt caching | 75-95% | 30-50% | moderate |

## 5. Architectural recommendation

The preferred path is a hybrid architecture that prioritizes command filtering and smart
context loading. The biggest gains come from reducing raw inputs such as build logs and
full-file reads.

## 6. Proxies and filters

- Use command proxies to compress noisy shell output.
- Use AST-backed readers instead of full linear file loading.
- Keep the context dense and stable.

## 7. Practical guidance

- Keep root instructions short.
- Read only what is needed.
- Prefer summarized evidence over raw dumps when possible.
- Reuse cached context when it is still valid.

---

## Summary

Tokenomics is a system design problem. The cheapest token is the token never read.
