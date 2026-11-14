# Context Handoff

Before ending a session or compressing context, update `docs/CURRENT-STATE.md` and create `checkpoints/RF-XX-YYYYMMDD-NNN.md`.

Record source identities, observed/inferred/unknown/designed facts, completed task IDs, current stage, next single action, blockers and rollback path. Do not rely on chat history to recover project state.

Current handoff (2026-11-14):

- Repository: https://github.com/gthubtom1/reverse-fusion, branch `master`.
- Stage: RF-11 accepted REA WASM Evidence slice; process runtime and real target remain partially `unverified`.
- Completed: contracts, source drift/path/hash checks, native route bridge, Craft six-tool gate, official Spec Kit init, typed REA/Spec/Craft adapters, lifecycle CLI, host discovery, reproducible WABT bootstrap and real REA WASM inspection.
- Provider record: see `docs/PROVIDER-STATUS.md`.
- Next single action: attach a real case's Evidence bundle when a target is supplied, then run the original reconstruction handoff.
- Rollback: revert the latest RF commit; old reverse-skill/installer/REA/Craft/Spec Kit and host configuration remain untouched.
