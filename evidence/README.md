# 执行记录与历史证据

RF35当前MCP修复证据：`rf35/tool-qualification.json`、原始`*-mcp-calls.json`、工具目录、配置保全、provider设置重启恢复、source-bound回归。旧RF33/34记录不是MCP宿主登记证明。

本目录保存**当时实际发生的观察**，不提供当前安装命令或未完成任务。当前版本、
宿主适配和部署步骤以[当前状态](../docs/CURRENT-STATE.md)、
[唯一安装入口](../docs/AGENT-BOOTSTRAP.md)和[宿主接入合同](../docs/HOST-PROJECT-CONNECTION.md)为准。

| 记录 | 作用与时间边界 |
|---|---|
| `deployment/`、`rf22/` | RF-25及早期有限代表材料与工具观察；目录名为保持身份链接而保留 |
| `rf28/`、`rf29/` | 真实组件交接、白话入口失败与修复的阶段记录 |
| `rf30/`、`rf31/` | 1.1.0/1.1.1工程交付与新克隆安装的历史记录 |
| `rf33/owned-desk-completion.json` | Codex普通请求下完整自有应用交付及精确归档索引 |
| `rf33/pi-full-use.json`、`pi-owned-desk.zip` | Pi完整运行、期限退出后恢复与最终交付；ZIP为原始字节快照 |
| `rf33/clean-install.json` | 明确提交上的全新克隆默认安装，不能冒充最新提交或另一台物理电脑实测 |
| `rf33/product-tests.txt`、`reconstruction-tests.txt`、`verification-before-rf34.json` | RF-33收尾前的工程资格与日志快照；保留原来的源码绑定 |
| `rf34/` | 当前最终文件收尾覆盖、静态检查与对应工程资格；当前`release/verification.json`指向此处日志 |
| `rf33/deployment-final.json` | 收尾前最后一次部署检查快照；不是另一台电脑的安装记录 |
| `rf33/release-*.json`、`doctor*.json`、`handoff*.json` | 各次检查快照；`final`与非`final`不是需要合并或改写的重复配置 |
| `rf33/claude-*.json` | 当时未登录状态和可选运行准备；不表示Claude适配未完成，不要求继续轮询登录 |

Evidence ID、来源摘要、旧绝对路径、原始错误、`partial/unknown/blocked`和负对照的
`fail`必须原样保留。它们既不是当前部署配置，也不能为了“清理旧东西”改成通过。
候选里的HTML/JS/启动器是测试/交付快照，不能作为共享工具的当前实现去编辑。
ZIP中的路径和session记录用于追溯，不是可在新电脑直接恢复执行的活动租约。

最终静态收尾的覆盖清单与结论见[收尾报告](../docs/FINAL-CLOSEOUT.md)。
