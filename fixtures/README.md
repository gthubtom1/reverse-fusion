# Local fixtures

`answer.wasm` is a 39-byte deterministic smoke fixture used to probe the REA
WASM adapter when a WABT 1.0.42-compatible directory is configured.
`answer-candidate.wasm` is the correct independent candidate and
`answer-wrong.wasm` returns 7 instead of 42 so the acceptance comparator has a
known failing variant. These are controlled fixtures, not real targets, and
carry no source-recovery claim.
