# Feature: PE/.NET reconstruction case

## Source references

- Reverse route: `R5` (`components/reverse-core/routes/R5.md`)
- Original REA Evidence: `state/rea-dotnet-original.json` and
  `state/rea-dotnet-original-members.json`
- Candidate REA Evidence: `state/rea-dotnet-candidate.json` and
  `state/rea-dotnet-candidate-members.json`

## Functional requirements

- FR-DOTNET-001: Preserve the managed `Program.Answer` signature and behavior.
- FR-DOTNET-002: Compare exact managed member signatures and retain changed
  build-local methods in the comparison result.
- FR-DOTNET-003: Replay finite command-line inputs and close the reviewed
  obligation only from typed proof Evidence.
