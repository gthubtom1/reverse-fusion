# Codex 跨项目接入

Reverse Fusion 的路由器和领域资料保留在当前 checkout。Codex 选择为 selected host 时，
`reverse_fusion install --apply --client codex` 另外写入以下用户级接入：

- `~/.agents/skills/reverse-fusion/SKILL.md`：说明何时启用 Reverse Fusion，以及如何调用
  当前 checkout 的 `.venv` 路由器。
- `~/.codex/AGENTS.md`（设置 `CODEX_HOME` 时使用该目录）中的 `reverse-fusion:begin/end` 标记块：要求涉及逆向、保护分析、
  协议复刻或行为重建的任务先使用这个技能。

另在`~/.codex/config.toml`（遵循`CODEX_HOME`）中登记`reverse-fusion-rea`与
`reverse-fusion-craft`。管理自有标记块，保留无关设置；原版工具、Deep模式和宿主权限见
[MCP接入](MCP-INTEGRATION.md)。运行`mcp-check`核实真实stdio协议和工具，客户端重载后
再核实界面/工具发现。配置落盘不是当前聊天已加载。卸载同时移除本checkout的自有MCP项，
旧checkout不能删除新checkout指针。

REA/Craft登记命令经仓库Python启动器恢复已保存的分析器路径，避免Codex启动时的
旧环境漏掉后来准备的Ghidra/Java等工具。`providers --refresh`保存当前有效选择，
`mcp-check`会在清除终端临时provider变量的环境里重新连接，核对所选工具的可达状态。
Craft分析先绑定成果项目case；重启恢复原版Project，不能把共享工作目录当成果目录。

技能与指引只保存 checkout 路径和调用规则，不复制 `skills/` 正文，不选择模型，不启动
provider，也不改变当前项目的工作目录。模型在普通软件开发任务中仍走 `host-native`；
进入 Reverse Fusion 时先运行：

```text
Windows: [checkout]\.venv\Scripts\python.exe -m reverse_fusion bridge --source local --case-root work/current-case --hint "[用户原话]" --record
POSIX:   [checkout]/.venv/bin/python -m reverse_fusion bridge --source local --case-root work/current-case --hint "[用户原话]" --record
```

然后读取返回的 `workflow`、`skill`、`required_reads`、`related_routes`、`next_stage`、
`hard_target` 和 `missing_support`。
首次保存原始要求，识别技术后细化同一 case_root；最终 objective 与当前 stage 分开。
已有案例按实际路径恢复。先只读探路后首次落盘时加 `--user-request "[用户原话]"`。

完整的跨项目交接见 [CROSS-PROJECT-WORKFLOW.md](CROSS-PROJECT-WORKFLOW.md)。任务命令
使用 `--project-root` 指向当前软件项目，省略时使用当前目录；不得为了调用共享工具切换到
工具仓库后再隐式保存 case。`required_read_paths` 指向共享技能资料，输出与 session 留在
成果项目。一次路由成功不等于 REA、Spec、Craft 或 Builder 已执行。

## 安装和卸载

先通过默认 `scripts/install.ps1` 或 `scripts/bootstrap-core.ps1` 安装真实 REA、Spec Kit、
Craft。缺任何核心组件，CLI 都拒绝把适配层标为完整安装。真实工作流与平台范围见
[NATIVE-COMPONENTS.md](NATIVE-COMPONENTS.md)。Codex 安装再启用适配层：

```text
[venv-python] -m reverse_fusion install --apply --client codex
```

只想保留仓库本地运行时，可以使用 `--no-global-adapter`。receipt 会在
`state/install.json` 中记录适配层路径和 `enabled` 状态。`uninstall --apply` 和仓库的
卸载脚本会删除本次安装管理的技能文件和标记块，并保留全局 `AGENTS.md` 中其他内容。
