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
single-writer/cleanup policy。真实 bundle 执行仍由原 Spec runner 在满足能力门后选择。
