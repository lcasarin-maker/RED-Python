# RULE #30 - Data validation at boundaries

**Origin:** `DEEPDIVE_DEPRECATED_FINDINGS.md` (Tier 2 - important)
**Adoption:** 2026-05-17 Phase 9 (enforcement tier 1 - prose-enforced)
**Enforcement:** RULE #30 [PROSE-ONLY] — la aplica una persona al revisar, no hay
codigo que la compruebe, y decirlo es mas honesto que dejarlo implicito.

---

## What it is

Validate **all** inputs at system boundaries (user input, API calls, file uploads,
external data sources). Reject malformed data at the boundary, not inside the code.

## Principles

### 1. Boundary = system boundary

Validate here:

- User input (forms, CLI args, API requests)
- File uploads (mimetype, size, content inspection)
- External API responses (schema mismatch, unexpected types)
- Environment variables (missing required values, invalid values)
- Database queries (parameterized, no raw SQL)

Do not validate here:

- Between functions in the same module
- Values that already passed boundary validation
- Internal in-memory state with no external source

### 2. Validation must be exhaustive

```python
# Wrong: assumes email is already well-formed
email = request.form.get("email")
user = User.create(email)
```

```python
# Correct: validate before use
email = request.form.get("email", "").strip()
if not email or "@" not in email or len(email) > 255:
    raise ValueError(f"Invalid email: {email}")
user = User.create(email)
```

### 3. Validation must reject, not coerce

```python
# Wrong: tries to "fix" invalid input silently
status = request.args.get("status", "PENDING")
if status not in ["PENDING", "DONE"]:
    status = "PENDING"
```

```python
# Correct: reject invalid input
status = request.args.get("status")
if status not in ["PENDING", "DONE"]:
    raise ValueError(f"Invalid status: {status}. Must be PENDING or DONE.")
```

---

## What to validate

### User input

- Present (not None, not empty)
- Correct type
- Length
- Format
- Allowed values
- Encoding

### File uploads

- MIME type
- Size
- Content
- Sanitized filename
- Safe metadata extraction

### External API responses

- Expected status code
- Valid schema
- Correct types
- Values in range
- Correct encoding

### Database queries

- Use parameterized queries
- Never concatenate raw user input into SQL
- Validate types before the query
- Limit results

---

## Integration

Validate at the boundary:

- CLI: validate parsed arguments
- API: use schema models
- File upload: validate before save

---

## Enforcement (aspirational -- not implemented)

The pre-commit hook was meant to detect missing boundary validation patterns
such as:

- f-strings in SQL
- `form.get()` without validation
- `json.loads()` without error handling
- `os.system()` with unsanitized variables

Checked 2026-08-17 against the fleet hook actually installed at
`.git/hooks/pre-commit`: none of these patterns are checked anywhere in it.
This section describes what was planned, not what runs -- consistent with the
`[PROSE-ONLY]` marker at the top of this document, not a second, separate
enforcement claim.

---

## Spirit of Rule #30

- Exhaustive.
- Reject, do not coerce.
- At the boundary.
- Documented.
- Testable.
