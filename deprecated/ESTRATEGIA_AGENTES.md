# Agent Strategy - Tokensaver V1

## Daily flow

### If I need to THINK

-> Gemini CLI (fragments only)
-> Copy the answer to `STATUS.md`

### If I need to EXECUTE

-> Claude Code Desktop/Terminal
-> Use `PROMPTS_RAPIDOS_v3.md` Template 1 or 2

### If I need to REVIEW A DOCUMENT

-> Antigravity (fragments only, not full files)
-> Copy the result into analysis

### If I need FAST CODE and the task is already clear

-> Codex
-> Use `PROMPTS_RAPIDOS_v3.md` Codex template

---

## Prohibitions

- Never use Gemini CLI with full files.
- Never use Antigravity with an entire `AGENTS.md`.
- Never use Codex for thinking; it is for execution only.
- Never use Claude Code without `--lines` in view.

---

## Session checklist

- Read `STATUS.md`.
- Decide whether you need to think, execute, or review.
- Choose the right tool.
- Use the `PROMPTS_RAPIDOS_v3.md` template.
- Finish by updating `STATUS.md` with the result.

---

## Quick reference

| Need | Tool | Context | Template |
|---|---|---|---|
| Think about the next step | Gemini CLI | `STATUS.md` fragments | Manual |
| Execute a code change | Claude Code | `CLAUDE.md` + `STATUS.md` | Template 1 or 2 |
| Review a document | Antigravity | 2-3 paragraphs | Manual |
| Write code when the task is clear | Codex | `AGENTS.md` + `STATUS.md` | Codex template |

---

**Status:** Sprint 0 strategy completed
**Next step:** copy both files into the 6 main projects
