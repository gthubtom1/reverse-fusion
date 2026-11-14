# REA WABT Evidence acceptance

Recorded 2026-11-14. The raw complete Evidence JSON is retained locally at
`state/rea-wasm-evidence.json` and is intentionally ignored by Git because it
contains this machine's absolute path. The committed facts below are a
traceable summary of that record; rerun the script to regenerate the complete
record.

## Reproduction

```powershell
$env:REVERSE_FUSION_NODE = "[Node 22.23.4+ absolute path]"
.\scripts\run-rea-doctor.ps1
.\scripts\run-rea-wasm.ps1
```

The first command records the real REA stdio handshake (6.9.0, 255 tools, 6
prompts and catalog digest `2c725b48818ac5266198069330907c657f0fa2b6b8236065e5a191e20d95c2d7`).
The scripts bootstrap the official `rea-agents@6.9.0` npm package into the
ignored local `vendor/rea` directory, verify its pinned npm integrity, download
WABT only when the pinned local directory is absent, verify the archive and
three executable SHA-256 values, set `REA_WABT_BIN_DIRECTORY` for child
processes only, and launch the REA CLI. They write complete JSON to `state/`
and do not write global configuration.

## Toolchain identity

- WABT release: `1.0.42`
- WABT archive SHA-256: `62f1eb2b51aa57cf0f0b8ba333bf2c72a049930aa9c5de01dcad271c4fe48c88`
- WABT source commit: `ff0ef7e0009402740c805a9744c09b05be063e48`
- REA: `6.9.0`
- REA provider: `wabt-artifact`, `wabt@1.0.42`
- Raw Evidence JSON SHA-256: `8422a8c4b1cbf3e5c509d59e7d6c1e8ddc7a10e190eaa1bd45f0fba444d07464`

## Observed Evidence

- Evidence ID: `ev_d6ed8f580f5b6d7fb001de26c8b8b6732fd32308f8aeb6eeb624738209e35f96`
- Artifact SHA-256: `ccf59f0f7a7625ee380ed228905aadfa11072ac14cea1c53d1e7f3953d4d48c6`
- Artifact size: 39 bytes
- Validation: `valid`
- Sections: Type, Function, Export and Code
- Export: `answer`, kind `func`, signature `() -> i32`
- Decoded WAT contains `i32.const 42`
- Runtime execution: `not-performed`
- Network fetch: `not-performed`

This is a real REA Evidence acceptance for the committed smoke fixture and the
pinned WABT toolchain. It does not claim original-source recovery or runtime
equivalence for an arbitrary target.

## Candidate differential slice

The same runner produces Evidence for `answer-candidate.wasm` and
`answer-wrong.wasm`, then `accept --fixture wasm` compares the original and
candidate interface facts and runs the bounded WABT interpreter:

- Correct candidate Evidence: `ev_85ebdcc34c5cb2ad48b8b5ed7760bcba11c1ff9fcf4fd09db0507872f42325f6`; interface equal, runtime `42 == 42`, status `pass`.
- Wrong candidate Evidence: `ev_cedc85b38d8f32880336028cf449293f3008d6529cc2756baf47a8232488efba`; interface equal, runtime `42 != 7`, status `fail`.
- Missing candidate Evidence: status `unknown`.

This proves the acceptance plane can catch a behavior change that a declared
interface comparison alone would miss.

## Obligation ledger closure

`scripts/run-rea-ledger.ps1` is the reproducible bridge from the accepted
vertical slice to REA's reconstruction-obligation authority. It regenerates a
canonical bundle containing the original and candidate inspection Evidence, the
REA WASM interface comparison, and a bounded `rea.reconstruction-proof` record
produced by the WABT interpreter run. The proof record is the Evidence consumed
by both the fixture and verifier bindings; ordinary inspection Evidence is not
treated as proof by the ledger.

The recorded run produced:

- Interface comparison Evidence: `ev_7feb4947e20562d5adf55dd6f5ad98a58a8e29516c5eeb82bf7b29e691ec6249`.
- Reconstruction proof Evidence: `ev_59a71030abee7eac0677de1b5282c8b7d709319c70e1a3074bf305c18ce43bec`.
- Ledger: `rol_09e99625528899bcc2b492bdc7b2811b44fb573c13418ff80af0404548039928`.
- Closure digest: `eb14c2b9101158f68ceecdb02f2d3d80d8c8b1e723c95d85bf3438e022dcc4b2`.
- Ledger status: `ready`, with `required_open: 0` and one `verified`
  obligation (`wasm-answer`).

The proof is finite and target-specific: it records the declared `answer`
export, the `answer() => i32:42` WABT run, and the exact original/candidate
Evidence links. It does not broaden into global source or runtime equivalence.


