# Craft bounded contract and compatibility adapter

本目录保存历史 typed candidate contract 与当前原生执行器的共同边界。
`bundle-manifest.json` 固定上游身份、实际可重放的 Windows 命令补丁、
single-writer/cleanup policy，以及六项生命周期能力。

当前复刻实现入口是实际 Craft engine adapter，身份和分发见
[原生清单](../craft-native/manifest.json)，操作见
[真实组件交接](../../docs/NATIVE-COMPONENTS.md)。当前宿主提供推理和内容，
通过 `native-craft prepare/build/check/refine/return_summary/cleanup` 执行真实
Workspace、候选写入/编辑与冻结检查。`session` 仅附加观察边界，不能替代原生
写入、检查和清理；直接编辑候选或离线复制也不算实际 Craft 执行。

`CraftAdapter.prepare()` / `run()` 保留 typed boundary 供兼容与合同检查使用。
`local-bounded-worker` 仅将明确选择的自有 fixture/source 复制到受限相对路径，
用于可重复离线合同检查；它不调用模型，不替代当前真实原生执行器或业务验收。
`build --host ...` 是可选子 CLI transport，不是默认当前会话实现入口；账号、
额度或工具缺失按实际结果报告。

清单中的 `historical_patch_series` 和 `companion_reference` 是历史身份记录，
不是当前原生 adapter 的安装/健康状态。历史 companion 的未观测或 unsupported
状态不能覆盖当前 adapter 的实际安装记录；保留其 `--all-tools` 参数。组件可用、
候选文件存在或生命周期结束均不等于原版行为比较已经通过。
