# Reverse Fusion 宿主自动部署契约

1.2.0 当前完整交付为 Windows x64 + Codex。无需用户提供真实样本来完成工程安装；
不要为完成安装新开目标对话或启动未知程序。Pi项目接入已完成实际全程使用，
Claude项目适配/官方Spec布局检查已完成；完整模型运行未实测，不作为适配发布门。
共用核心以代表性运行验证，宿主差异按HOST-PROJECT-CONNECTION.md核对与检查。
宿主项目接入见HOST-PROJECT-CONNECTION.md；其他操作系统按实际能力报告。
组件和本地回归检查与软件业务验收分开，发布依据见 RELEASE-1.2.md。
安装核心并更新全局入口后，用 `[venv-python] scripts/verify-engineering.py` 生成本机
代码摘要绑定的工程回归记录。Codex运行`release-check --deployed`检查当前版本、
真实核心和全局入口；Pi/Claude使用`release-check`检查共用版本，并按下面第4步
核实所选宿主的实际项目连接。`--deployed`是当前Codex全局入口检查，不能拿它
检查Pi/Claude而误报适配失败。这些检查不运行目标，也不要求再做一次软件复刻。
这是随仓库保存的唯一部署入口。把 GitHub 仓库链接交给当前的 Codex、Pi、
Claude Code 或兼容 coding agent，并说“把这个仓库部署到当前工作区”即可；
agent 克隆或定位仓库后，以本文件的当前 checkout 版本为准。

部署把 Reverse Fusion 的代码和资料保留在当前 checkout；当选定宿主是 Codex 时，
还会在当前用户的 `~/.agents/skills/reverse-fusion/SKILL.md` 和 `~/.codex/AGENTS.md`
写入一个薄适配层。适配层只指向这个 checkout 的路由器，不复制技能正文，不把输出
写到其他项目，也不修改模型、凭据或 provider 配置。这样另一个项目可以直接调用同一
份共享路由；如果不需要跨项目调用，可使用 `--no-global-adapter` 跳过它。

仓库地址：<https://github.com/gthubtom1/reverse-fusion>

Codex 跨项目接入的文件和生命周期见 [CODEX-INTEGRATION.md](CODEX-INTEGRATION.md)。
部署验证还必须在 checkout 外的独立临时项目运行
`[venv-python] -m unittest tests.test_cross_project -v`，验证外部项目的案例记录/恢复、
session 冻结与路径边界。仅从外部目录运行一次无写入的 bridge 不够。

智能体克隆或定位仓库后，必须以当前 checkout 的文件为准，先读取：

`README.md`、`AGENTS.md`、`RULES.md`、`docs/DEPLOYMENT-GUIDE.md`、
`docs/PRODUCT-GOAL.md`、`docs/PROJECT-CONTEXT.md`、`docs/CURRENT-STATE.md`、
`docs/DECISIONS.md`、`docs/PROVIDER-STATUS.md`、
`docs/TARGET-CAPABILITY-MATRIX.md`、`docs/REVERSE-CAPABILITY-AUDIT.md`、
`SOURCE-MANIFEST.json`、`components/official/manifest.json`、
`components/reverse-core/preservation.json`、
`components/reverse-core/runtime.json` 和 `checkpoints/` 中最新 checkpoint。

## 部署动作

1. 发现当前 checkout、OS、架构、shell 和 Python 3.11+ launcher，再让用户当前正在
   使用的宿主成为 `[selected-host]`：`codex`、`pi` 或 `claude`。可以发现其他 CLI，
   但发现不等于安装；本次只为 `[selected-host]` 写安装 receipt，不探测或调用其余宿主。
2. 创建仓库本地 `.venv`。Windows 先执行
   `scripts/install.ps1 -DryRun -Python [launcher]`，再执行
   `scripts/install.ps1 -Python [launcher]`；Linux/macOS 先执行
   `RF_PYTHON=[launcher] RF_DRY_RUN=1 ./scripts/install.sh`，再执行
   `RF_PYTHON=[launcher] ./scripts/install.sh`。
3. 从这一步开始，只使用刚创建的 venv Python，不再使用裸 `python`：

   ```text
   # Windows: [repo]\.venv\Scripts\python.exe
   # Linux/macOS: [repo]/.venv/bin/python
   [venv-python] -m reverse_fusion contracts
   [venv-python] -m reverse_fusion plan --client [selected-host] --intent normal-dev --format json
   [venv-python] -m reverse_fusion doctor --format json
   [venv-python] -m reverse_fusion handoff --check --format json
   [venv-python] -m reverse_fusion install --apply --client [selected-host] --format json
   ```

4. 确认 `state/install.json` 的 `status` 为 `installed` 且 `host.client` 等于
   `[selected-host]`。选择 Codex 时还确认 `global_adapter.enabled` 为 `true`，并检查
   receipt 中记录的 `global_adapter.skill` 和 `global_adapter.agents` 路径存在。receipt
   中发现到的其他 CLI 只属于环境观察，不代表它们已安装、已登录、已加载本仓库或通过握手。
   Pi/Claude的`install`只建立共享组件安装记录，不能据此声称成果项目已连接。
   在用户选定的成果项目执行：

   ```text
   [venv-python] -m reverse_fusion connect --client [selected-host] --project-root [成果项目绝对路径]
   [venv-python] -m reverse_fusion connect --client [selected-host] --project-root [成果项目绝对路径] --apply
   ```

   核对返回的技能文件、项目指引与`.reverse-fusion/[selected-host].json`均存在且
   指向本checkout，宿主能按自身规则发现该入口。Pi检查`.pi/skills`和`AGENTS.md`，
   Claude检查`.claude/skills`和`CLAUDE.md`。以后新成果项目执行同一连接步骤，
   不重装核心。若当前只部署共享工具、尚无成果项目，明确报告“共享核心已安装，
   项目入口待选择成果目录”，不能把工具仓库自身的连接当成所有项目都已连接。
5. 默认 Windows 安装会执行 `scripts/bootstrap-core.ps1`，实际安装固定 REA、官方 Spec Kit
   和原生 Craft adapter。缺组件时安装不能完成；`doctor.core_deployment` 必须为 installed。
   真实版本、补丁、构建和工作流见 [NATIVE-COMPONENTS.md](NATIVE-COMPONENTS.md)。
   安装写仓库自己的 `.venv`、`state/install.json`，并在 Codex 选择下写入用户级适配层。
   WABT、JADX 等目标 provider
   仅在具体任务需要时由对应 bootstrap 写入工具仓库 `vendor/`；case 仅在用户开始目标时
   写入 `--project-root` 选定成果项目的 `work/`，不会集中写回共享工具仓库。
6. 模型、账号和 provider 由 `[selected-host]` 拥有。项目不选择、下载、切换或绑定
   模型，不复制凭据，也不修改宿主运行配置。Codex 适配层只增加路由指引；Craft
   companion 的 `--all-tools` 参数保持不变。
   按需准备 REA 时，先核 Node 的精确 engine；PATH 版本不满足要求且本机已有兼容
   Node，可将其绝对路径交给 `scripts/bootstrap-rea.ps1 -NodePath [路径]`。bootstrap
   校验后保存本 checkout 的运行时 receipt，后续命令可恢复；不要把本机路径提交到 Git，
   不要为此覆盖宿主或全局 Node。具体选择顺序见部署指南。
7. 当前对话中的 agent 负责推理，真实 Craft engine 负责受限候选写入和构建检查；
   不另启一个模型或重复 Study。正式 Spec 工作流和 native-craft 接入是复刻实现必需步骤。
   只有需要独立 transport 时，才对 `[selected-host]` 执行
   `[venv-python] -m reverse_fusion handshake --client [selected-host] --timeout 45 --record`。
   固定 sentinel 只证明 assistant 应答，不等于领域加载或业务成功；登录/额度阻塞如实
   记录，当前会话仍可使用已有工具开发。具体冻结任务和候选观察流程见部署指南。
8. 完成后报告实际 checkout、commit、venv Python、selected host、receipt、当前实际
   provider 状态、未验证能力、`blocked`/`unsupported`/`unknown` 和下一步。
   只记录本次观察，不把旧握手、旧 smoke 或历史 release 表改写成当前验收。

## 对话中的使用

先读 [智能体工作合同](AGENT-WORKFLOW.md)，向用户提供
[白话使用指南](BEGINNER-GUIDE.md)。用户不需要专业提示词；宿主负责从目标和证据
选择领域、保存完整交付要求、调查依赖，并在就绪后交给真实 Spec/Craft。
新目录里的普通请求才是入口验收；预先指定内部路线的测试只验证组件衔接。

- `normal-dev` 是默认模式，不强制创建 case，也不强制启动 REA、Spec Kit、Builder、
  proof 或 ledger。
- `analysis` 目标只要求隔离 case、可恢复 route、原版 Evidence/观察、限制与结论；
  没有复刻请求时，不要求 Spec tasks、candidate、comparison、proof 或 ledger。
- `reconstruction` 目标才要求冻结 Spec tasks、受限 Builder candidate、build/run、
  original/candidate comparison、integration proof、cleanup 和 obligation ledger。
- 研究外部网站、EXE、APK、协议、依赖或参考项目时，在当前成果项目内创建隔离的
  `analysis` 或 `reconstruction` subcase，不把临时 candidate 写回主项目。
- 对目标首次用用户原话调用本地 `bridge --source local --hint [用户原话] --record`，
  指定当前成果项目和同一 case_root 后保留。首次只读探路后落盘时使用
  `--user-request [用户原话]`，不以技术 hint 覆盖最终目标。读取返回的 `skill`、
  `required_reads`、`hard_target` 和 `missing_support`。缺少必需资料时状态为
  `unavailable`，不能用旧 receipt 替代。
- 跨项目任务命令传入 `--project-root [当前成果项目绝对路径]`，并按
  [CROSS-PROJECT-WORKFLOW.md](CROSS-PROJECT-WORKFLOW.md) 接续证据、规格、Builder
  和独立验收；不要把工具 checkout 当作所有项目的输出目录。
- 任务出现加壳、混淆、反调试、反虚拟机、反 Hook、动态加载、早退或自校验时，
  按 `RULES.md` 和 `components/reverse-core/runtime.json` 加载困难目标资料；
  工具顺序由证据决定，不固定成一条流水线。
- analysis 只把 Evidence 支持的结论带回主项目；reconstruction 只把 Evidence 支持的
  结论、冻结 tasks 和审查后的 candidate 带回主项目。
  业务结果保留 `pass`、`fail`、`unknown`、`blocked`、`unsupported`。
- 工具可见、MCP catalog、Craft Ready、exit 0 和模型自述都不等于业务验收。

## 完成和停止标准

部署完成首先要求真实 REA、Spec Kit、Craft 均安装且核心探针已运行；只装 Python 包不算。
当前预编译 Craft 只资格化 Windows x64；其他平台必须完成源码适配实测，否则明确部署未完成。
此外要求当前 checkout 的 venv、selected-host receipt、Codex 用户级适配层（若启用）、
`contracts`、`plan`、`doctor`、`handoff` 和本地路由边界已记录。它不表示其他宿主或项目
已经通过业务验收，也不表示当前电脑具备所有 REA、IDA、Frida、Android 设备或商业工具能力。

换电脑仍使用本流程：重建本机路径和运行时记录，安装固定核心，完成所选宿主入口，
执行工程检查即可。禁止把`-PackageOnly`作为完整部署、跳过缺失核心后报完成，
或要求用户重讲组件关系/提供样本/登录另一宿主才能完成安装。网络下载或环境条件
失败时修复具体问题并重跑相关步骤；暂时失败应写“部署未完成”，不能交付残缺成功。
此安装流程不需要重做产品设计或整段样本复刻。新操作系统涉及的原生分发仍按实际
能力处理，不将Windows x64安装验证外推到所有平台。

以后检查上游时，只读比较 `SOURCE-MANIFEST.json` 和
`components/official/manifest.json`，只有真实 capability gap 得到改善才吸收，
并更新 manifest、provider status、CURRENT-STATE、checkpoint 和本文件相关引用。
