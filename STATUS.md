# STATUS.md - RED-Python satellite status

## Current state

- The repository is being normalized as a CC-supervised satellite.
- `AGENT.md` is now a short entrypoint and the onboarding contract is the
  source of truth.
- The onboarding, supervision, and learning structure is now present.
- Foreign changes are now explicitly part of the onboarding protocol and must
  be absorbed, validated, discarded, or quarantined.
- The wiki vault is in place for CC audits.
- A local governance helper and satellite-specific tests have been added.

## What changed in this pass

- Clean satellite README in English.
- External audit contract rewritten around satellite onboarding and supervision.
- Learning flow documented for satellite -> CC -> GS promotion.
- Structured learning schema and template added.
- Wiki navigation pages added for the satellite contract.
- `scripts/satellite_governance.py` added as a stdlib-only validator and packet builder.

## Remaining debt

- Validate the new docs and wiki with CC tooling.
- Run the satellite tests and confirm they stay green.
- Review the remaining legacy mixed-content files and decide what should be
  preserved versus deprecated.
- Confirm the GitHub repository visibility matches the supervision policy.
- Keep the tree clean after every onboarding pass.

## Next step

Run the validator, review-changes helper, and the test suite, then refine any
failures before pushing the satellite back upstream.
