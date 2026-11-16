# Pinned original Craft MCP launcher

This thin Rust entry uses the fixed upstream `craft-anything-mcp::serve_stdio`
and `craft-anything-engine` implementation at
`8374ad71544f2cc44698ea74ef990aa31600bac6` (Craft 0.6.1). It exposes the upstream
MCP protocol and tools, alongside the separate bounded native implementation
lease. It does not replace that lease, start another model, or run a Study loop.

Start through the installed host MCP registration with `--all-tools`,
`--deep-mode`, `--allow-run` and an absolute checkout-owned `--state-dir`.
Deep mode applies only to this server process and does not change global
settings. `--allow-run` preserves the original MCP server's external-host
consent semantics: the host must enforce the user's actual permission scope;
without the flag, upstream run refusal remains. Automatic GUI mode stays off.
Provider availability still applies; a visible catalog is not a guarantee that
every browser/device/provider is installed or that a target action is authorized.

Provider/plugin settings are restored from this MCP state's `config.toml` on
restart; no old global Craft settings are read. Engine caches and the default
project directory remain under this state's `engines/` and `projects/` paths.
The host still supplies explicit absolute outcome-project paths for actual
work. Auto mode stays disabled after loading settings; Deep remains a per-run
flag. Original engine tools/plugins are loaded through upstream installation.

The default `scripts/bootstrap-craft-mcp.ps1` downloads the manifest-pinned
Windows x64 archive. It verifies archive, executable, complete third-party
notice and dependency inventory SHA-256 identities, calls `--version`, and
writes only this checkout's `state/craft-mcp-runtime.json`. The archive has three
flat entries: executable, `THIRD-PARTY-NOTICES.txt`, `dependency-notices.json`.
It does not register host configuration by itself.

For a maintainer source build, pass `-BuildFromSource` and explicit Cargo/Rustc/
GNU toolchain paths as needed. Source HEAD, allowed upstream patch and patched
file identities are checked before `cargo build --release --locked`. The source
and binary receipt stay separate from original-target behavior acceptance.

After qualification, set `RF_CARGO` to the direct Cargo executable and
`RF_MINGW_LICENSES` to the build toolchain's license directory, then run the
repository venv's `scripts/package-craft-mcp.py`. The package contains license
texts for every resolved dependency plus GCC/MinGW runtime notices and an exact
dependency inventory. Packaging binds wrapper source/Cargo.lock and updates
manifest asset hashes; it never uploads a release or modifies native adapter
packaging. Release tag: `craft-mcp-v0.1.0-rf35`.
