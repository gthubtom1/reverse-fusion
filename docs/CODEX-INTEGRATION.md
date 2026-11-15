# Codex 跨项目接入

Reverse Fusion 的路由器和领域资料保留在当前 checkout。Codex 选择为 selected host 时，
`reverse_fusion install --apply --client codex` 另外写入两项用户级接入：

- `~/.agents/skills/reverse-fusion/SKILL.md`：说明何时启用 Reverse Fusion，以及如何调用
  当前 checkout 的 `.venv` 路由器。
- `~/.codex/AGENTS.md`（设置 `CODEX_HOME` 时使用该目录）中的 `reverse-fusion:begin/end` 标记块：要求涉及逆向、保护分析、
  协议复刻或行为重建的任务先使用这个技能。

这两项内容只保存 checkout 路径和调用规则，不复制 `skills/` 正文，不选择模型，不启动
provider，也不改变当前项目的工作目录。模型在普通软件开发任务中仍走 `host-native`；
进入 Reverse Fusion 时先运行：

```text
Windows: [checkout]\.venv\Scripts\python.exe -m reverse_fusion bridge --source local --hint "任务"
POSIX:   [checkout]/.venv/bin/python -m reverse_fusion bridge --source local --hint "任务"
```

然后读取返回的 `workflow`、`skill`、`required_reads`、`related_routes`、`next_stage`、
`hard_target` 和 `missing_support`。

完整的跨项目交接见 [CROSS-PROJECT-WORKFLOW.md](CROSS-PROJECT-WORKFLOW.md)。任务命令
使用 `--project-root` 指向当前软件项目，省略时使用当前目录；不得为了调用共享工具切换到
工具仓库后再隐式保存 case。`required_read_paths` 指向共享技能资料，输出与 session 留在
成果项目。一次路由成功不等于 REA、Spec、Craft 或 Builder 已执行。

## 安装和卸载

Codex 的默认安装会启用适配层：

```text
[venv-python] -m reverse_fusion install --apply --client codex
```

只想保留仓库本地运行时，可以使用 `--no-global-adapter`。receipt 会在
`state/install.json` 中记录适配层路径和 `enabled` 状态。`uninstall --apply` 和仓库的
卸载脚本会删除本次安装管理的技能文件和标记块，并保留全局 `AGENTS.md` 中其他内容。
