# Provider and host status

Recorded 2026-11-14 for RF-05 through RF-16.

| Surface | Observed result | State | Next bounded action |
|---|---|---|---|
| Spec Kit | `specify 1.4.0`; `specify check` passed; Codex, Pi and Claude CLI detected | verified for CLI/init | use the project-local feature artifacts and run the official workflow when a real feature is supplied |
| REA process capture | Windows PTY provider returned `capability_unavailable` because descendant cleanup is not verified | unsupported on this host | run the same capture on Linux/macOS or a REA host with a qualified PTY provider |
| REA MCP runtime | repository-local official `rea-agents@6.9.0` package with pinned npm integrity; process-local `mcp doctor` passed: 255 tools, 6 prompts, catalog digest `2c725b48818ac5266198069330907c657f0fa2b6b8236065e5a191e20d95c2d7` | verified for local stdio handshake | provide a supported Node 22.23.4+/24.22.1+ path on a fresh host |
| REA WASM inspection | process-local `REA_WABT_BIN_DIRECTORY` pointed to pinned WABT 1.0.42; `inspect-wasm-artifact` returned `ev_d6ed8f580f5b6d7fb001de26c8b8b6732fd32308f8aeb6eeb624738209e35f96`, valid 39-byte artifact and export `answer: () -> i32` | verified for this fixture and toolchain | repeat with a real target Evidence bundle when supplied |
| REA reconstruction proof and obligation ledger | bounded WABT runner emitted `rea.reconstruction-proof` Evidence `ev_59a71030abee7eac0677de1b5282c8b7d709319c70e1a3074bf305c18ce43bec`; official ledger closure `rol_09e99625528899bcc2b492bdc7b2811b44fb573c13418ff80af0404548039928` | verified for the declared WASM obligation; `required_open: 0` | reuse the same proof contract for each real target's reviewed obligations |
| Craft companion | installed 0.6.1 MCP with `--all-tools`; setup doctor self-test passed, Codex registration reported a different command shape, and receipt says `native_r46_backend_qualified: false`; repository fallback `local-bounded-worker` passes its six-tool/single-writer/cleanup fixture | MCP tool companion is healthy; upstream R46 backend unsupported; local deterministic fallback verified | only accept a runner-selected qualified backend for model builds; fallback remains for reproducible offline candidates |
| Craft agent backend transport | Craft `0.6.1` `ai test Codex` returned the signed-in Codex version; `chat --backend Codex --clean-room` returned `RF_CRAFT_BACKEND_CODEX` with exit 0; temporary backend registration was removed and Craft config SHA-256 returned to `DF760044CAC114045B328CAEB0F1948AAD9BAB857C93982729360FA4310061B9` | verified for agent-cli transport; not a qualified native R46 bounded executor | keep native R46 qualification separate from agent-cli reachability; use the repository fallback until the bounded executor is installed |
| Host adapters | `scripts/run-host-handshakes.ps1` observed Codex `RF_HOST_HANDSHAKE_CODEX` and Pi `RF_HOST_HANDSHAKE_PI` with exit 0; Claude `2.1.310` started but returned `Not logged in · Please run /login` | Codex/Pi loading and handshake verified; Claude explicitly blocked by missing host credentials; all probe records set `config_mutation=false` | authenticate Claude on a future host, then rerun the same probe |

The status table is evidence about this machine and this session. It does not
claim that another computer has the same provider availability.
