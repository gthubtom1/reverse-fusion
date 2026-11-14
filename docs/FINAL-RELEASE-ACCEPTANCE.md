# Final v1 release acceptance

This release closes `reconstruction-product-v1` for the bounded target and
provider surfaces declared in `docs/PRODUCT-GOAL.md`. It does not claim that
future targets or unavailable runtime providers have been exercised.

| Gate | Direct evidence | Result |
|---|---|---|
| Fresh clone and lifecycle | Remote `https://github.com/gthubtom1/reverse-fusion` at commit `029f4fe093b0d93ff92ca0a1de5565d3f655ecf7`; `fresh-clone-rf22-029f4fe` runs local `install`, `plan`, `doctor`, `update`, `uninstall`, `contracts`, `handoff`, `bridge --source local` and 14 Python tests without an old receipt | pass |
| Single route owner | `bridge --source local` resolves repository `routing.json`; external route is explicit read-only compatibility | pass |
| Official identities | `SOURCE-MANIFEST.json`, official REA `6.9.0`, Spec Kit `1.4.0`, Craft `0.6.1`, JADX MCP `0.7.1` manifest | pass |
| Real host Builder | Codex generated the APK candidate; `prepare`, `build`, `check`, `refine`, `return_summary`, `cleanup` pass; no `--model`; `config_mutation=false` | pass |
| WASM chain | original/candidate/comparison/proof Evidence and ledger `rol_09e99625528899bcc2b492bdc7b2811b44fb573c13418ff80af0404548039928`, `required_open=0` | pass |
| Web/JavaScript chain | original/candidate/comparison `ev_216f5663a396f32a8c09777922294d6149abcee640129d9911fb62e150b47a75`, runtime proof, ledger `rol_39c38b659a45e5b080c5dc55870f154eb17b9e484fb998aacba88d07cd579c48`, `required_open=0` | pass for reviewed export; static/package unknowns retained |
| PE/.NET chain | original/candidate managed Evidence, exact member comparison, four runtime traces, ledger `rol_53dd8e6683c0351977afc491a5c50863e56a390e5925d0c6d63fde1372bebba9`, `required_open=0` | pass |
| APK/DEX chain | pinned JADX 0.7.1; original/candidate package/class Evidence, static comparison and ledger `rol_b9833a0dd114ad263d96217960a2990d87c9e3629048488d3f4f2379f93762b`, `required_open=0` | static pass; Android runtime unknown without adb/emulator |
| Three-state behavior | WASM correct=`pass`, intentionally wrong=`fail`, missing Evidence=`unknown` | pass |
| Host status | Codex/Pi handshakes pass; Claude missing-login boundary is recorded as blocked | pass with explicit provider boundary |
| Cleanup and scope | generated state/build files ignored; builder and probes record cleanup; old repository, old installs and global config remain unchanged | pass |
| Consistency | Python tests, contracts, `git diff --check`, docs, manifests, checkpoint and GitHub remote agree | pass |

## Retained boundaries

- Native Craft R46 qualification is unsupported; the verified product path is a
  host-owned Builder whose current model and provider belong to Codex/Pi/Claude.
- Windows REA process capture is unsupported because descendant cleanup has not
  been qualified.
- Web static semantic unknowns and package/parser obligations are recorded as
  unknown scope, not silently closed.
- Android device/runtime behavior is unknown on this host because no adb device
  or emulator was available.

These boundaries are part of the product contract. A future target closes its
own case by attaching original Evidence, frozen Spec tasks, a qualified host
Builder, candidate build/run observations, comparison, proof, cleanup and a
ledger with the same fail-closed semantics.
