# Final v1 release acceptance

Recorded 2026-11-14 after commit `5de732c` was pushed to
`https://github.com/gthubtom1/reverse-fusion`.

The release is accepted within the capability boundaries in
`FINAL-COMPLETION-SPEC.md`. It is a portable framework release, not a claim
that every future target has already been analyzed or rebuilt.

| Gate | Evidence | Result |
|---|---|---|
| Fresh clone | Remote clone `fresh-clone-rf14-825a008ce5634ea7803bb85f825eb789`; `install.ps1 -DryRun`, `contracts`, `plan`, `doctor`, `handoff` | pass |
| Single route owner | Reverse native router dry-run returned `skills/reconstruction/SKILL.md`; bridge owner is `reverse.native-router` | pass |
| Official identities | `SOURCE-MANIFEST.json`, `components/official/manifest.json`, REA `6.9.0`, Spec Kit `1.4.0`, Craft `0.6.1` | pass |
| REA Evidence chain | Original `ev_d6ed8f...`, candidate `ev_85ebdc...`, interface comparison `ev_7feb49...` | pass |
| Obligation closure | Proof `ev_59a710...`; ledger `rol_09e996...`; closure digest `eb14c2...`; `required_open=0` | pass |
| Spec Kit | Project-local `.specify`, `spec.md`, `plan.md`, `tasks.md`, `converge.md` | pass |
| Craft builder | `local-bounded-worker`; six-tool gate, single writer, digest and cleanup all pass | pass within fallback boundary |
| Host loading and handshake | `run-host-handshakes.ps1`: Codex and Pi returned fixed sentinels with exit 0; Claude started and returned the typed missing-login result | Codex/Pi pass; Claude blocked by missing credentials, explicitly recorded |
| Craft backend transport | Craft `ai test Codex` and clean-room `chat --backend Codex` returned exit 0 and the fixed backend sentinel; Craft config hash restored to its pre-probe value | pass for agent-cli transport; native R46 bounded executor remains unqualified |
| Target matrix | WASM verified; JavaScript/Web, Electron, PE/.NET, APK/DEX, Native and Protocol/API boundaries recorded | pass within declared matrix |
| Three-state acceptance | WASM correct=`pass`, wrong=`fail`, missing=`unknown`; console slice has the same three states | pass |
| Maintenance and rollback | Source drift tests, rollback record, upstream maintenance policy and context handoff | pass |
| Repository consistency | `10` Python tests passed, contracts passed, `git diff --check` passed, remote master contains the release commit | pass |

## Provider boundaries retained

- Windows REA PTY process capture is recorded as unsupported because descendant
  cleanup is not qualified on this host.
- The installed Craft companion is healthy as an MCP companion, and its Codex
  agent-cli transport was exercised. Its receipt still does not qualify a
  native R46 model backend, so the repository fallback remains deterministic
  and explicit.
- Codex and Pi host loading/handshake are verified by fixed-sentinel probes.
  Claude loading reaches the CLI but is blocked by the missing host login/API
  credential. A future authenticated host can rerun the same probe.
- Arbitrary real-target behavior still requires a target and a provider with
  the required capability.

These boundaries are part of the release contract. A future target closes its
own case by attaching original Evidence, freezing Spec Kit tasks, selecting a
qualified Builder or the bounded fallback, and running the same comparison,
proof and obligation-ledger path.
