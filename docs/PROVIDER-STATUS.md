# Provider and host status

Recorded 2026-11-14 for RF-05 through RF-11.

| Surface | Observed result | State | Next bounded action |
|---|---|---|---|
| Spec Kit | `specify 1.4.0`; `specify check` passed; Codex, Pi and Claude CLI detected | verified for CLI/init | use the project-local feature artifacts and run the official workflow when a real feature is supplied |
| REA process capture | Windows PTY provider returned `capability_unavailable` because descendant cleanup is not verified | unsupported on this host | run the same capture on Linux/macOS or a REA host with a qualified PTY provider |
| REA MCP runtime | repository-local official `rea-agents@6.9.0` package with pinned npm integrity; process-local `mcp doctor` passed: 255 tools, 6 prompts, catalog digest `2c725b48818ac5266198069330907c657f0fa2b6b8236065e5a191e20d95c2d7` | verified for local stdio handshake | provide a supported Node 22.23.4+/24.22.1+ path on a fresh host |
| REA WASM inspection | process-local `REA_WABT_BIN_DIRECTORY` pointed to pinned WABT 1.0.42; `inspect-wasm-artifact` returned `ev_d6ed8f580f5b6d7fb001de26c8b8b6732fd32308f8aeb6eeb624738209e35f96`, valid 39-byte artifact and export `answer: () -> i32` | verified for this fixture and toolchain | repeat with a real target Evidence bundle when supplied |
| Craft companion | installed 0.6.1 MCP with `--all-tools`; setup doctor self-test passed, Codex registration reported a different command shape, and receipt says `native_r46_backend_qualified: false`; repository fallback `local-bounded-worker` passes its six-tool/single-writer/cleanup fixture | MCP tool companion is healthy; upstream R46 backend unsupported; local deterministic fallback verified | only accept a runner-selected qualified backend for model builds; fallback remains for reproducible offline candidates |
| Host adapters | Codex, Pi and Claude executables detected by repository-local discovery | verified for discovery only | each host still needs a real loading/handshake check |

The status table is evidence about this machine and this session. It does not
claim that another computer has the same provider availability.
