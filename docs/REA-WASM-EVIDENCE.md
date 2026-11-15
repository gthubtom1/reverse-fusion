# REA / WABT bounded Evidence acceptance

The latest representative archive is indexed by `evidence/rf22/manifest.json`.
RF-25 regenerates raw records from actual runs; it supersedes the previous
path-normalized archive whose Evidence IDs no longer authenticated. Historical
absolute paths are observations, not deployment settings. Do not replace a
hash-covered field and retain its old Evidence ID.

## Reproduction

Choose a local Node path satisfying the pinned REA engine range
`^22.23.4 || ^24.22.1 || >=26.12.1`, then on the exercised PowerShell surface:

```powershell
$env:REVERSE_FUSION_NODE = "[supported Node absolute path]"
.\scriptsun-rea-doctor.ps1
.\scriptsun-wasm-vertical.ps1
.\scriptsun-rea-ledger.ps1
```

The bootstrap scripts fetch the official `rea-agents@6.9.0` and WABT `1.0.42`
into ignored repository-local vendor directories, verify pinned integrity and
archive/executable hashes, and configure child processes only. The runners
stop on native failures and do not accept old JSON output as a fresh success.
They write execution products under `state/`, without global configuration.

The original exports `answer: () -> i32` and contains `i32.const 42`. The
correct candidate returns 42; the wrong candidate returns 7. Interface equality
alone is insufficient: real WABT interpreter replay yields correct=`pass`,
wrong=`fail`; missing candidate Evidence yields `unknown`. The executable and
artifact digests are rechecked before use.

## Proof and ledger

The repository-owned bounded verifier uses the pinned official REA serializer.
It checks original/candidate artifact hashes, executes the interpreter, preserves
source/comparison links and emits `rea.reconstruction-proof` for the declared
answer obligation. This is an integration verifier, not REA's native process
capture verifier. Its actual observed values determine passed/failed bindings;
a self-reported constant is not accepted.

Official REA builds the ledger from those records and the reviewed obligation.
The finite correct run is ready with `required_open=0`; exact Evidence, proof and
ledger IDs are read from the current archive and RF-25 checkpoint rather than a
second hand-maintained ID list here. Run `scripts/verify-evidence.mjs` after REA
bootstrap to admit identities/links and exercise a real tamper rejection.

This establishes the declared fixture behavior only. It does not establish
source recovery, arbitrary WASM behavior or unrelated network/runtime claims.
