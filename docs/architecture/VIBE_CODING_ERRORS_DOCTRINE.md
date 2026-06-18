# Vibe Coding Errors Doctrine

This doctrine catalogues the failure modes that appear when vibe coding replaces disciplined engineering.

## Core idea

The problem is not speed. The problem is when the workflow rewards appearance over correctness.

## Common failure modes

- Silent debt accumulation.
- Prototype drift becoming permanent.
- Happy-path bias.
- UI optimism that hides broken logic.
- Documentation that claims more than the code delivers.

## Required countermeasures

- Validate before declaring success.
- Prefer reproducible evidence over narrative.
- Treat every generated code block as suspect until proven.
- Keep tests behavior-based and adversarial.
- Keep the scope small and the changes surgical.

## Architectural lessons

- A pretty demo is not a working system.
- A working system without tests is fragile.
- A clean README is not a clean implementation.
- A model that sounds confident is not a model that is correct.

## Final rule

If the system says green but the behavior is not proven, the green is a lie.
