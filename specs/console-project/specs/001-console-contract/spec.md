# Feature: Console contract reconstruction

## Source references

- Original route owner: `reverse.native-router`
- REA Evidence reference: `E-CONSOLE-001`
- Reverse Fusion evaluator: `reverse_fusion.vertical.evaluate_console`

## Functional requirements

- FR-001: Given an argument list, the independent implementation emits `argv`,
  `count`, and a space-joined `joined` value.
- FR-002: The candidate is compared against the frozen reference output with a
  complete Evidence reference.
- FR-003: Missing Evidence produces `unknown` and never produces `pass`.

## Success criteria

- SC-001: The correct candidate passes the deterministic console fixture.
- SC-002: The intentionally wrong candidate fails the same fixture.
- SC-003: The missing-Evidence variant is reported as `unknown`.

## Scope

This feature covers the selected console boundary only. It does not claim
whole-program source recovery or behavior outside the recorded fixture.
