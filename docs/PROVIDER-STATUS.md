# Provider and host status

Recorded 2026-11-15 for RF-17 through RF-22. These observations describe this
host and do not claim identical provider availability on another computer.

| Surface | Observed result | State | Boundary or next action |
|---|---|---|---|
| Repository-owned Reverse router | `bridge --source local` resolves fixed `routing.json` and local `routes/R*.md` without an old receipt; Web=`R3`, PE/.NET=`R5`, APK/DEX=`R1` | verified | carry the selected route into each new target case |
| Spec Kit | `specify 1.4.0`, project-local artifacts and reconstruction task files | verified | keep feature tasks and converge records append-only |
| REA MCP runtime | official `rea-agents@6.9.0`, pinned integrity, process-local doctor passed | verified | bootstrap a supported Node 22.23.4+/24.22.1+ path on a fresh host |
| WABT/REA WASM | WABT `1.0.42`; original/candidate/comparison/proof; ledger `rol_09e99625528899bcc2b492bdc7b2811b44fb573c13418ff80af0404548039928`, `required_open=0` | verified for bounded fixture | reuse proof contract for future WASM cases |
| REA Web/JavaScript | original `ev_d42bef240bdf9e48b3444a5bb947adcc5bb30257a8e492115e421e9cac1e3955`, candidate `ev_ff3486e9a5d5cb34105392e5bdfbb2388d416d8c2028ab75ad8ecad4eaa55ed1`, runtime proof and ledger `rol_39c38b659a45e5b080c5dc55870f154eb17b9e484fb998aacba88d07cd579c48` | verified for reviewed export; static partial | package/parser obligations remain explicit unknown scope |
| REA PE/.NET | original/candidate managed artifacts and members, exact comparison, four runtime traces; ledger `rol_53dd8e6683c0351977afc491a5c50863e56a390e5925d0c6d63fde1372bebba9` | verified for bounded method | build larger managed targets with the same exact-signature contract |
| JADX/REA APK/DEX | official `jadx-headless-mcp@0.7.1` downloaded only by `bootstrap-jadx.ps1`, SHA-256 `6e5eacf500b64292bfb73c49797c1958f6ee44646e43e868039ae7feb573ff75`; static package/class comparison; ledger `rol_b9833a0dd114ad263d96217960a2990d87c9e3629048488d3f4f2379f93762b` | static verified; Android runtime unknown | rerun with adb/emulator to close runtime boundary |
| REA process capture | Windows PTY provider returned `capability_unavailable` because descendant cleanup is not verified | unsupported on this host | use Linux/macOS or a qualified Windows PTY provider |
| Craft companion | upstream 0.6.1 MCP retains required `--all-tools`; native R46 backend receipt remains unqualified | companion healthy; native backend unsupported | keep host-owned Builder as the real model transport; fallback is offline-only |
| Host-owned Builder | Codex generated APK candidate; six checks `prepare/build/check/refine/return_summary/cleanup` pass, no `--model`, `config_mutation=false` | verified for this case | use host-provided current model/provider; never select one in the repository |
| Host handshakes | Codex and Pi fixed sentinels pass; Claude CLI starts and returns missing-login boundary | Codex/Pi verified; Claude blocked | authenticate Claude on a future host and rerun the read-only probe |

All provider failures, login gaps and device gaps remain typed as
`blocked`, `unsupported` or `unknown`; none is converted into business
acceptance by exit code or tool visibility.
