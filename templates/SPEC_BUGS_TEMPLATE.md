# SPEC_BUGS — Template para Bug Fixes (5 minutos)

**Cómo usar:** Copia este template, rellena con tu bug específico, guarda como `SPEC_BUGS.md`, ejecuta:
```bash
python scripts/spec_executor.py SPEC_BUGS.md
```

---

## Bug #XXX: [Título breve del bug]

**Descripción (1-2 líneas):**
[Qué está mal y cómo afecta al usuario]

---

### Ubicación
```
archivo.py:línea
```

Ejemplo: `src/auth/login.py:45`

---

### Síntomas (cómo se ve el bug)
- [Comportamiento observado #1]
- [Comportamiento observado #2]
- [Impacto en usuario]

Ejemplo:
- Login timeout after 5 seconds with no error message
- User sees blank screen
- Application appears frozen

---

### Requerimientos (checklist de qué arreglar)

- [ ] Requirement 1: Description
- [ ] Requirement 2: Description
- [ ] Requirement 3: Description

**Ejemplo:**
- [ ] Catch timeout exception from requests.get()
- [ ] Display error message: "Connection timeout. Please retry"
- [ ] Implement retry logic: 1s, 2s, 4s exponential backoff
- [ ] Log error to protocol_state.db
- [ ] No new dependencies required
- [ ] Backward compatible (no API changes)

---

### Restricciones (limitaciones/reglas)

- [Restricción 1]
- [Restricción 2]

**Ejemplo:**
- Cannot modify database schema (no migrations)
- Must maintain existing function signature
- Retry max 3 attempts total

---

### Aceptación (Qué prueba que está arreglado)

- [x] Acceptance criterion 1
- [x] Acceptance criterion 2

**Ejemplo:**
- [x] Login timeout caught and handled gracefully
- [x] User sees error message within 100ms of timeout
- [x] Auto-retry succeeds on 2nd attempt (80%+ of time)
- [x] No regression: existing 12 tests still pass
- [x] New test covers timeout scenario

---

## NOTAS

- **Tiempo estimado en SPEC:** 5 minutos (escribir bug description)
- **Tiempo AI ejecuta:** 2-5 minutos (design + code + tests + commit)
- **Total reducción:** 90% (vs manual 30-45 min)
- **No decisiones manuales** — AI genera todo de SPEC

---

## Workflow Automático

```
[You write SPEC_BUGS.md]
       ↓
[python spec_executor.py SPEC_BUGS.md]
       ↓
[AI parses SPEC]
       ↓
[AI generates fix code]
       ↓
[AI generates test cases]
       ↓
[AI runs pytest]
       ↓
[AI validates acceptance criteria]
       ↓
[git commit + export to DB]
       ↓
[DONE — bug fixed, tested, committed]
```

---

## Ejemplo Real: Login Timeout Bug

```markdown
## Bug #042: Login endpoint timeout not handled

Descripción: When login endpoint is slow (>5 seconds), user sees blank screen with no feedback.

### Ubicación
src/auth/login.py:45

### Síntomas
- User clicks "Login", waits 5 seconds, sees blank screen
- No error message
- App appears frozen
- Bad UX: user doesn't know what happened

### Requerimientos
- [ ] Catch timeout exception in requests.get(timeout=5)
- [ ] Return JSON: {"error": "Connection timeout. Please retry"}
- [ ] Implement retry: 1s, 2s, 4s backoff (max 3 attempts)
- [ ] Log to protocol_state.db: {timestamp, error_type, attempt_count}
- [ ] Keep response time < 100ms (no blocking)
- [ ] No changes to login() function signature

### Restricciones
- Cannot modify POST /api/auth/login endpoint
- No new dependencies (already have requests)
- Must work with existing Aequitas_OS BD schema

### Aceptación
- [x] User sees "Connection timeout" message within 100ms
- [x] 2nd attempt auto-retries with 1s backoff
- [x] Succeeds on 2nd try 80%+ of time (mock tested)
- [x] All 12 existing tests pass (no regression)
- [x] New test: test_login_timeout_retry() included
```

---

## Tips

1. **Síntomas claros** → AI código mejor
2. **Requerimientos específicos** → menos iteraciones
3. **Aceptación medible** → validación automática
4. **Restricciones listadas** → no sorpresas
