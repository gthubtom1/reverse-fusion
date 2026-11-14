# Context Handoff

Before ending a session or compressing context, update `docs/CURRENT-STATE.md` and create `checkpoints/RF-XX-YYYYMMDD-NNN.md`.

Record source identities, observed/inferred/unknown/designed facts, completed task IDs, current stage, next single action, blockers and rollback path. Do not rely on chat history to recover project state.

Current handoff (2026-11-14):

- Repository: https://github.com/gthubtom1/reverse-fusion, branch `master`.
- Stage: RF-04 accepted static slice; provider runtime and real target remain `unverified`.
- Completed: contracts, source drift/path/hash checks, native router dry-run bridge, REA/Spec/Craft typed adapters, lifecycle CLI and console pass/fail/unknown fixture.
- Next single action: attach a real case's Evidence bundle when a target is supplied, then run the original reconstruction handoff.
- Rollback: revert the latest RF commit; old reverse-skill/installer/REA/Craft/Spec Kit and host configuration remain untouched.
