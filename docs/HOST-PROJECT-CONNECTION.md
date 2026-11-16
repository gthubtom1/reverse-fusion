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

## 共用核心与宿主适配的完成条件

用户2026-11-16明确：采用共用核心、宿主薄入口和代表性完整运行。无需每新增一个
宿主都登录并完整复刻样本，才允许判定适配完成。按以下三层分别记录：

| 层次 | 要验证什么 | 是否要求每个宿主完整模型实测 |
|---|---|---|
| 共用核心 | Reverse/REA/官方Spec/原生Craft、目标保留、比较修正与恢复 | 已有Codex/Pi代表性完整运行；核心变化按受影响能力回归 |
| 宿主适配 | 官方入口与技能目录、项目路径、命令调用/权限约束、Spec布局、接入/更新/移除和配置保留 | 必须核对实际约定并检查适配；不要求登录模型或整段样本重跑 |
| 实际使用观察 | 某个宿主/模型/环境在具体任务中的行为和效果 | 按已发生事实另记，可按需抽测；不是每个适配的强制发布门 |

当前Codex/Pi/Claude均有明确入口实现，三者的项目连接/移除和官方生成Spec八阶段
发现检查已经通过；Codex/Pi另有完整运行记录。因此Claude应标为“项目接入适配完成，
未做完整模型运行实测”，不能因为本机未登录把适配写成未完成。未发生的运行记录仍
保持未实测，不能把Codex/Pi的运行结果改写成Claude跑过。

不同宿主不必使用同名文件：本实现Codex/Pi使用`AGENTS.md`，Claude使用`CLAUDE.md`，
技能位置与工具调用方式按各自约定映射。未来接入新宿主复用共用核心，核对这些差异，
检查路径/参数/生命周期即可；新增工具协议、权限、进程或工作目录语义时，对差异做
针对性验证，不重做整套项目。换操作系统涉及原生二进制/运行时分发，仍需相应工程验证。

## 宿主未登录时的可选运行观察

没有登录时可完成适配检查；只有实际运行该宿主的模型任务需要账号。用户未来确需
Claude运行观察时，可自行在Claude Code终端执行`claude auth login`。不要把密钥或
登录令牌发进对话。之后按现有准备恢复，不另选provider或模型。此项不是适配完成或
当前交付的阻塞条件，不自动轮询登录、不要求用户为发布专门登录。

本轮已准备仓库外的独立原件副本和Claude项目指引，索引保存在
`../evidence/rf33/claude-ready-project.json`。该文件记录原件摘要、入口位置、普通
请求和可选运行观察的完成条件；尚未初始化案例、生成规格或编写候选，不把准备工作冒称运行实测。
新电脑根据自己的目录重建连接，不使用记录中的旧电脑绝对路径。
