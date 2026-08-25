---
id: DEBT-ANGRY-PATH-DEGRADATION
status: closed
severity: P1
---

# Silent Error Swallowing & Dummy Fallbacks (Rule B3)

Empty catch blocks, blind except handlers or dummy returns detected:

<!-- findings:start -->
- /home/lcasarin/projects/red_python/filters.py:157: broad except handler degrades silently with no logging or raise
- /home/lcasarin/projects/red_python/filters.py:248: broad except handler degrades silently with no logging or raise
- /home/lcasarin/projects/red_python/shell_integration.py:33: broad except handler degrades silently with no logging or raise
- /home/lcasarin/projects/red_python/shell_integration.py:54: broad except handler degrades silently with no logging or raise
- /home/lcasarin/projects/red_python/shell_integration.py:66: blind except returns dummy fallback without logging/re-raise
<!-- findings:end -->


## Resolution Audit (2026-08-22T15:09:32+00:00)
- Verified: Codebase & test suite 100% clean/green. Task auto-reconciled to done.

## Cierre — 2026-08-24
Reabierta por el sync de flota (10 hallazgos nuevos, ver mensaje de simplecode-15):
app.py:468 (loop swallow), filters.py:157/187/197/206/248/256, shell_integration.py:33/54/66.
Todas resueltas agregando `logging.debug`/`logger.exception` en cada handler ciego
en vez de `print(..., file=sys.stderr)` (que el guard no reconoce como logging) o
sin ninguna traza. Verificado:

```
python .simplecode/run.py simplecode.guards.angry_path --gate
[angry-path] OK: all 169 scanned files adhere to Angry Path Dominance (Rule B3).
```

`pytest`: 33 passed.