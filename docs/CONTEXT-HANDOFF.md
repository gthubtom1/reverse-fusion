# Context Handoff

Before ending a session or compressing context, update `docs/CURRENT-STATE.md`
and the current checkpoint. Recover state from the checkout and execution
records rather than chat history.

Current handoff: RF-27, product `1.0.0`, 2026-11-16.

- Repository: <https://github.com/gthubtom1/reverse-fusion>, branch `master`.
- Deployment entry: `docs/AGENT-BOOTSTRAP.md`. This travels with the repository;
  the user does not need to keep or repeatedly paste a chat prompt.
- Current status and next action: `docs/CURRENT-STATE.md`. Audit closure and
  exact scope and checks: `checkpoints/RF-27-20261116-001.md`.
- Product contract: `docs/PRODUCT-GOAL.md`. Architecture is an adaptive helper
  for the current host, not a model choice or fixed reverse-engineering order.
- Default writer: current-session Builder. Frozen tasks/research and allowed
  candidate writes are observed by `session prepare/check/refine/finish`.
  Task commands use the outcome project's `--project-root` (default cwd).
  Case-bound prepare reuses the handoff checker and freezes the semantic review;
  it cannot prove semantic readiness or discover omitted dependencies.
  Business proof remains independent. Optional child Codex currently has a
  credits block; earlier text smoke is not an APK candidate.
- Archive: `evidence/rf22/manifest.json` indexes current raw representative
  Evidence, proof and ledgers. RF-25 supersedes the identity-invalid normalized
  archive without changing hash-covered paths under an existing Evidence ID.
- Scope: WASM three-state check, Web finite export replay and .NET finite method
  replay; APK build/static manifest/member comparison only. Web full graph has
  4 required open obligations; APK device/runtime remains unknown.
- Providers: `docs/PROVIDER-STATUS.md`; source IDs and distributions:
  `SOURCE-MANIFEST.json` and `components/official/manifest.json`. Craft is an
  interface-only reference; historical patch names are not distributed files.
- Reverse preservation: 603 source files with upstream/local digest and current
  adaptation reasons in `components/reverse-core/preservation.json`. RF-24's
  historical report is `docs/REVERSE-CAPABILITY-AUDIT.md`.
- Normal development does not require reverse tasks. Analysis subcases need
  route/Evidence/conclusions; reconstruction adds frozen tasks and the complete
  candidate acceptance chain. Restore required reads and isolation on resume.
- Rollback: `docs/ROLLBACK.md`; no transaction journal or automatic provider
  restore is implemented. Old installs and host runtime configuration stay outside
  this repository's write scope; the managed Codex adapter is removed by receipt.

RF-27 corrects gaps not covered by RF-26's local contract closure. The next action is a user target case or selective upstream
review. New observations can supersede historical results; never rewrite a
historical checkpoint to imply it measured a later checkout or host state.
