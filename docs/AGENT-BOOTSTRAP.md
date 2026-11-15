# Reverse Fusion 宿主自动部署契约

这是随仓库保存的唯一部署入口。把 GitHub 仓库链接交给当前的 Codex、Pi、
Claude Code 或兼容 coding agent，并说“把这个仓库部署到当前工作区”即可；
agent 克隆或定位仓库后，以本文件的当前 checkout 版本为准。

部署只作用于这个 Reverse Fusion checkout 和当前选定的一个宿主，不注册全局命令，
也不把能力自动注入其他项目。另一个项目需要使用本仓库时，用户必须显式让该项目的
agent 读取本 checkout 的 `AGENTS.md` 和本文件，或在那个工作区重新克隆并部署仓库。

仓库地址：<https://github.com/gthubtom1/reverse-fusion>

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
   `[selected-host]`。receipt 中发现到的其他 CLI 只属于环境观察，不代表它们已安装、
   已登录、已加载本仓库或通过握手。
5. 安装只写仓库自己的 `.venv` 和 `state/install.json`。REA、WABT、JADX 等 provider
   仅在具体任务需要时由对应 bootstrap 写入仓库 `vendor/`；case 仅在用户开始目标时写入
   仓库 `work/` 或明确的仓库内 case root。
6. 模型、账号和 provider 由 `[selected-host]` 拥有。项目不选择、下载、切换或绑定
   模型，不复制凭据，也不修改宿主全局配置。Craft companion 的 `--all-tools` 参数保持不变。
7. 当前对话中的 agent 就是默认 Builder，不为了使用本仓库另启一个 CLI、账号或模型。
   只有需要独立 transport 时，才对 `[selected-host]` 执行
   `[venv-python] -m reverse_fusion handshake --client [selected-host] --timeout 45 --record`。
   固定 sentinel 只证明 assistant 应答，不等于领域加载或业务成功；登录/额度阻塞如实
   记录，当前会话仍可使用已有工具开发。具体冻结任务和候选观察流程见部署指南。
8. 完成后报告实际 checkout、commit、venv Python、selected host、receipt、当前实际
   provider 状态、未验证能力、`blocked`/`unsupported`/`unknown` 和下一步。
   只记录本次观察，不把旧握手、旧 smoke 或历史 release 表改写成当前验收。

## 对话中的使用

- `normal-dev` 是默认模式，不强制创建 case，也不强制启动 REA、Spec Kit、Builder、
  proof 或 ledger。
- `analysis` 目标只要求隔离 case、可恢复 route、原版 Evidence/观察、限制与结论；
  没有复刻请求时，不要求 Spec tasks、candidate、comparison、proof 或 ledger。
- `reconstruction` 目标才要求冻结 Spec tasks、受限 Builder candidate、build/run、
  original/candidate comparison、integration proof、cleanup 和 obligation ledger。
- 研究外部网站、EXE、APK、协议、依赖或参考项目时，在仓库内创建隔离的
  `analysis` 或 `reconstruction` subcase，不把临时 candidate 写回主项目。
- 对目标先调用本地 `bridge --source local`；读取返回的 `skill`、
  `required_reads`、`hard_target` 和 `missing_support`。缺少必需资料时状态为
  `unavailable`，不能用旧 receipt 替代。
- 任务出现加壳、混淆、反调试、反虚拟机、反 Hook、动态加载、早退或自校验时，
  按 `RULES.md` 和 `components/reverse-core/runtime.json` 加载困难目标资料；
  工具顺序由证据决定，不固定成一条流水线。
- analysis 只把 Evidence 支持的结论带回主项目；reconstruction 只把 Evidence 支持的
  结论、冻结 tasks 和审查后的 candidate 带回主项目。
  业务结果保留 `pass`、`fail`、`unknown`、`blocked`、`unsupported`。
- 工具可见、MCP catalog、Craft Ready、exit 0 和模型自述都不等于业务验收。

## 完成和停止标准

部署完成只表示当前 checkout 的 venv、selected-host receipt、`contracts`、`plan`、
`doctor`、`handoff` 和本地路由边界已记录。它不表示其他宿主或项目已经加载本仓库，
也不表示当前电脑具备所有 REA、IDA、Frida、Android 设备或商业工具能力。

以后检查上游时，只读比较 `SOURCE-MANIFEST.json` 和
`components/official/manifest.json`，只有真实 capability gap 得到改善才吸收，
并更新 manifest、provider status、CURRENT-STATE、checkpoint 和本文件相关引用。
