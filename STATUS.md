# STATUS.md - RED-Python satellite status

## Current state

- The repository is being normalized as a CC-supervised satellite.
- `AGENT.md` is now a short entrypoint and the onboarding contract is the
  source of truth.
- The active runtime, CLI, adapters, and core authority docs are now English.
- The onboarding, supervision, and learning structure is now present.
- Foreign changes are now explicitly part of the onboarding protocol and must
  be absorbed, validated, discarded, or quarantined.
- The wiki vault is in place for CC audits.
- A local governance helper and satellite-specific tests have been added.
- The GitHub home is recorded explicitly so visibility is not left implicit.
- Private is the default; public visibility needs explicit authorization.

## What changed in this pass

- Clean satellite README in English.
- External audit contract rewritten around satellite onboarding and supervision.
- Learning flow documented for satellite -> CC -> GS promotion.
- Core runtime strings, CLI output, and adapter docs translated to English.
- Structured learning schema and template added.
- Wiki navigation pages added for the satellite contract.
- `scripts/satellite_governance.py` added as a stdlib-only validator and packet builder.
- `docs/DEBT_LEDGER.md` added as the canonical operational debt tracker.
- `docs/supervision/GITHUB_HOME.md` added as the GitHub home evidence record.

## Remaining debt

- Validate the new docs and wiki with CC tooling.
- Keep historical archives and deprecated material quarantined instead of
  letting them drift back into the active surface.
- Keep the GitHub home record current and resolve the public/private policy
  debt with explicit authorization when ready.
- Keep the tree clean after every onboarding pass.

## Next step

Run the validator, review-changes helper, and the test suite, then refine any
failures before pushing the satellite back upstream.
