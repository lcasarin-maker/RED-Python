---
id: TASK-001
title: Rename Spanish identifiers and file names to English
status: backlog
priority: medium
created: 2026-07-31
---

## Context

Cerberus governance requires descriptive English names for files and
identifiers (SP-011). This project's application code predates that
rule. The rename is deliberately gradual: adoption does not touch
application code, because a mass rename and a governance change in the
same commit make both impossible to review.

## Definition of done

- File names and Python identifiers outside third-party code are
  descriptive English following PEP 8.
- The project's own test suite passes after each rename batch.
- No stale references remain (grep for the old names).
