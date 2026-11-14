# Provider and host status

Recorded 2026-11-14 for RF-05 through RF-10.

| Surface | Observed result | State | Next bounded action |
|---|---|---|---|
| Spec Kit | `specify 1.4.0`; `specify check` passed; Codex, Pi and Claude CLI detected | verified for CLI/init | use the project-local feature artifacts and run the official workflow when a real feature is supplied |
| REA process capture | Windows PTY provider returned `capability_unavailable` because descendant cleanup is not verified | unsupported on this host | run the same capture on Linux/macOS or a REA host with a qualified PTY provider |
| REA WASM inspection | provider returned `directory_not_absolute` for `REA_WABT_BIN_DIRECTORY`; no WABT tools are registered | unverified | supply one absolute WABT 1.0.42-compatible directory through the official installation path |
| Craft companion | installed 0.6.1 MCP with `--all-tools`; setup doctor self-test passed, Codex registration reported a different command shape, and receipt says `native_r46_backend_qualified: false` | MCP tool companion is healthy; R46 bounded backend unsupported | only accept a runner-selected qualified backend with six capabilities and cleanup evidence |
| Host adapters | Codex, Pi and Claude executables detected by repository-local discovery | verified for discovery only | each host still needs a real loading/handshake check |

The status table is evidence about this machine and this session. It does not
claim that another computer has the same provider availability.
