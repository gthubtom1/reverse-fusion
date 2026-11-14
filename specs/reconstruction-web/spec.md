# Feature: Web/JavaScript reconstruction case

## Source references

- Reverse route: `R3` (`components/reverse-core/routes/R3.md`)
- Original REA Evidence: `state/rea-web-original.json`
- Candidate REA Evidence: `state/rea-web-candidate.json`
- Runtime proof: `state/rea-web-proof-evidence.json`

## Functional requirements

- FR-WEB-001: Preserve the `answer(value)` export and its `rf:` + trim +
  uppercase behavior.
- FR-WEB-002: Compare the original and candidate static export shape and retain
  REA unknowns when the analyzer cannot prove an expression.
- FR-WEB-003: Run a finite input set through both modules and record a typed
  reconstruction proof and cleanup result.

## Scope

The case covers the selected module and finite Node runtime traces. Browser
rendering, network behavior, packaging lifecycle and unmodeled JavaScript
semantic nodes remain explicit REA unknowns.
