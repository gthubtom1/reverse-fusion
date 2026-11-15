# RF-22 representative Evidence

This directory contains RF-25 authenticated Evidence, comparison,
proof and obligation-ledger records for the four representative product
chains:

- `wasm/` — WABT inspection, interface comparison, runtime proof and ledger;
- `web/` — Web/JavaScript export comparison, runtime proof and ledger;
- `dotnet/` — PE/.NET managed-member comparison, runtime proof and ledger;
- `apk/` — APK/DEX package and class comparison, static proof and ledger.

`manifest.json` records the SHA-256 digest of every tracked artifact. The
records prove the shared analysis-to-reconstruction contract for bounded
representative targets. They do not claim that every future packer, obfuscator,
device or runtime has already been executed; those target-specific states stay
`unknown`, `blocked` or `unsupported` until their Evidence is attached.

The `rf22` path remains stable. RF-25 supersedes the old path-rewritten records:
hash-covered fields and Evidence IDs are retained together. Historical absolute
paths are observations, never installation settings. JSON formatting and a
transport BOM may change; semantic fields are not path-normalized.

Each target includes a complete linked `bundle.json` plus original, candidate,
comparison, proof, ledger and ledger input. The Web `ledger.json` closes the
bounded answer replay; `full-ledger.json` is independently retained as unknown
with 5 obligations / 1 verified / 4 required open. APK static projections do not
establish method bodies or Android launch behavior.

`builder/` retains the actual current-session receipt, frozen input versions,
archive mapping and eight generated source files. Its receipt observes writes;
business acceptance belongs to the separate target proof/ledger records. The
archived frozen task versions describe the input at preparation time; current
Spec tasks and append-only converge corrections describe the latest result.

After the pinned REA package is bootstrapped, run `node scripts/verify-evidence.mjs`
with an engine-compatible Node. It checks file digests, official Evidence and
bundle admission, linked closure, tamper rejection and frozen Builder/source hashes.
