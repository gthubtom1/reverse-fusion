# Craft bounded adapter

上游 Craft Anything 0.6.1 不原生提供 AcceptedResearch/ExternalBaseline/bounded policy。

本目录保存接口身份与边界：

- upstream identity。
- 四个历史 patch 名称的参考身份；本仓库没有分发可重放的 native patch bundle。
- bundle manifest。
- host entry protocol。
- source/lock/toolchain requirements。
- update and rollback instructions。

当前仓库已经提供 `CraftAdapter.prepare()` / `run()` 的 typed boundary；没有
provider/backend 时返回 `unsupported`，有 backend 时返回带 cleanup 状态的
candidate。`bundle-manifest.json` 固定 upstream 参考 commit、四个历史 patch seam 和
single-writer/cleanup policy，并要求 `prepare/build/check/refine/return_summary/cleanup`
六项能力全部存在。`companion_reference` 是用户声明的历史 companion 身份，
不作为当前安装或健康回执；保留其 `--all-tools` 参数。当前未观测到活动回执/注册，
native R46 backend 资格仍为 unsupported。

默认编码者是当前对话中已经运行的宿主 agent。`reverse_fusion session prepare`
冻结任务、研究文件和写入白名单；当前宿主使用自身工具实现，`session check/refine/finish`
记录边界观察。它不新开账号或模型，文件通过也不等于业务通过。`build --host ...`
是可选的 CLI transport；额度、登录或工具缺失保留 blocked，不转成候选成功。

项目同时提供 `local-bounded-worker` 作为仓库自有 fallback：它只把明确
选定的 fixture/source 写入一个安全的仓库相对路径，校验任务 digest、
baseline、single-writer 和 cleanup，并返回同一 typed candidate contract。
它用于可重复的离线验收，不冒充真实模型 Builder；有合格 Craft backend
时由原 runner 选择替换。
