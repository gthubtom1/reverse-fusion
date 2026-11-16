# Pinned original Craft MCP launcher

This thin Rust entry uses the fixed upstream `craft-anything-mcp::serve_stdio`
and `craft-anything-engine` implementation at
`8374ad71544f2cc44698ea74ef990aa31600bac6` (Craft 0.6.1). It exposes the upstream
MCP protocol and tools, alongside the separate bounded native implementation
lease. It does not replace that lease, start another model, or run a Study loop.

The 0.1.1 launcher adds `fusion_case_open(project_root, case_root)` with existing
absolute outcome directories. It creates/reopens `craft-analysis.cany` inside
that case using the original analysis `Project`, not a second candidate build.
Analysis and investigation updates refuse unbound use; diagnostics and provider
setup remain available. Evidence/unknowns, investigation memory, annotations,
target identities and journal persist in the selected case. A fresh Session on
case switch prevents merging the previous case's records. Changed/missing
targets are reported and retained separately without blocking saved research.
The fixed baseline is 303 upstream engine tools plus the two owned binding/asset staging tools;
runtime plugins can add tools. Binding does not bypass Spec/native writer leases.

The installed host registration runs the repository venv's Python
`scripts/mcp-launch.py craft`. It resolves this manifest's versioned binary,
restores the same saved allowlisted provider paths used by the official REA
CLI/MCP, inherits stdio without rewriting protocol messages, and owns the server
process tree. Refresh existing paths with `reverse_fusion providers --refresh`;
explicit choices use `--set-path KEY=absolute-path`. No shell profiles, arbitrary
environment import, global Craft settings or credentials are read to recover
these paths. A configured path is not successful provider execution.

The binary receives `--all-tools`,
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
`REVERSE_FUSION_CRAFT_TOOL_<ID>` (upper-case tool id) supplies an existing absolute
provider executable selected by the owned runtime resolver. That explicit
selection overrides saved Craft settings for this run and does not mutate
the user's original settings. MCP plugins are supported. WASM component plugins
remain the optional upstream compile feature and are not compiled in this build.

The analysis Project does not create a build Inbox/Workspace. The reviewed native
lease supplies those for actual build/write/edit/check operations. User questions,
permission choices, progress and refinement are handled by the current host and
official Spec/native workflow rather than the original GUI or another AI loop.
`fusion_asset_generate` calls the original `assets_image_generate` or
`assets_model_generate` and original fal.ai/Tripo P1 HTTP producer in a fresh
`<bound case>/asset-staging/asset*/` Workspace/Inbox. Each call explicitly supplies
kind, relative PNG/GLB save_as, budget_usd and host-confirmed allow_paid; the only
credential source is `REVERSE_FUSION_CRAFT_FAL_KEY` in the server environment,
never tool parameters, logs, receipts or old keychains. Listed over-budget requests
fail before network use. Original costs/errors are retained with key echoes
redacted. Results include staged files/digests; reviewed Spec/native commands
integrate them into the formal candidate. The asset tool never edits that candidate.
Host image generation is an image alternative, not a 3D connector.

`scripts/qualify-craft-assets.py` runs actual original tools and the Fal HTTP
producer against explicit loopback `--asset-test-base`. That maintainer-only
transport uses a synthetic key and never reads a real credential. Default host
registrations never pass it; production retains the upstream official HTTPS
endpoint. Image and model fixtures, budget/path/permission refusals, original
error handling, key redaction and candidate fixity are exercised. No paid
generation or real service quality claim was made by this qualification.

The default `scripts/bootstrap-craft-mcp.ps1` downloads the manifest-pinned
Windows x64 archive. It verifies archive, executable, complete third-party
notice and dependency inventory SHA-256 identities, calls `--version`, and
writes only this checkout's `state/craft-mcp-runtime.json`. The archive has three
flat entries: executable, `THIRD-PARTY-NOTICES.txt`, `dependency-notices.json`.
It does not register host configuration by itself.

For a maintainer source build, pass `-BuildFromSource` and explicit Cargo/Rustc/
GNU toolchain paths as needed. Source HEAD, allowed upstream patch and patched
file identities are checked before `cargo build --release --locked`. MCP uses
its own `vendor/craft/mcp-upstream` checkout so its binding/diagnostic patch cannot
alter the existing native writer's source tree or published binary. The source
and binary receipt stay separate from original-target behavior acceptance.

After qualification, set `RF_CARGO` to the direct Cargo executable and
`RF_MINGW_LICENSES` to the build toolchain's license directory, then run the
repository venv's `scripts/package-craft-mcp.py`. The package contains license
texts for every resolved dependency plus GCC/MinGW runtime notices and an exact
dependency inventory. Packaging binds wrapper source/Cargo.lock and updates
manifest asset hashes; it never uploads a release or modifies native adapter
packaging. Release tag: `craft-mcp-v0.1.1-rf36`.

Run `scripts/qualify-craft-memory.py --output <new-directory>` to execute owned
bind/analysis/brief/finding/handoff/annotation/journal, restart and case-isolation
checks against the actual binary. It also keeps changed targets separate and
checks that effective Deep mode matches the session's process override.

Recorded finite results: [Craft recovery](../../evidence/rf36/craft-memory-report.json)
and [raw calls](../../evidence/rf36/craft-memory-calls.json). Shared-provider
qualification is recorded separately in [REA provider report](../../evidence/rf36/provider-report.json),
[calls](../../evidence/rf36/provider-calls.json), and
[original evidence bundle](../../evidence/rf36/provider-bundle.json).
Asset wiring evidence is in [asset report](../../evidence/rf36/craft-assets-report.json)
and [calls](../../evidence/rf36/craft-assets-calls.json).
The 305-tool catalog and these finite results do not assert that every provider,
device or original GUI capability is ready. Full responsibility mapping is in
[the integration contract](../../docs/INTEGRATION-CONTRACT.md).
