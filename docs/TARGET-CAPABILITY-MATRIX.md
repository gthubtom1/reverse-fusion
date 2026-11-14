# Target capability matrix

Reverse Fusion does not promise that every future target has been executed in
advance. It defines the route and evidence contract for each target family and
adds a representative fixture when a provider path is implemented.

| Family | Static route | Dynamic route | Current state | First real target gate |
|---|---|---|---|---|
| WASM | WABT `inspect_wasm_artifact`, interface comparison | WABT interpreter fixture only | verified for bounded fixture; ledger ready | retain original/candidate Evidence and runtime value comparison |
| JavaScript/Web | REA `analyze_javascript_application`, export-shape comparison | finite Node module replay | verified for reviewed export; static partial and package/parser unknowns retained | add browser/CDP authority when a page target requires it |
| Electron | REA Electron page/scenario tools | owned Electron scenario | contract planned | one local Electron fixture |
| PE/.NET | REA managed artifact/member inspection and exact comparison | .NET 8 command-line replay | verified for bounded managed method; ledger ready | extend with native/obfuscation probes when supplied |
| APK/DEX | REA Android package/class inspection through pinned JADX headless MCP | adb/emulator/Frida provider-dependent | static verified; Android runtime unknown on this host; ledger ready | rerun with a qualified device/emulator provider |
| Native ELF/PE | native layout/hardening/disassembly tools | PTY/debug provider-dependent | Windows PTY unsupported currently | Linux/macOS provider or qualified Windows cleanup provider |
| Protocol/API | packet/HAR/static contract tools | capture/replay provider-dependent | contract planned | one local fixture capture |

The matrix is a routing and contract inventory. A target-level claim still
requires the Evidence and comparison for that target.
