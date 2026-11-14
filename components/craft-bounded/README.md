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

项目同时提供 `local-bounded-worker` 作为仓库自有 fallback：它只把明确
选定的 fixture/source 写入一个安全的仓库相对路径，校验任务 digest、
baseline、single-writer 和 cleanup，并返回同一 typed candidate contract。
它用于可重复的离线验收，不冒充真实模型 Builder；有合格 Craft backend
时由原 runner 选择替换。
