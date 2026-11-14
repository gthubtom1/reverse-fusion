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
| Host plans | Codex, Pi and Claude discovered by repository-local adapter; no global config mutation | pass for discovery; loading remains separately unverified |
| Target matrix | WASM verified; JavaScript/Web, Electron, PE/.NET, APK/DEX, Native and Protocol/API boundaries recorded | pass within declared matrix |
| Three-state acceptance | WASM correct=`pass`, wrong=`fail`, missing=`unknown`; console slice has the same three states | pass |
| Maintenance and rollback | Source drift tests, rollback record, upstream maintenance policy and context handoff | pass |
| Repository consistency | `10` Python tests passed, contracts passed, `git diff --check` passed, remote master contains the release commit | pass |

## Provider boundaries retained

- Windows REA PTY process capture is recorded as unsupported because descendant
  cleanup is not qualified on this host.
- The installed Craft companion is healthy as an MCP companion, but its receipt
  does not qualify a native R46 model backend. The repository fallback remains
  deterministic and explicit.
- Host loading/handshake and arbitrary real-target behavior are reported as
  unverified until a target and a provider with the required capability are
  supplied.

These boundaries are part of the release contract. A future target closes its
own case by attaching original Evidence, freezing Spec Kit tasks, selecting a
qualified Builder or the bounded fallback, and running the same comparison,
proof and obligation-ledger path.
