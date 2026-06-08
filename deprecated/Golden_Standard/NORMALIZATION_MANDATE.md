# NORMALIZATION MANDATE — Golden Standard v0.5
**Effective:** 2026-06-02 | **Authority:** CoderCerberus v0.5 (Anti-Slop S5)

---

## MANDATE STATEMENT

All entries in Golden Standard (Patterns + Principles) MUST follow **rigid normalization rules** for:

1. **Numbering** (sequential, no gaps, no mixed schemes)
2. **Naming** (descriptive-first, metaphors optional with explanation)
3. **Structure** (consistent file organization, no orphaned references)
4. **Cross-linking** (all references point to existing files)

**Enforcement:** S5 (Anti-Slop) gates; violations block GS commits.

---

## NORMALIZATION RULES

### Rule N1: Numbering MUST Be Sequential

**Principle:** Each catalog uses a single numeric sequence. No mixed prefixes.

| Catalog | Scheme | Requirement |
|---------|--------|-------------|
| **VC** (Coding) | VC-001 to VC-123 | Sequential; no gaps; single numeric sequence |
| **VT** (Testing) | VT-001 to VT-115 | Sequential; no gaps; single numeric sequence |
| **TK** (Tokenomics) | TK-001 to TK-042 | Sequential; **includes Foundation** (F01-F03), **excludes Positive** (P01-P11 → Principles) |
| **Principles** | Level-Module | LEVEL_N/M1 through LEVEL_N/M[count]; no gaps |

**Action:**
- ✅ VC: Already normalized (001-123 sequential)
- ✅ VT: Already normalized (001-115 sequential)
- ❌ TK: MUST normalize
  - TK-F01..F03 merge into TK-001..003 as "Critical Foundation Leaks"
  - TK-004..030 (current TK-001..027 shifted)
  - TK-031..042 reserved for new entries
  - TK-P01..P11 MOVE to Principles/LEVEL_5_TokenSaving/M3_Positive_Principles.md
- ❌ Principles: MUST add LEVEL_3 to hierarchy

---

### Rule N2: Names MUST Be Descriptive-First

**Principle:** Primary name describes the *problem + mechanism*. Metaphors are secondary.

**Format:**
```
VC-NNN: [Problem Type] — [Root Cause or Mechanism]

Example (Current):  VC-118: Zombie Compatibility Theater
Normalized:         VC-118: Replacement Shim Theater — Backward Compat Delusion
                    (Primary: Problem | Secondary: Metaphor)

Example (Current):  TK-F02: Poda Primitiva
Normalized:         TK-F01: Coarse-Grained Retrieval Fetching — Primitive Poda
                    (Primary: Technical Term | Secondary: Metaphor)
```

**Validation Checklist:**
- [ ] Name includes problem type? (e.g., "Compatibility", "Retrieval", "Memory")
- [ ] Name includes mechanism or root cause? (e.g., "Shim", "Coarse-Grained", "Monolithic")
- [ ] If metaphorical, metaphor follows colon after description?
- [ ] No vague words alone (e.g., "Slop", "Panic", "Theater" as standalone names)?

**Action:** Apply to all VC, VT, TK entries. Audit 5 samples per catalog before full pass.

---

### Rule N3: File Organization MUST Be Consistent

**Principle:** All INDEX.md files MUST map to corresponding category markdown files.

**Structure Requirement:**

```
Patterns/
├── Coding_Vices/
│   ├── INDEX.md                          ✅ (references 8 categories)
│   ├── I_Epistemology.md                 ❌ (STUB REQUIRED)
│   ├── II_Process_Scope.md               ❌ (STUB REQUIRED)
│   ├── III_State_Concurrency.md          ❌ (STUB REQUIRED)
│   ├── IV_Architecture.md                ❌ (STUB REQUIRED)
│   ├── V_Environment.md                  ❌ (STUB REQUIRED)
│   ├── VI_Governance.md                  ❌ (STUB REQUIRED)
│   ├── VII_Security.md                   ❌ (STUB REQUIRED)
│   ├── VIII_Replacement.md               ❌ (STUB REQUIRED)
│   └── APPENDICES.md                     ✅
├── Testing_Vices/
│   ├── INDEX.md                          ✅
│   ├── I_Logic_Oracles.md                ❌ (STUB REQUIRED)
│   ├── II_Simulation.md                  ❌ (STUB REQUIRED)
│   └── III_Flow_Discovery.md             ❌ (STUB REQUIRED)
├── Tokenomics/
│   ├── INDEX.md                          ✅ (UPDATE: remove F/P prefixes)
│   ├── I_Memory.md                       ❌ (STUB REQUIRED)
│   ├── II_Ingestion.md                   ❌ (STUB REQUIRED)
│   └── III_Output.md                     ❌ (STUB REQUIRED)
└── README.md                              ✅

Principles/
├── INDEX.md                              ✅
├── LEVEL_1_Integrity/
│   ├── INDEX.md                          ✅
│   ├── M1_Core_Principles.md             ❌ (STUB REQUIRED)
│   ├── M2_Usability.md                   ❌ (STUB REQUIRED)
│   ├── M3_Angry_Path.md                  ❌ (STUB REQUIRED)
│   └── M4_Errors_Secrets.md              ❌ (STUB REQUIRED)
├── LEVEL_2_Operation/
│   ├── INDEX.md                          ✅
│   ├── M1_Fundamentals.md                ❌ (STUB REQUIRED)
│   ├── M2_User_Scope.md                  ❌ (STUB REQUIRED)
│   ├── M3_Flows_State.md                 ❌ (STUB REQUIRED)
│   ├── M4_Orchestration_Tokenomics.md    ❌ (STUB REQUIRED)
│   └── M5_Audit_Git.md                   ❌ (STUB REQUIRED)
├── LEVEL_3_Validation/                   ❌ (DIRECTORY MISSING)
│   ├── INDEX.md                          ❌ (STUB REQUIRED)
│   ├── M1_Regression_Suite.md            ❌ (STUB REQUIRED)
│   ├── M2_Angry_Path_Testing.md          ❌ (STUB REQUIRED)
│   └── M3_Secrets_Audit.md               ❌ (STUB REQUIRED)
├── LEVEL_4_Guards/
│   ├── INDEX.md                          ✅
│   ├── M1_Prohibitions.md                ❌ (STUB REQUIRED)
│   ├── M2_Mandatory_Operatives.md        ❌ (STUB REQUIRED)
│   └── M3_Risk_Models.md                 ❌ (STUB REQUIRED)
├── LEVEL_5_TokenSaving/
│   ├── INDEX.md                          ✅
│   ├── M1_Diagnostics.md                 ❌ (STUB REQUIRED)
│   ├── M2_Leaks_Solutions.md             ❌ (STUB REQUIRED)
│   └── M3_Positive_Principles.md         ❌ (STUB REQUIRED; MIGRATE TK-P01..P11)
└── README.md                              ✅
```

**Stub Format (Minimum):**
```markdown
# [Category Name]

**Source:** `deprecated/...` (recovered) OR `TBD`
**Status:** PLACEHOLDER | **Date Created:** 2026-06-02

---

## Modules / Entries

(Content to be populated from deprecated files or inline index)

---

## Related Vices

See [related catalog].

---

## Next Steps

- [ ] Populate from deprecated/ sources
- [ ] Validate against DEDUP_LOG.yaml
- [ ] Cross-link to Principles/Patterns
```

---

### Rule N4: Cross-Links MUST Point to Existing Files

**Principle:** Every reference in GS must resolve. No dead links.

**Validation:**
```bash
# Find all references to category files
grep -r "I_Epistemology\|II_Process\|III_State" \
  Golden_Standard/Patterns/ \
  Golden_Standard/Principles/

# Action: Either create the file OR update the reference to point to INDEX.md
```

**Action:** Update all INDEX.md files to link to:
- Category files IF they exist
- INDEX.md placeholder IF category file does not yet exist
- Inline section headings IF no category file planned

---

## ENFORCEMENT (Binding Authority)

| Mandate | Enforcer | Trigger |
|---------|----------|---------|
| **N1: Sequencing** | S5 (Anti-Slop) | `run_security_audit_12d.py` checks numbering; blocks if gaps found |
| **N2: Naming** | S5 (Anti-Slop) | Manual audit; blocked if vague names detected (blacklist: "Slop", "Panic", "Theater" alone) |
| **N3: Structure** | S5 + CLAUDE.md | Pre-commit hook validates file existence; blocks if orphaned references |
| **N4: Cross-Links** | S5 + CI | Link checker (TBD) validates all GS references |

---

## IMPLEMENTATION SCHEDULE

### Phase 1: IMMEDIATE (This Session)
- [ ] Create this NORMALIZATION_MANDATE.md
- [ ] Create AUDIT_REPORT_2026-06-02.md
- [ ] Create stub files (32 total stubs)
- [ ] Normalize TK numbering in Tokenomics/INDEX.md
- [ ] Move TK-P01..P11 entries to Principles/LEVEL_5/M3_Positive_Principles.md

### Phase 2: SHORT-TERM (Next Session)
- [ ] Populate category files from deprecated/ using intelligent deduplication
- [ ] Update CORRELATION_MATRIX.md with correct file paths
- [ ] Validate all cross-links

### Phase 3: ONGOING
- [ ] Enforce N1-N4 in all future GS edits
- [ ] Add pre-commit hook to validate
- [ ] Audit quarterly

---

## RELATED MANDATES

- **S5 (Anti-Slop):** Zero warnings, test = failure, evidence-based
- **B9 (Root Cause):** Explain technical reason in natural language before code
- **B10 (Checkpointing):** PLAN.md with numbered steps before touching code
- **VC-118 (Zombie Compat):** Pure replacement strategy; no shims or wrappers

---

## APPROVAL & VERSION

| Field | Value |
|-------|-------|
| **Created By** | Claude Haiku (Agent Binding v0.5) |
| **Date** | 2026-06-02 |
| **Authority** | CoderCerberus v0.5, Mandate S5 (Anti-Slop) |
| **Binding Force** | MANDATORY for all GS edits (effective immediately) |
| **Next Review** | 2026-07-02 (monthly) |

**Status:** ✅ **ACTIVE**

---

## Quick Reference: What Violates This Mandate?

| Action | Status | Example |
|--------|--------|---------|
| Adding VC-124 after VC-123 exists | ✅ ALLOWED | "VC-124: New Finding" |
| Adding TK-F04 after TK-F03 | ❌ BLOCKED | Must use TK-028 |
| Naming "VC-NNN: Slop" | ❌ BLOCKED | Use "Stochastic Output Acceptance — Slop" |
| Creating file `I_Epistemology.md` | ✅ REQUIRED | Stub first, populate later |
| Linking to `/Patterns/I_Epistemology.md` | ✅ ALLOWED if file exists | Check before writing INDEX.md |
| Linking to missing file | ❌ BLOCKED | Update to INDEX.md or inline section |

