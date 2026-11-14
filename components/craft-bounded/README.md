# Craft bounded adapter

上游 Craft Anything 0.6.1 不原生提供 AcceptedResearch/ExternalBaseline/bounded policy。

本目录未来保存：

- upstream identity。
- patch series identity。
- bundle manifest。
- host entry protocol。
- source/lock/toolchain requirements。
- update and rollback instructions。

当前仓库已经提供 `CraftAdapter.prepare()` / `run()` 的 typed boundary；没有
provider/backend 时返回 `unsupported`，有 backend 时返回带 cleanup 状态的
candidate。`bundle-manifest.json` 固定 upstream commit、四个 patch seam 和
single-writer/cleanup policy，并要求 `prepare/build/check/refine/return_summary/cleanup`
六项能力全部存在。当前 Codex companion 的安装回执明确记录
`native_r46_backend_qualified: false`，因此本仓库保留该 MCP 作为工具伴随，
由原 Spec runner 选择的合格 bounded backend 仍是后续运行时门。
