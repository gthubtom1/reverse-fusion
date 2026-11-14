# Target capability matrix

Reverse Fusion does not promise that every future target has been executed in
advance. It defines the route and evidence contract for each target family and
adds a representative fixture when a provider path is implemented.

| Family | Static route | Dynamic route | Current state | First real target gate |
|---|---|---|---|---|
| WASM | WABT `inspect_wasm_artifact`, interface comparison | WABT interpreter fixture only | verified for fixture | retain original/candidate Evidence and runtime value comparison |
| JavaScript/Web | REA web bundle/static endpoint tools | CDP/browser capture when available | contract planned | one local page with static and observed endpoint pair |
| Electron | REA Electron page/scenario tools | owned Electron scenario | contract planned | one local Electron fixture |
| PE/.NET | managed/native artifact inspection | provider-dependent | contract planned | one local managed sample and member comparison |
| APK/DEX | APK/Android static tools | device/Frida provider-dependent | contract planned | one offline APK fixture |
| Native ELF/PE | native layout/hardening/disassembly tools | PTY/debug provider-dependent | Windows PTY unsupported currently | Linux/macOS provider or qualified Windows cleanup provider |
| Protocol/API | packet/HAR/static contract tools | capture/replay provider-dependent | contract planned | one local fixture capture |

The matrix is a routing and contract inventory. A target-level claim still
requires the Evidence and comparison for that target.
