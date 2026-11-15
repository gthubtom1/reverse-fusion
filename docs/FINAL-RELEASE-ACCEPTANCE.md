# v1 release acceptance

RF-25 is the current audit of product `1.0.0`. Its completion status is read
from `docs/CURRENT-STATE.md` and `checkpoints/RF-25-20261115-001.md`; RF-22,
RF-23 and RF-24 checkpoints preserve historical observations and do not
override this audit. The declared finite gates below passed, including a
remote fresh clone of the audited source commit; runtime boundaries remain explicit.

| Gate | Direct record / scope | Current result |
|---|---|---|
| URL-only deployment | `docs/AGENT-BOOTSTRAP.md`, linked by README and AGENTS; current selected host, local venv/receipt | implemented; final remote fresh-clone check recorded in RF-25 checkpoint |
| One Reverse owner | local routing JSON, descriptors, domain bodies and required reads; no old receipt needed | contracts and hard-target route pass in remote clone |
| Retained enhanced domains | 603-file preservation inventory, upstream/local SHA and reasons for adaptations | 603/603 source and local digests pass, 13 recorded adaptations |
| Component identities | REA 6.9.0; Spec source 1.4.1.dev0 vs historical CLI 1.4.0; WABT1.0.42; JADX0.7.1; interface-only Craft reference | explicit and separate from local provider health |
| Real candidate writer | current conversation host freezes task/research hashes and generates eight source files; session check/refine/finish | observed; candidate writes are not business acceptance |
| Child CLI boundary | actual Codex child build returned out of credits | blocked, not required by current-session path |
| Evidence archive admission | raw RF-25 records under stable `evidence/rf22/` path; official identity parsing, link closure, tamper rejection and file digests | 28 records authenticated, links closed, 4 tamper controls rejected, 40 file hashes and Builder input/output hashes pass |
| WASM | real interpreter values and official REA bounded ledger; correct/wrong/missing cases | pass/fail/unknown respectively |
| Web/JavaScript | real original/candidate analysis, inventory, export replay, proof and bounded ledger | finite export pass; full graph ledger unknown with 4 required open |
| PE/.NET | actual .NET8 build/run, managed member comparison, finite replay, proof and ledger | bounded method pass |
| APK/DEX | actual build and real package/class inspection, manifest/member comparison, proof and static ledger | bounded static pass; Android runtime unknown |
| Optional host probes | exact final assistant sentinel, selected client, config snapshots and finite deadline | Pi pass, Codex credits blocked, Claude login blocked; config digests unchanged |
| Failure boundaries | stale candidates, existing-file edits/deletions, source/task drift, links/path traversal, provider failure | focused counterexamples pass; actual native failure and Node24.20 engine rejection observed |
| Scope and cleanup | repository-local writes; global configuration snapshots where observed; ignored build outputs | per-run cleanup scope recorded; uncertain descendants remain unknown |
| Documentation and release | current docs/manifests/checkpoint, tests, `git diff --check`, GitHub commit and remote fresh clone | RF-25 closed; tested source a643b958774dc8d90b3be29f68aff5d5d0f0b91a, 37+39 tests pass; final docs closure follows |

The canonical IDs are in `evidence/rf22/manifest.json`; this table does not keep
a second independently edited list of IDs. The RF-25 checkpoint records exact
test counts, clone commit and remaining provider boundaries after final checks.

## Retained runtime boundaries

- Current-session Builder uses the already active host and adds no CLI account
  or model dependency. Optional CLI transport has its own live status.
- Craft native R46 is unsupported and the current companion is unobserved. The
  repository does not distribute the four historical patches.
- Windows REA PTY descendant cleanup remains unsupported.
- Web runtime proof covers the declared finite answer cases. The complete graph
  ledger is `unknown`: 5 total, 1 verified and 4 required open obligations (2
  packaging and 2 application/parser); comparison links are retained. Its
  archive is `evidence/rf22/web/full-ledger.json`.
- APK proof covers manifest/member projections. It does not establish Answer
  method body behavior, a launchable application or device execution. The
  fixture MainActivity is not a functioning Android Activity.
- PowerShell provider runners have been exercised on the audit host; Git Bash
  checks do not claim native Linux or macOS hardware execution.

These boundaries are valid operational states inside the declared integration
scope. They do not establish full equivalence for a future target. A new target
gets its own Evidence, frozen tasks when reconstructing, candidate, observations,
comparison, cleanup and obligation ledger.
