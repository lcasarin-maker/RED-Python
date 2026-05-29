# Rules Documentation

This document aggregates all **Cerberus** rules in a single, human‑readable reference.  The source files live in `cerberus/rules/*.yaml`.

---

## R‑PENDING‑ESCALATION
**ID:** `R-PENDING-ESCALATION`
**Description:** No debe existir ninguna tarea pendiente sin atender.
**Check:** `len(context.get('pending_tasks', [])) == 0`
**Enforcement:** `error_if_true`

*Purpose*: Guarantees that the watcher or audit never forgets a detected adjustment. The rule is evaluated after each audit run; if any pending task remains, the watcher will keep looping.

---

## R‑TEST‑COVERAGE
**ID:** `R-TEST-COVERAGE`
**Description:** Cada regla debe disponer al menos de un test unitario en `tests/rules/`.
**Check:** `all(rule.get('id') in [test_rule_id for test_rule_id in context.get('test_rule_ids', [])] for rule in context.get('rules', []))`
**Enforcement:** `error_if_false`

*Purpose*: Enforces Gemini‑13 style discipline that **no rule can be added without a corresponding test**.

---

### How to add a new rule
1. Create a new **YAML** file under `cerberus/rules/` with the fields `id`, `description`, `check`, `enforcement`.
2. Add a unit test under `tests/rules/` that registers the rule ID in the `test_rule_ids` list.
3. Run `pytest` – the rule will be validated automatically by the engine.

---

### Generating this document automatically
The script `tools/generate_rules_docs.py` iterates over every `*.yaml` file in `cerberus/rules/` and renders the markdown above.  It is invoked by the CI pipeline after any rule change.
