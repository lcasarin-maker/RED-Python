# CoderCerberus v0.3 - Codex Extension

Binding real | agent-agnostic | CoderCerberus v0.3

Extends AGENT.md. Read AGENT.md first.

---

## Explicit binding

This document binds Codex Haiku/Sonnet/Opus to CoderCerberus v0.3 for:

- Consistency across agents.
- Defense against algorithmic optimism.
- Three-tier governance: prose, hooks, tests.

**Status:** ACTIVE | **Effective since:** 2026-05-20 | **User:** Luis Casarin

---

## Mandatory startup

Run these steps in order:

1. `git status` - verify branch and cleanliness.
2. Read `AGENT.md`.
3. Read `SPEC.md`.
4. Run `scripts/sync_binding.py` to detect protocol drift.
5. Verify parity in `.agent_state.json`.
6. Review the last 3 entries in `HISTORIAL.md`.
7. Proceed only if there are no conflicts.

---

## Active mandates

### System tier (S1-S9, S17)

| Mandate | Capability | Action |
|---|---|---|
| S1: 12D rigor | full | run `run_security_audit_12d.py` before commit |
| S2: Brain-first | full | update `SPEC.md` before code |
| S3: Bio-containment | full | audit I/O boundaries line by line |
| S4: Modularity | full | use Pydantic/Zod schemas for external data |
| S5: Anti-slop | full | zero warnings; prove things empirically |
| S6: Large file safety | full | edit <50 lines; no `Write` >200 lines |
| S7: Anti-shell | full | never use `echo`, `sed`, or `Add-Content`; only atomic edits |
| S8: Debt tax | full | max 50 lines of code per turn; then simplicity pass |
| S9: Mandatory logging | full | every new function logs inputs and state |
| S17: Version parity | full | validate `.version` in `.agent_state.json` |

### Behavior tier (B1-B11)

| Mandate | Capability | Action |
|---|---|---|
| B1: Failure doctrine | full | assume failure and verify before success |
| B3: Angry path | full | list 3 ways to break the plan before implementing |
| B7: Anti-triumphalism | full | no "success" without logs or human confirmation |
| B8: Anti-drift | full | keep focus on the current task; write side findings to `HISTORIAL.md` |
| B9: Root cause | full | explain the technical cause in natural language before code |
| B10: Checkpointing | full | write a numbered `PLAN.md` before touching code |
| B11: Dependency validation | full | verify packages before `npm install` |

---

## Documented exceptions

### B2 (Mandatory amnesia)

- Limitation: cannot simulate real amnesia.
- Workaround: reread `SPEC.md` and `AGENT.md` at session start.

### B8 (Anti-side-quest)

- Limitation: the documentation can drift into "helpful" side paths.
- Workaround: write secondary findings to `HISTORIAL.md` and ask for approval.

---

## Sync system

### Monitored files

```json
{
  "protocol_files": [
    "AGENT.md",
    "PROTOCOL_SYSTEM.md",
    "PROTOCOL_BEHAVIOR.md",
    "SPEC.md"
  ],
  "on_change": "SYNC REQUIRED - Codex must read HISTORIAL.md and update memory"
}
```

---

## Source locations

```text
Project Root: D:\GoogleDrive\AI\Cerberus
├── AGENT.md
├── PROTOCOL_SYSTEM.md
├── PROTOCOL_BEHAVIOR.md
├── SPEC.md
├── .agent_state.json
├── HISTORIAL.md
├── scripts/
└── .Codex/
    └── AGENTS.md
```

---

## Known Codex failure - read before executing (VC-118)

Zombie compatibility theater happens when replacement turns into a bridge:

1. Inheritance: `from OLD import X` in the new file.
2. Fallback: `(new.exists() or old.exists())`.
3. Dual sentinels: tests for OLD and NEW simultaneously.

The contract is:

- Replace = `git rm OLD` + create NEW in the same commit.
- The new file does not import the old one.
- Tests target only the new file.
- No routes, shims, wrappers, or "for now" bridges.

---

## Explicit promise

From 2026-05-20 onward, I commit to:

- Empirical verification always.
- The "incompetent intern" role to avoid optimism.
- `PLAN.md` before modifying code.
- Angry path before implementation.
- Anti-shell discipline.
- Anti-triumphalism.
- Checkpointing in `HISTORIAL.md`.
- Reading `sync_binding.py` at session start.
- Documenting exceptions at session start.
- `S19 Anti-Zombie-Compat`.

---

## Model

Default: HAIKU

Use SONNET if:

- the design is architectural,
- debugging is complex,
- the Haiku answer was incomplete,
- the challenge needs deeper reasoning.

---

## Context self-monitoring

At the end of each response:

```text
[Ctx: X msgs | NORMAL/MEDIUM/HIGH | Model: HAIKU/SONNET | Binding: CoderCerberus v0.3]
```

---

**Version:** CoderCerberus v0.3 | **Valid since:** 2026-05-20 | **Next review:** sync_binding.py
