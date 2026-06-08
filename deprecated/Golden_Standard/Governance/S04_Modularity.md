# S4: Modularity — Schemas at Boundaries

**Source:** PROTOCOL_SYSTEM.md (v0.5, universal)
**Authority:** LEVEL_4/M2 (Mandatory Operatives)
**Severity:** 🔴 CRITICAL

---

## Definition

State crossing module boundaries MUST have schema validation (Pydantic, Zod, TypeScript interfaces).

No untyped data between modules. Every import/export is a boundary.

---

## Why

Type chaos at boundaries is how bugs escape modules. Schemas are the contract.

---

## Rules

1. **Every function taking external input** → validate with schema
2. **Every cross-module call** → typed return
3. **API responses** → Pydantic models, not `dict`
4. **Config objects** → Structured types, not raw JSON

---

## Enforcement

- **Type checker:** Blocks untyped imports
- **S3:** Bio-Containment (validation at I/O)

---

## Related

- **S3:** Security at boundaries
- **LEVEL_4/M2:** Mandatory Operatives
