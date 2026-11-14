# Context Handoff

Before ending a session or compressing context, update `docs/CURRENT-STATE.md` and create `checkpoints/RF-XX-YYYYMMDD-NNN.md`.

Record source identities, observed/inferred/unknown/designed facts, completed task IDs, current stage, next single action, blockers and rollback path. Do not rely on chat history to recover project state.

Current handoff (2026-11-14):

- Repository: https://github.com/gthubtom1/reverse-fusion, branch `master`.
- Stage: RF-16 final v1 accepted within declared boundaries; Codex/Pi host loading and Craft agent-cli transport are verified, while Claude login, process runtime and arbitrary real targets remain explicitly `blocked`, `unverified` or `unsupported` where recorded.
- Completed: contracts, source drift/path/hash checks, native route bridge, Craft six-tool gate plus local fallback writer, official Spec Kit init, typed REA/Spec/Craft adapters, lifecycle CLI, host discovery, reproducible local WABT/REA bootstrap and real REA original/candidate inspection.
- Provider record: see `docs/PROVIDER-STATUS.md`.
- Ledger closure: WASM proof Evidence `ev_59a71030abee7eac0677de1b5282c8b7d709319c70e1a3074bf305c18ce43bec`; ledger `rol_09e99625528899bcc2b492bdc7b2811b44fb573c13418ff80af0404548039928` is `ready` with `required_open: 0`.
- Fresh-clone release gate: remote `master` clone passed install preview, contracts, plan, doctor and handoff.
- Host probe: `scripts/run-host-handshakes.ps1` records Codex/Pi `pass` and Claude `blocked` with `config_mutation=false`.
- Craft probe: Codex agent-cli `ai test` and clean-room chat passed; native R46 qualification remains false and the user Craft config digest was restored.
- Next single action: attach a real case's Evidence bundle when a target is supplied and run the same reconstruction handoff.
- Rollback: revert the latest RF commit; old reverse-skill/installer/REA/Craft/Spec Kit and host configuration remain untouched.
