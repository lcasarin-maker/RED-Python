---
id: DEBT-correccion-red-py-115-scanner-scan-en-la-2244eed5
title: red.py:115 — scanner.scan(...) en la linea 114 lanza un hilo daemon (core.py Sca
status: pagada-2026-08-17
created: 2026-08-16
---

## Finding

<!-- findings:start -->
- [CORRECCION] red.py:115 — scanner.scan(...) en la linea 114 lanza un hilo daemon (core.py Scanner._run) que solo llama on_done tras terminar su bucle os.walk (core.py:89-91); con --follow-symlinks activo (ns.follow_symlinks llega a Scanner y de ahi a os.walk(..., followlinks=follow) en core.py:109), un ciclo de symlinks hace que os.walk nunca termine, _run nunca llega a on_done(total), y done_event.wait() en la linea 115 c (detector: deadlock_without_heartbeat)
<!-- findings:end -->

## Acceptance

- [ ] The finding no longer reproduces, OR
- [ ] `status:` above is moved off `backlog` with the reason written here.

Re-running the guard must not regenerate this file.

## Pagada 2026-08-17

Arreglada por el enjambre `wf_6222d8b1-da5` y **verificada de forma independiente**:
el detector del hallazgo ya no dispara sobre `red_python/red.py`.
Sin commit: el cambio queda en el árbol de trabajo para revisión.

Razón registrada por quien la arregló:

> scanner.scan(...) lanza un hilo daemon (core.py Scanner._run) que solo llama on_done tras terminar su os.walk (topdown=False); con --follow-symlinks activo, un ciclo de symlinks hace que os.walk nunca termine (con topdown=False el walk hace todo el descenso recursivo ANTES de emi
