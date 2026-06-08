# System Mandates (S1-S23) — Authoritative Index

**Location:** GS/Governance/ (Single Source of Truth)
**Source Authority:** PROTOCOL_SYSTEM.md (universal), CLAUDE.md (subset for Claude)
**Scope:** Agent-agnostic system rules applicable to ALL agents

---

## Quick Reference

| Mandate | Title | Category | Severity | Page |
|---------|-------|----------|----------|------|
| **S1** | 6D Angry Path (Rigor Validation) | INTEGRITY | 🔴 CRITICAL | [S01_Rigor.md](S01_Rigor.md) |
| **S2** | Brain-First (SPEC.md Authority) | OPERATION | 🔴 CRITICAL | [S02_Brain_First.md](S02_Brain_First.md) |
| **S3** | Bio-Containment (Security/IO) | GUARDS | 🔴 CRITICAL | [S03_Bio_Containment.md](S03_Bio_Containment.md) |
| **S4** | Modularity (Schemas/State) | GUARDS | 🔴 CRITICAL | [S04_Modularity.md](S04_Modularity.md) |
| **S5** | Anti-Slop (Quality/Warnings) | INTEGRITY | 🔴 CRITICAL | [S05_Anti_Slop.md](S05_Anti_Slop.md) |
| **S6** | Large File Safety | GUARDS | 🟠 HIGH | [S06_Large_File_Safety.md](S06_Large_File_Safety.md) |
| **S7** | Anti-Shell (Edit Guards) | GUARDS | 🟠 HIGH | [S07_Anti_Shell.md](S07_Anti_Shell.md) |
| **S8** | Debt Tax (50-line limit) | GUARDS | 🟠 HIGH | [S08_Debt_Tax.md](S08_Debt_Tax.md) |
| **S9** | Structured Logging | INTEGRITY | 🟠 HIGH | [S09_Logging.md](S09_Logging.md) |
| **S10** | Code Lifecycle (deprecated/) | OPERATION | 🟡 MEDIUM | [S10_Code_Lifecycle.md](S10_Code_Lifecycle.md) |
| **S13** | Prompt Caching (Token Optimization) | TOKENS | 🟡 MEDIUM | [S13_Prompt_Caching.md](S13_Prompt_Caching.md) |
| **S14** | Zero-Trust (Double-Key Rule) | GUARDS | 🔴 CRITICAL | [S14_Zero_Trust.md](S14_Zero_Trust.md) |
| **S15** | Localization (Single Source) | OPERATION | 🔴 CRITICAL | [S15_Localization.md](S15_Localization.md) |
| **S16** | UI Validation (Ask Humans) | VALIDATION | 🔴 CRITICAL | [S16_UI_Validation.md](S16_UI_Validation.md) |
| **S17** | Version Sync (Anti-Drift) | OPERATION | 🟠 HIGH | [S17_Version_Sync.md](S17_Version_Sync.md) |
| **S18** | Token Optimization (3 Leaks) | TOKENS | 🟡 MEDIUM | [S18_Token_Optimization.md](S18_Token_Optimization.md) |
| **S19** | Pure Replacement (Anti-Zombie) | INTEGRITY | 🔴 CRITICAL | [S19_Pure_Replacement.md](S19_Pure_Replacement.md) |
| **S20** | Structured Error Logs | GUARDS | 🟠 HIGH | [S20_Error_Logs.md](S20_Error_Logs.md) |
| **S21** | Git Veto + Dual-Session | OPERATION | 🔴 CRITICAL | [S21_Git_Veto.md](S21_Git_Veto.md) |
| **S22** | Code Purity (No Stubs) | INTEGRITY | 🔴 CRITICAL | [S22_Code_Purity.md](S22_Code_Purity.md) |
| **S23** | Test Purity (No Theater) | INTEGRITY | 🔴 CRITICAL | [S23_Test_Purity.md](S23_Test_Purity.md) |

---

## Grouped by Severity

### 🔴 CRITICAL (13 mandates)

Must be enforced before any code change:
- **S1** (Rigor), **S2** (Brain-First), **S3** (Security), **S4** (Modularity), **S5** (Quality)
- **S9** (Logging), **S14** (Zero-Trust), **S15** (Localization), **S16** (UI Validation)
- **S19** (Pure Replacement), **S21** (Dual-Session), **S22** (Code Purity), **S23** (Test Purity)

### 🟠 HIGH (6 mandates)

Operational and safety rules:
- **S6** (Large File), **S7** (Anti-Shell), **S8** (Debt Tax)
- **S10** (Lifecycle), **S17** (Sync), **S20** (Error Logs)

### 🟡 MEDIUM (2 mandates)

Optimization rules (apply but not blockers):
- **S13** (Caching), **S18** (Token Optimization)

---

## Reading Order (by Impact)

**Session Start (CRITICAL):**
1. Read S2 (Brain-First) → Understand SPEC.md is authority
2. Read S21 (Git Veto) → Dual-session awareness
3. Read S1 (Rigor) → How to validate work

**Before Coding (CRITICAL):**
4. Read S3 (Security) → No hardcoded secrets
5. Read S4 (Modularity) → Schema/state rules
6. Read S19 (Pure Replacement) → Deletion + creation pattern
7. Read S22, S23 (Purity) → No stubs, no theater

**During Coding (HIGH):**
8. Read S7 (Anti-Shell) → Edit guards
9. Read S8 (Debt Tax) → 50-line max
10. Read S9 (Logging) → Structured logs

**Before Commit (CRITICAL):**
11. Read S14 (Zero-Trust) → Pre-destructive checklist
12. Read S5 (Anti-Slop) → Zero warnings

---

## Cross-Reference to Principles

Each S-mandate maps to a Principle level:

| Level | S-Mandates | Focus |
|-------|-----------|-------|
| **LEVEL_1_Integrity** | S1, S5, S9, S19, S22, S23 | Verification, rigor, purity |
| **LEVEL_2_Operation** | S2, S10, S17, S21 | Workflow, version control, dual-session |
| **LEVEL_3_Validation** | S1*, S23* | Testing gates |
| **LEVEL_4_Guards** | S3, S4, S6, S7, S8, S14, S20, S21 | Prohibitions, mandatory operatives |
| **LEVEL_5_TokenSaving** | S13, S18 | Optimization |

(*subset)

---

## Enforcement

**Who enforces?**
- **Pre-commit hook:** S1, S3, S5, S6, S7, S8, S14 (blocking)
- **run_security_audit_12d.py:** S1-S14, S19-S23 (gatekeeper)
- **Agent runtime:** S21 (double-key rule)
- **Manual discipline:** S10, S13, S17, S18 (developer responsibility)

---

## Scope: Agent-Agnostic

These mandates apply to:
- ✅ Claude (via CLAUDE.md binding)
- ✅ Gemini (via GEMINI.md binding)
- ✅ CodeX / ChatGPT (future adapters)
- ✅ Any future agent

Each agent binding (CLAUDE.md, GEMINI.md, etc.) implements these mandates in agent-specific ways, but the rules themselves are universal.

---

## Related Documents

- **Principles:** `GS/Principles/LEVEL_*/` (Why rules exist)
- **Patterns:** `GS/Patterns/` (What violations look like)
- **Agent Bindings:** `CLAUDE.md`, `GEMINI.md`, `.cursorrules` (How agents implement)
- **Protocol:** `PROTOCOL_SYSTEM.md` (Original authoritative source)

---

## Next: Populate Files

Each S-mandate file (S01_Rigor.md through S23_Test_Purity.md) will be created with:
- **Definición:** What the rule is
- **Razón:** Why it exists (principle reference)
- **Acción:** How to apply it
- **Enforcement:** Who checks it
- **Excepciones:** When it might not apply (or "none")

Estimated effort: ~2-3 hours to populate all 23 files from PROTOCOL_SYSTEM.md source.

