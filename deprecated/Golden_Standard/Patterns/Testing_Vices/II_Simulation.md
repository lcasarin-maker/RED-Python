# VT-II: Simulation & Isolation (VT-023..034)

**Source:** `deprecated/BIBLIOTECA_VICIOS_TESTING_EVALUACION.md` (Category II)
**Status:** ACTIVE | **Entries:** 12 | **Date:** 2026-06-02
**Focus:** False mocks, incomplete fakes, simulation theater

---

## Catalog

| ID | Name | Symptom | Root Cause | Prevention |
|---|---|---|---|---|
| **VT-023** | Complacent Mock | Simulates success | Reality substituted | Calibrate against real system |
| **VT-024** | Incomplete Fake | Omits hard cases | Partial model | Test against real system |
| **VT-025** | Network Stub | Old response frozen | Frozen environment | Live contract tests |
| **VT-026** | Simplified Database | Rules differ | Different semantics | Test equivalent engine |
| **VT-027** | Fixed Clock | Always ideal dates | Variance eliminated | Test temporal boundaries |
| **VT-028** | Controlled Randomness | Doesn't explore distribution | Hidden variance | Test statistical properties |
| **VT-029** | Fake Filesystem | Doesn't test perms/locks | Idealized resource | Test with real filesystem |
| **VT-030** | Friendly Monkey Patch | Real system untested | Invasive substitution | Limit patches |
| **VT-031** | Stubbed Command | Prints installed | Simulated action | Verify external effect |
| **VT-032** | Partial Mock Scan | Incomplete coverage | Universe incomplete | Scan active domain |
| **VT-033** | Wrapper as Fix | Layer hides broken contract | Occlusion of cause | Fix subject, not judge |
| **VT-034** | Placeholder Approved | Incomplete passes | Form confuses completion | Real behavior before approval |

---

## Prevention Path

1. **Suspect simulation** → Calibrate against real
2. **Expand hard cases** → Include edge domains
3. **Live contracts** → Not frozen mocks
4. **Resource parity** → Real perms, locks, timing
5. **Wrapper blocks approval** → Fix root, not adapter

---

## Related

- **VC-118:** Zombie Compat (wrappers as evasion)
- **S4:** Modularity (schema validation at boundaries)

