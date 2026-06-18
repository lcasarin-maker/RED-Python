# Agent Onboarding Rules

This guide is for Claude, Gemini, Codex, ChatGPT, or any new AI agent joining the project.

---

## Onboarding

### 1. Read first

Read these files first:

```text
AGENT.md                 <- base protocol for all agents
[AGENT_NAME].md          <- your agent-specific extension
AGENT_SAFETY.md          <- critical prohibitions
README.md                <- global router
STATUS.md                <- current state
```

- `AGENT.md`: protocol that applies to all agents.
- `[AGENT_NAME].md`: your specific file, such as `CLAUDE.md` or `GEMINI.md`.
  - It extends `AGENT.md` with agent-specific instructions.
  - Example: `CLAUDE.md` adds auto-initialization, model selection, and MCP filesystem usage.
  - Example: `GEMINI.md` adds incident awareness and dual-session risk handling.

### 2. Understand the structure

```text
NIVEL_1_INTEGRIDAD.md    <- code
NIVEL_2_OPERACION.md     <- operations
  └─ N2_MODULOS/N2_M5_*  <- rules #0-17
NIVEL_3_VALIDACION.md    <- validation checklist
NIVEL_4_GUARDIAS.md      <- prohibitions and obligations
NIVEL_5_TOKEN_SAVING.md  <- token optimization
```

### 3. Memorize the rules

```text
#0  Atomicity (previous state)
#1  Directed reading
#2  Caveman mode (do not derive)
#3  Memory = project files
#4  Trigger-based monitoring
#5  Brutal honesty
#6  Surgical edits
#7  User profile (Luis: lawyer, not programmer)
#8  Strict scope control
#9  Follow the plan, do not drift
#10 Verify before asking
#11 Decide and execute
#12 Exploration vs audit
#13 Auto-commit (>3 files or >50 lines)
#14 Reversion and backups
#15 Mandatory validation before CLEAR
#16 Lifecycle + cleanup
#17 Post-move validation
#18 Pre-commit safety hook (blocks destructive actions)
#19 Checkpoint state format (SHA256, reducer)
#20 Structured error reporting (JSON-parseable)
#21 Post-session retrospective (5 questions + JSON)
#22 Sources of Truth Index (SPEC vs POLICY)
```

### 4. Read AGENT_SAFETY.md

```text
PROHIBITED: git reset / revert / clean without directive
REQUIRED: Read HISTORIAL.md before destructive changes
REQUIRED: Document changes in HISTORIAL.md
```

### 5. Practice

- Open the project.
- Read `STATUS.md`.
- Identify field 3, "Working on".
- Read the last 3 entries in `HISTORIAL.md`.
- Done.

---

## Fail-safes

### Before any destructive git action

```bash
git reset / revert / clean / rm / checkout .

1. Read HISTORIAL.md (latest changes)
2. Run git status
3. Ask the user: "Am I going to [ACTION]? Confirmed?"
4. Document it in HISTORIAL.md afterwards
```

### If another agent already made changes

```text
[1] Read HISTORIAL.md first
[2] Review the last 3 sessions
[3] If there are recent changes: integrate, do not revert
[4] Example: Gemini did v2.8.6, Claude did Phase 5
             -> Solution: v2.9.0 (preserve both)
             -> Do not: git reset (would lose Phase 5)
```

### Dual-session conflicts

```text
If two agents work in parallel:
  [A] Claude: Phase 5 (README, CONTRIBUTING, .secrets)
  [B] Gemini: v2.8.6 (modules, rules #0-17)

  BAD: Gemini runs git reset -> loses Phase 5
  GOOD: Claude preserves v2.8.6 + restores Phase 5 -> v2.9.0
```

---

## Session template

```markdown
# My First Session in Coder Cerberus V0.1

## Pre-work checklist
- [ ] I read AGENT.md
- [ ] I read [MY_FILE].md (CLAUDE.md / GEMINI.md / my extension)
- [ ] I read AGENT_SAFETY.md
- [ ] I read STATUS.md
- [ ] I read HISTORIAL.md (last 3 sessions)
- [ ] git status (clean or what changed?)
- [ ] I understand rules #0, #13, #15, #17

## My task
[Describe here]

## Plan
1. [Step 1]
2. [Step 2]
3. Validate
4. Compact if >40 messages

## If I break something
1. git log --oneline
2. Document in HISTORIAL.md
3. Inform the user immediately
4. Do not run git reset without confirmation
```

---

## Golden rules

1. Never run git reset/revert without explicit directive.
2. Always read HISTORIAL.md before destructive actions.
3. Always document what you did in HISTORIAL.md.
4. Always validate before CLEAR.
5. Always respect scope.
6. Never assume.
7. Always auto-commit if >3 files.
8. Always test after a move.

---

## Need help?

- Easy question? -> Rule #10
- Big change? -> Rule #11 + Rule #15
- Security doubt? -> Read AGENT_SAFETY.md
- Historical context? -> HISTORIAL.md
- Current state? -> STATUS.md

---

## You are ready when...

- [ ] You understand rules #0-17
- [ ] You know why AGENT_SAFETY.md exists
- [ ] You read HISTORIAL.md before destructive actions
- [ ] You document changes automatically
- [ ] You validate before CLEAR
- [ ] You use COMPACT when context exceeds 40 messages

Welcome to the protocol. Do not break anything.
