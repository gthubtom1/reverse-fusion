# Converge record

## RF-20

- Build: original and candidate Release DLLs built with .NET 8.
- Static comparison: one unchanged `Answer` member and one build-local changed
  `Main` member; no unknown members.
- Runtime: four finite inputs pass with identical output.
- Obligation ledger: `dotnet-answer` verified with `required_open=0`.
- Cleanup: verified; host Builder records `config_mutation=false`.
