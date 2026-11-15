# Feature: PE/.NET reconstruction case

## Source references

- Reverse route: `R5` (`components/reverse-core/routes/R5.md`)
- Original REA Evidence: `evidence/rf22/dotnet/original.json` and
  `evidence/rf22/dotnet/original-members.json`
- Candidate REA Evidence: `evidence/rf22/dotnet/candidate.json` and
  `evidence/rf22/dotnet/candidate-members.json`

## Functional requirements

- FR-DOTNET-001: Preserve the managed `Program.Answer` signature and behavior.
- FR-DOTNET-002: Compare exact managed member signatures and retain changed
  build-local methods in the comparison result.
- FR-DOTNET-003: Replay finite command-line inputs and close the reviewed
  obligation only from typed proof Evidence.
