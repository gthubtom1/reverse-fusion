# 在Codex、Pi、Claude的成果项目接入

共享仓库保留唯一组件运行时、路由和领域正文。当前宿主负责推理，真实Craft执行
实现，不另外选择模型或绑定账号。Codex全局接入继续通过原安装流程管理。

Pi、Claude或希望显式接入的Codex项目可执行：

```text
[共享仓库venv-python] -m reverse_fusion connect --project-root [成果项目] --client pi
[共享仓库venv-python] -m reverse_fusion connect --project-root [成果项目] --client pi --apply
```

第一条只预览，第二条写当前项目内的薄技能、带标记指引与本项目接入记录。
Pi使用`.pi/skills/reverse-fusion/SKILL.md`和`AGENTS.md`；Claude使用
`.claude/skills/reverse-fusion/SKILL.md`和`CLAUDE.md`；Codex使用`.agents/skills`
与`AGENTS.md`。保留已有其他指引，拒绝覆盖非本工具管理的技能，不修改用户全局
设置、账号、凭据或模型。`--remove --apply`只移除本checkout的项目接入内容。

复刻时初始化当前宿主对应的官方Spec项目，例如
`specify init --here --non-interactive --integration pi --script ps`，然后执行它实际
生成的工作流。Pi官方模板位于`.pi/prompts/speckit.*.md`，Claude位于
`.claude/skills/speckit-*/SKILL.md`，Codex位于`.agents/skills`。工具按项目官方
integration记录解析，冻结constitution/specify/clarify/plan/tasks/analyze/implement/
converge实际入口；缺任何必需阶段会明确失败，不把手写同名文档冒称官方流程。

`bridge.component_entries.spec.generated_workflow`返回实际宿主和阶段文件位置。
同样继续使用原case、Evidence、交接审查、native-craft和独立比较。领域模型选择
及安装成功不代表具体软件已完成；项目接入存在不代表宿主已登录或业务执行通过。
当前实际宿主运行资格见最新checkpoint，不用历史CLI发现或sentinel代替完整使用。
