# Reverse Fusion

给当前 coding agent 使用的普通开发、逆向分析与独立复刻工具集。
仓库：<https://github.com/gthubtom1/reverse-fusion>。

产品版本 **`1.4.0`，Windows x64 / Codex 完整工程版**，当前维护阶段 `RF-36 原版职责与实际工具闭环`。
不需要用户继续提供样本才能安装或交付本版本。范围与有限发布门见
[版本说明](docs/RELEASE-1.4.md)。准确的工程检查、历史实测和
未覆盖范围分别保存在 [当前状态](docs/CURRENT-STATE.md)、
[发布验收](docs/FINAL-RELEASE-ACCEPTANCE.md) 与
[最终收尾](docs/FINAL-CLOSEOUT.md)与[最新 checkpoint](checkpoints/RF-36-20261116-001.md)。
工程版本与具体软件的复刻结果分别报告。旧版本状态和执行记录按需追溯，不是当前下一步指令。

1.4.0按[原版职责承接合同](docs/INTEGRATION-CONTRACT.md)补齐实际工具路径、原版使用
方法与记录恢复：MCP和CLI共用已保存的本地分析器路径，Craft在成果case中打开原生
Project，REA原生Evidence可导出并跨进程恢复。Ghidra、WABT、JADX与Craft重启/隔离
已有真实调用记录；工具目录和功能效果分别验收，不用目录数量代替工具工作。

## 换电脑，只给仓库链接

当前默认完整分发面向 Windows x64 + Codex；Pi项目接入已实际跑通整段使用，
Claude项目适配和官方Spec布局检查已完成，完整模型运行未实测。宿主适配不以每个
都重跑完整任务为前提，共用核心通过代表性运行验证。其他操作系统
按实际能力报告。跨宿主操作见[项目接入](docs/HOST-PROJECT-CONNECTION.md)。把仓库链接交给当前 Codex，说：

> 把这个仓库部署到当前工作区，按仓库内的部署入口安装并报告实际验证结果。

**部署交接已保存在 [docs/AGENT-BOOTSTRAP.md](docs/AGENT-BOOTSTRAP.md)**，并由
`AGENTS.md` 指向。用户无需保存聊天里的长提示词。agent 克隆后读取当前 checkout，
发现 OS、shell、Python 和当前宿主，再创建本地 `.venv`、检查合同并写当前宿主的
安装 receipt。部署流程不写固定盘符、用户名或模型名称。

```text
git clone https://github.com/gthubtom1/reverse-fusion.git
cd reverse-fusion
让当前智能体读取 AGENTS.md 和 docs/AGENT-BOOTSTRAP.md 并执行
```

基础安装需要 Python 3.11+；具体目标需要的 Node、Java、.NET、设备和其他工具按需
发现、准备。REA、Spec Kit 和 Craft engine 是完整部署必需组件；固定资产写本仓库 `vendor/`
或 `.venv`。WABT/JADX、设备等按目标准备。真实组件交接见 [组件部署](docs/NATIVE-COMPONENTS.md)。模型、账号、登录和 provider 属于当前宿主，项目不选择或下载模型。

仓库正文和运行时只保留在这个 checkout；选择 Codex 的安装还会在用户级
`~/.agents/skills/reverse-fusion/SKILL.md` 与 `~/.codex/AGENTS.md` 写入薄适配层。
因此在另一个项目中可以直接调用同一个共享路由器，不需要复制整套 `skills/`。若要
只做仓库本地安装，使用 `--no-global-adapter`。Codex 默认还登记 `reverse-fusion-rea` 和 `reverse-fusion-craft` 两项 MCP；原版对照、模式、工具与宿主权限见 [MCP 接入](docs/MCP-INTEGRATION.md)。`mcp-check` 实际连接登记命令，`release-check --deployed` 缺登记或连接证据就拒绝完成。详细的发现、安装、跨项目使用与卸载
步骤见 [部署指南](docs/DEPLOYMENT-GUIDE.md) 和 [Codex 跨项目接入](docs/CODEX-INTEGRATION.md)。

## 在对话中怎么用

**零基础先看 [白话使用指南](docs/BEGINNER-GUIDE.md)**。你说目标，智能体负责选领域、
判断缺什么、调用组件并比较结果；不需要你编写专业流程提示词。

1.2.0新增的普通请求完整使用记录见[功能复核](docs/FUNCTIONAL-ACCEPTANCE-REVIEW.md)：
仓库自有完整小应用已实际走完真实四组件、比较、修正和交付，保留各阶段原始记录。
新增[有预算REA执行](docs/BOUNDED-REA.md)、[独立进程比较](docs/PROCESS-COMPARISON.md)
及[Pi/Claude项目接入](docs/HOST-PROJECT-CONNECTION.md)。宿主适配与完整模型运行观察分别记录；
每宿主完整模型实测不是接入发布前提。

- **正常开发**：直接描述要开发的网站、应用或其他项目。默认 `normal-dev`，
  不强制建立逆向 case，也不强制启动 REA、Spec、Builder 或 ledger。
- **分析**：需要研究目标时，agent 选择专业领域，建立或恢复隔离 subcase，保存
  目标身份、Evidence、观察、未知项和结论。只要求分析时不进入复刻验收。
- **复刻**：分析结果足够支持选定功能后，执行官方 Spec 工作流并冻结 tasks，由当前会话推理并通过真实 Craft engine
  编码，再独立构建、运行、比较原版与候选，保留 proof、cleanup 和 obligation ledger。
- **开发中途研究参考项目**：在主项目中创建隔离 analysis/reconstruction subcase，
  将审查后的事实和候选整合回来；主项目不需要变成一种固定逆向流程。

聚合架构、阶段交接和各组件边界见 [架构说明](docs/ARCHITECTURE.md)。专业任务的入口是：

```text
[venv-python] -m reverse_fusion bridge --project-root "[当前项目绝对路径]" --source local --case-root work/current-case --hint "[用户原话]" --record
```

读取返回的 `workflow`、`skill`、`related_routes`、`next_stage`、`required_reads` 和
`hard_target`；`missing_support` 应为空。`normal-dev` 的普通开发返回
`workflow.stage=host-native`，不会抢占 Reverse。复刻目标首次仍进入 analysis，保存原话后
在同一 case 细化；就绪后显式切换 `--mode reconstruction`。混合目标的 secondary skill 通过 `related_routes` 和 case refs 保留，
不要求一次性加载所有 45 个领域。
完整的证据→规格→Builder→独立验收流程见
[跨项目交接](docs/CROSS-PROJECT-WORKFLOW.md)。路由成功不表示 REA、Spec、Craft 已执行。
已记录复刻 case 的 Builder prepare 会绑定原交接清单和语义审查记录，关键未知项或
摘要不一致会阻断；不绑定 case 的通用 session 只证明文件边界观察。
困难特征也可以在后续观察中发现。加壳、混淆、反调试、动态 DEX、JNI、JS VM/WASM
等资料按证据加载，静态分析、运行、dump、脱壳、hook 和设备观察的顺序由 agent
判断。缺工具或关键事实时保留 `unknown`、`blocked` 或 `unsupported`，不靠固定
工具顺序或模型自述把未知项变成通过。

## 融合了什么，哪些由本仓库维护

| 部分 | 当前职责与实现 |
|---|---|
| Enhanced Reverse | 从我们二开版 `reverse-skill` 固定来源保留 603 个文件；本仓库维护路由、恢复指针、困难目标交接与有意适配 |
| REA | 官方 `6.9.0`，负责原生分析、Evidence、比较和 ledger；本仓库有 typed adapter、runner 与明确归属的有限 integration verifier |
| Spec | 需求、plan、tasks、来源引用与 converge；官方固定版本 CLI 必须安装，并执行其生成的项目工作流 |
| Craft/Builder | 固定真实 Rust engine、原版 MCP 工具/插件加载 + 本仓库外部写入接缝；当前会话推理，原生 Craft 执行写入、命令和检查 |
| 宿主与安装 | 本仓库的本地安装、Codex 用户级路由适配、发现、只读握手、当前会话 Builder 和配置摘要观察；不更改旧仓库、旧安装、模型、凭据或无关provider配置；Codex管理两项自有MCP登记 |

这是一套有本地代码、技能正文、合同与验收的独立仓库。REA等固定运行时按manifest
获取；当前Craft engine接缝、可重放Windows补丁和原生身份由本仓库维护。
旧companion配置保持只读，不是当前部署依赖。来源见
[SOURCE-MANIFEST.json](SOURCE-MANIFEST.json) 与
[组件清单](components/official/manifest.json)。

Reverse 的保全清单含 skills 453、CTF sidecar 136、Burp 14 个文件，记录本地与上游
摘要及有意适配原因（准确数量以清单为准）。加壳、反调试、OLLVM、Android 动态 DEX/JNI/反 Frida、
.NET 混淆和 JS VM/WASM 的方法与 helper 已保留；内容和路由可达不等于所有保护器
已实测。详见 [能力迁移审计](docs/REVERSE-CAPABILITY-AUDIT.md)。

## 当前会话推理，Craft 实际执行

当前宿主读取 [智能体工作合同](docs/AGENT-WORKFLOW.md)，按实际证据判断分析何时足以
支持本批实现。执行官方 Spec 工作流并审查交接后，通过真实 Craft engine 写入/编辑
候选和运行检查。实际参数见 [真实组件交接](docs/NATIVE-COMPONENTS.md)。
`session` 仅是附加文件边界观察；`craft --source` 仅是离线夹具复制，均不替代真实实现。
工具可见、文件存在、exit 0 或 Craft 状态都不等于原版功能已经复刻。

## 有限验收与实际边界

RF-25 重建并认证了 [代表性归档](evidence/rf22/README.md)，身份与文件摘要由
[manifest](evidence/rf22/manifest.json) 索引；保留原始 hash 覆盖字段，历史绝对路径
是当时运行的观察值，不是新电脑的安装配置。

| 链路 | 已观察的范围 | 保留的范围限制 |
|---|---|---|
| WASM | 真实 WABT 运行、REA 分析/接口比较/proof/ledger；正确 pass、错误 fail、缺证据 unknown | 有限 answer fixture |
| Web/JavaScript | 原版/候选分析，四组 Node export 重放，有限 answer ledger ready | 静态 shape partial；完整 graph ledger unknown，4 个 required open |
| PE/.NET | 两侧 .NET8 构建与运行、真实成员比较、四组输入、proof/ledger | 有限 Answer 方法范围 |
| APK/DEX | javac/D8/AAPT 构建、真实 package/class 分析、manifest/member 投影与静态 ledger | 方法体等价与 Android 设备运行 unknown；fixture MainActivity 不是可启动 Activity |

上表是有限代表材料的既有观察，完整应用与宿主结果见[当前状态](docs/CURRENT-STATE.md)。
旧子CLI额度/登录探针、companion与PTY清理边界只作为历史记录，不代表当前会话
不可用，也不要求安装时重做这些探针。实际记录由[evidence索引](evidence/README.md)
及[provider状态](docs/PROVIDER-STATUS.md)定位。每个实际目标有自己的验收范围。

## 维护、验证与卸载

基础检查始终使用仓库 `.venv` 中的 Python：

```text
[venv-python] -m reverse_fusion contracts --format json
[venv-python] -m reverse_fusion plan --client [selected-host] --intent normal-dev --format json
[venv-python] -m reverse_fusion doctor --format json
[venv-python] -m reverse_fusion handoff --check --format json
[venv-python] -m reverse_fusion release-check --format json
```

Codex额外使用`release-check --deployed`检查用户级入口；Pi/Claude核实当前成果项目
的显式连接，不使用Codex全局入口检查。完整步骤仅由[安装入口](docs/AGENT-BOOTSTRAP.md)维护。

`doctor.status=pass` 仅表示仓库合同检查通过。查看 `components` 中的现场组件状态：
REA 的 source pin 不是安装，入口存在不是握手；检查 `core_deployment`，缺少核心组件时不能报告完整部署。

需要复现 provider 链时，使用 `scripts/bootstrap-*.ps1` 与 `scripts/run-*-vertical.ps1`；
先按目标准备候选和对应运行时。基础安装不要求每次跑完全部代表性链。归档认证可在
准备 REA 后运行 `node scripts/verify-evidence.mjs`，Node 须满足 REA 的精确 engine。

CLI 生命周期默认 dry-run；`install --apply --client [selected-host]` 写安装 receipt，
并在 Codex 选择下写入用户级适配层。`uninstall --apply` 会移除 receipt 和本次安装
写入的适配层。Windows 的 `scripts/uninstall.ps1 -Apply` 与
POSIX 的 `scripts/uninstall.sh` 移除本仓库 venv 和 receipt，保留 vendor、case 与成果。
安装/卸载遇到已报告的文件写入失败会恢复受控入口和记录；没有跨进程崩溃恢复日志。

恢复已有项目可用 `workflow --project-root "[成果项目]"`，需要时指定原 case 和 session。
它只读取当前状态、实际组件入口、引用和冻结变更，不执行目标或更改证据。具体失败
处理及“缺资料时继续独立工作”见 [恢复说明](docs/RECOVERY.md)。

以后想更新时，让 agent 按 [上游维护流程](docs/UPSTREAM-MAINTENANCE.md) 读取
manifest、比较上游变化、评估实际收益，再选择性适配本仓库增强版；无需跟随每次发布。

更多入口：[产品目标](docs/PRODUCT-GOAL.md)、[维护交接](docs/HANDOFF-PROMPT.md)、
[决策](docs/DECISIONS.md)、[全量复核](docs/FULL-AUDIT.md)、
[能力矩阵](docs/TARGET-CAPABILITY-MATRIX.md)、[回滚](docs/ROLLBACK.md)、
[第三方声明](THIRD-PARTY-NOTICES.md)。
