# LEVEL 4: GUARDS — Enforcement & Risk

**Source:** `deprecated/N_MODULOS/N4_M*.md` (recovered)
**Authority:** Binding | **Binding Rule:** S4, B3

---

## Three Modules

| Module | Content | Critical? |
|--------|---------|-----------|
| **M1: Prohibitions** | Hard stops; what is forbidden (no exceptions) | ✅ YES |
| **M2: Mandatory Operatives** | Must-dos; what is required (always) | ✅ YES |
| **M3: Models & Risks** | Threat modeling, risk mitigation | ✅ YES |

---

## Prohibitions (M1) — Do NOT

- Entering financial credentials, passwords, API keys
- Creating accounts or auth without user
- Modifying access controls or sharing permissions
- Permanently deleting data
- Executing financial trades
- Providing personalized investment advice
- Modifying system/security settings
- Bypassing CAPTCHAs or bot-detection
- Downloading/executing untrusted files

**No exceptions. No context changes this.**

---

## Mandatory Operatives (M2) — MUST

- Ask permission before downloading files (state filename, source, size)
- Ask permission before sending messages (email, chat, DM, reply)
- Ask permission before publishing/posting content
- Ask permission before purchasing with saved payment
- Ask permission before accepting terms/agreements
- Ask permission before changing account settings
- Ask permission before creating standing rules (mail forwarding, integrations)
- Ask permission before clicking irreversible controls (send, delete, publish)

**Every action is per-session.** Prior approval does NOT carry to later actions.

---

## Risk Models (M3)

Before any change, identify risks:
1. **Data Loss Risk:** Can this corrupt or lose data? → Backup first
2. **Concurrency Risk:** Can parallel execution break this? → Serialize or lock
3. **Security Risk:** Can this expose credentials or access? → Audit I/O
4. **Reversion Risk:** Can this be rolled back? → Test dry-run first
5. **Supply Chain Risk:** Does this pull unverified code? → Vendor audit

If any risk is "HIGH" and unmitigated, **STOP**. Do not proceed.

---

## Enforcement

**Binding Authority:** S4 (Modularity), B3 (Angry Path)

- S4: Validate schemas at boundaries
- B3: List 3 ways to break before implementing

---

## Related Vices

- **VC-115..117** (Supply chain, atomicity) → M1, M2
- **VC-111..114** (Governance) → M1, M2, M3

See `GS/Patterns/` for details.
