# REA WABT Evidence acceptance

Recorded 2026-11-14. The raw complete Evidence JSON is retained locally at
`state/rea-wasm-evidence.json` and is intentionally ignored by Git because it
contains this machine's absolute path. The committed facts below are a
traceable summary of that record; rerun the script to regenerate the complete
record.

## Reproduction

```powershell
.\scripts\run-rea-doctor.ps1
.\scripts\run-rea-wasm.ps1
```

The first command records the real REA stdio handshake (6.9.0, 255 tools, 6
prompts and catalog digest `2c725b48818ac5266198069330907c657f0fa2b6b8236065e5a191e20d95c2d7`).
The second script downloads the official WABT archive only when the pinned local
directory is absent, verifies the archive and three executable SHA-256 values,
sets `REA_WABT_BIN_DIRECTORY` for the child process only, and launches the
installed REA 6.9.0 CLI. It writes the complete JSON to `state/` and does not
write global configuration.

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


