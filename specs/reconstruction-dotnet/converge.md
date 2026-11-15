# Converge record

## RF-20

- Build: original and candidate Release DLLs built with .NET 8.
- Static comparison: one unchanged `Answer` member and one build-local changed
  `Main` member; no unknown members.
- Runtime: four finite inputs pass with identical output.
- Obligation ledger: `dotnet-answer` verified with `required_open=0`.
- Cleanup: verified; host Builder records `config_mutation=false`.

## RF-25 audit correction and current replay

- Earlier host CLI text smoke is transport-only; it did not generate this project.
- The current conversation agent generated the archived candidate source from frozen task/research files; see `evidence/rf22/builder/manifest.json`. File checks and business acceptance are separate.
- Current original/candidate Evidence, comparison, proof, inputs and ledger are in `evidence/rf22/dotnet/`; identities are indexed by the archive manifest. The older archive was superseded after identity authentication failed.
- Bounded execution cleanup is observed; no unqualified descendant containment claim is made.
- .NET8 build and four executable traces pass. Official MCP compares the exact retained member Evidence; no unexported CLI parent IDs remain.
