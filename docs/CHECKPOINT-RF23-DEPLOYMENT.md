# RF-23 Deployment Checkpoint (historical)

Date: 2026-11-15

Repository: `https://github.com/gthubtom1/reverse-fusion`

This checkpoint records the Codex workspace deployment after the RF-23 product
commit. RF-24 was the release when this record was written; current status is
in `CURRENT-STATE.md` and the RF-25 checkpoint. This file remains the historical
deployment record referenced by the RF-23 audit:

- `scripts/install.ps1 -Python python` created the repository-local `.venv`.
- `reverse_fusion install --apply --client codex --format json` wrote only
  `state/install.json` and reported `global_config_mutation: false`.
- `scripts/run-host-handshakes.ps1` observed real sentinel responses from Codex
  and Pi. Claude started but reported its missing-login boundary as `blocked`.
  Known host configuration hashes were equal before and after every probe.
- `reverse_fusion plan --client codex --intent normal-dev`, `doctor`,
  `handoff --check`, and `contracts` passed. Doctor now reads the handshake
  record on Windows PowerShell output with or without a UTF-8 BOM.
- A live Codex host-owned Builder run in an ignored repository-local state
  workspace produced a candidate and passed `prepare`, `build`, `check`,
  `refine`, `return_summary`, and `cleanup`; its host configuration snapshot
  remained unchanged and no model was selected by the repository.
- The focused Python suite passes all 18 tests, including the BOM compatibility
  check. The generated `.venv`, `state/`, caches and candidate workspace remain
  ignored and are not part of the GitHub product.

The portable installation contract remains the repository URL plus the commands
in `docs/DEPLOYMENT-GUIDE.md`; no fixed local path or model is part of the
contract. Claude authentication, native Craft R46 qualification, Windows REA
PTY cleanup and Android device runtime remain host capability boundaries.
