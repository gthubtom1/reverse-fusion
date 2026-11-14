# Implementation plan

1. Freeze route R5 and the original Release .NET artifact Evidence.
2. Let the current host Builder write the candidate source inside `state/`.
3. Build original and candidate with the repository-selected .NET SDK path.
4. Run REA artifact/member inspection and exact managed comparison.
5. Replay inputs, emit canonical reconstruction proof, ledger and cleanup.
