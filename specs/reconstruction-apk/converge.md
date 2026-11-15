# Converge record

## RF-21

- Builder: Codex host generated the two bounded Java outputs and completed
  prepare/build/check/refine/return_summary/cleanup.
- Build: javac, D8 and AAPT produced a candidate APK.
- Static comparison: package and `Answer` class projections pass; APK ledger
  `apk-answer-static` is verified with `required_open=0`.
- Android runtime: unknown because this host has no adb device or emulator;
  this remains an explicit provider boundary.
- Cleanup: verified; no host/global configuration mutation was recorded.

## RF-25 audit correction and current replay

- Earlier host CLI text smoke is transport-only; it did not generate this project.
- The current conversation agent generated the archived candidate source from frozen task/research files; see `evidence/rf22/builder/manifest.json`. File checks and business acceptance are separate.
- Current original/candidate Evidence, comparison, proof, inputs and ledger are in `evidence/rf22/apk/`; identities are indexed by the archive manifest. The older archive was superseded after identity authentication failed.
- Bounded execution cleanup is observed; no unqualified descendant containment claim is made.
- javac release-8/D8/AAPT build and manifest/member projections pass. The fresh verification rebuild produces a new APK artifact hash from the unchanged pinned fixture sources; its newly analyzed original Evidence is the verification baseline. The completed Builder receipt retains its earlier research version without rewriting it. Static projection proves neither method-body behavior nor an Activity launch; Android runtime remains unknown.
