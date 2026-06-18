# Coder Cerberus Master Control Manual

This document defines the immutable core of the Coder Cerberus protocol.
Its purpose is to eliminate silent failure in AI-assisted development through a
defensive modular architecture and a zero-trust audit environment.

## 1. Operating doctrine and mental model

The interaction between user and agent follows a strict principle of algorithmic
pessimism. No automatic correctness is assumed.

- **The Incompetent Intern:** the base mental model treats the AI as an overconfident
  assistant that may alter data or hide logic failures to please the operator.
- **Mandatory Amnesia:** each session starts with a clean initialization ritual.
  Prior conversation assumptions are ignored and the core repo manifests are reread.
- **Anti-triumphalism:** success cannot be declared based on a pretty UI or the absence
  of immediate errors. Success is validated only through execution traces and raw logs.

## 2. Temporal work structure

To keep order and avoid normative conflicts, development is split into four independent
sequential phases.

| Operational phase | Active critical mandates | Mandatory exit condition |
| :--- | :--- | :--- |
| 1. Startup | Purge context, index repo, verify core version parity | Environment integrity validated |
| 2. Planning | Hostile-path analysis, root cause diagnosis, schema structuring | Human approval of the physical plan file |
| 3. Execution | Surgical edits, no drift, mandatory logging | Approval from the automated multidimensional validator |
| 4. Validation | Adversarial tests, empirical evidence collection, rollback control | Green tests and consolidated decision history |

## 3. Current multidimensional validator

No functional change is consolidated into the main repo without passing these operational dimensions.

1. **D1: Code structure** - strict typing, zero static warnings, and allowed-file-list compliance.
2. **D2: Effective functionality** - complete unit-test coverage. Silent exception swallowing is prohibited.
3. **D3: Human validation** - raw terminal logs are mandatory physical evidence.
4. **D4: Security and I/O** - strict validation of inputs and outputs at system boundaries.
5. **D5: State integrity** - structural consistency in local persistence manifests.
6. **D6: Workspace hygiene** - temporary generation artifacts, obsolete scripts, and corrupt caches are removed.

## 4. Technical constraints

To contain code degradation risk, the system imposes hard barriers on automated agents.

- **No full-file rewrites:** changes must be atomic, targeted line-level replacements.
- **50-line insertion tax:** the agent has a strict 50-new-line limit per turn. After that, a simplicity pass is required.
- **No shell mutation hacks:** no sed or stream redirection for code changes. Structural mutation must go through formal editing tools.
- **Mandatory logging:** every new logical function must record structured logs exposing inputs and final state.

## 5. Escalation and interruption protocol

The operational agent stays fully focused on the assigned task. Secondary findings,
adjacent optimizations, or minor non-blocking issues do not stop progress. They are
documented in the logistics history for later review in a dedicated session.
Execution is interrupted only for real technical blockers, critical security issues,
or imminent session-resource exhaustion.
