# Context Handoff

Before ending a session or compressing context, update
`docs/CURRENT-STATE.md` and create a new checkpoint. Never recover project
state from chat history alone.

Current handoff (2026-11-15, RF-23):

- Repository: https://github.com/gthubtom1/reverse-fusion, branch `master`.
- Status: `reconstruction-product-v1-final`; RF-17 portable route, RF-18 real
  host-owned Builder, RF-19 Web, RF-20 PE/.NET, RF-21 APK/DEX and RF-22 release
  acceptance plus RF-23 independent-audit hardening are closed. Local domain
  skills live under `skills/`; normalized representative Evidence lives under
  `evidence/rf22/`.
- Representative ledgers: WASM
  `rol_09e99625528899bcc2b492bdc7b2811b44fb573c13418ff80af0404548039928`;
  Web `rol_39c38b659a45e5b080c5dc55870f154eb17b9e484fb998aacba88d07cd579c48`;
  .NET `rol_53dd8e6683c0351977afc491a5c50863e56a390e5925d0c6d63fde1372bebba9`;
  APK `rol_b9833a0dd114ad263d96217960a2990d87c9e3629048488d3f4f2379f93762b`.
  All four reviewed ledgers report `required_open: 0`.
- Host record: Codex/Pi fixed-sentinel handshakes pass; Claude is explicitly
  blocked by missing login. Codex generated the APK candidate and completed all
  six Builder checks, including refine and cleanup.
- Provider record: `docs/PROVIDER-STATUS.md` records Craft native R46,
  Windows PTY, Web static unknowns and Android runtime unknowns separately.
- Product contract and continuation prompt: `docs/PRODUCT-GOAL.md` and
  `docs/HANDOFF-PROMPT.md`.
- Next single action: perform a read-only upstream review or open a new target
  case; do not rewrite the closed RF-17–RF-23 evidence.
- Rollback: revert the latest RF-23 repository commit(s); old reverse-skill,
  installer, REA/Craft/Spec Kit and host configuration remain untouched.
