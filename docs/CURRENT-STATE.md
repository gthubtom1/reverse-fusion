# Current State

Stage: RF-12
Status: vertical-wasm-chain-verified; final-v1-gates-in-progress

Completed:

- Single-repository skeleton.
- Official component manifest.
- Versioned contract schemas.
- Static `contracts`, `plan`, `doctor`, and `handoff` commands.
- `python -m reverse_fusion` module entry.
- Four profiles.
- Craft bounded boundary documentation.
- Six contract and vertical-slice unit tests pass.
- Native reverse router dry-run bridge is available without a second routing table.
- Official REA evidence/bundle, project-local Spec pointer, and bounded Craft candidate contracts are implemented.
- Console vertical slice proves correct pass, intentionally wrong fail, and missing-evidence unknown.
- GitHub repository created and pushed: https://github.com/gthubtom1/reverse-fusion
- RF-05 Craft six-tool gate, baseline/path/task/model drift checks and cleanup-aware candidate contract.
- RF-06 official Spec Kit 1.4.0 check/init and project-local feature artifacts.
- RF-07 acceptance plane separated into specification, behavior comparison and runtime fields.
- RF-08 Codex/Pi/Claude host discovery without global configuration writes.
- RF-09 hard-target provider limitations recorded as unsupported/unverified.
- RF-10 release, rollback and upstream maintenance records updated.
- RF-11 reproducible WABT 1.0.42 environment and real REA WASM Evidence accepted.
- RF-12 real REA original/candidate Evidence plus correct/wrong/missing candidate acceptance path.

Not yet connected or intentionally unverified:

- REA Windows PTY process capture on this host.
- Qualified Craft R46 backend execution and real model build.
- Host loading/handshake and real target behavior.

Acceptance: RF-01 through RF-12 bounded gates and finite fixtures pass where the host supports them; final-v1 gates are defined in `docs/FINAL-COMPLETION-SPEC.md` and provider/runtime gaps remain in `docs/PROVIDER-STATUS.md`.

Next single action: when a real target is supplied inside an existing case, attach its original Evidence bundle and use the same bridge for an independent reconstruction feature.
