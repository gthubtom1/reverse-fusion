# Reverse Fusion 宿主自动部署契约

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

以后检查上游时，只读比较 `SOURCE-MANIFEST.json` 和
`components/official/manifest.json`，只有真实 capability gap 得到改善才吸收，
并更新 manifest、provider status、CURRENT-STATE、checkpoint 和本文件相关引用。
