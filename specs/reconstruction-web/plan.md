# Implementation plan

1. Freeze route R3, original REA Evidence and the bounded task list.
2. Use the host-owned Builder to write only the candidate module files.
3. Run REA static analysis and export-shape comparison.
4. Replay finite Node inputs, emit `rea.reconstruction-proof`, and build the
   official obligation ledger.
5. Preserve static partial/unknown coverage and cleanup evidence in the case.
