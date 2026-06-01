# Sprint 8 KISS Audit

## Scope
- Flatten operational entrypoints where nesting added no real encapsulation.
- Keep the remaining structure only when it groups cohesive assets or preserves clarity.

## Changes Applied
- Moved `scripts/dashboard/server.py` to `scripts/serve_dashboard.py`.
- Moved `scripts/automation/monitor_projects.py` to `scripts/monitor_projects.py`.
- Moved `scripts/automation/monitor_heartbeat.py` to `scripts/monitor_heartbeat.py`.
- Kept `protocol_engine/rules/` as a logical data namespace because it groups rule YAMLs under one loader.

## Verdicts
- `scripts/` entrypoints: `OPTIMAL` after flattening the visible one-off subdirectories.
- `protocol_engine/`: `ADECUADO`, because the nested `rules/` folder is cohesive and data-driven.
- `docs/`: `ADECUADO`, because the hierarchy still serves human navigation.

## Conclusion
- No further flattening is justified right now without turning clarity into churn.
- The KISS goal for Sprint 8 is satisfied by reducing avoidable directory depth and preserving only the namespaces that still add signal.
