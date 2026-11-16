# Reverse Fusion 部署与使用指南

1.1.0 完整工程分发的当前范围是 Windows x64 + Codex；安装不依赖用户样本。
其他宿主与系统的旧入口保留，但完整分发资格需另行适配，不能自动报告为已支持。
工程发布门见 [RELEASE-1.1.md](RELEASE-1.1.md)。
把仓库链接交给正在使用的 Codex、Pi、Claude Code 或兼容 coding agent，并说
“部署到当前工作区”即可。完整部署动作只在
[AGENT-BOOTSTRAP.md](AGENT-BOOTSTRAP.md) 维护；这份指南解释使用与维护逻辑。
无需用户另存长提示词。所有路径根据当前 checkout 计算，不固定盘符、用户目录、
shell、模型或工具安装路径。

组件之间的真实衔接见 [ARCHITECTURE.md](ARCHITECTURE.md)：Reverse 是唯一默认
路由与 case owner，REA/Spec/Builder/验收按 workflow stage 按需激活。

## 部署范围与顺序

1. 智能体读取 README、AGENTS 和 `docs/AGENT-BOOTSTRAP.md`，发现 OS、架构、
   shell 和 Python 3.11+ launcher。正在对话的宿主即 `[selected-host]`，无需为
   本产品另选模型或账号。发现其他 CLI 不代表安装或登录。
2. Windows 先 dry-run `scripts/install.ps1 -DryRun -Python [launcher]`，再运行
   `scripts/install.ps1 -Python [launcher]`。POSIX 先
   `RF_PYTHON=[launcher] RF_DRY_RUN=1 ./scripts/install.sh`，再
   `RF_PYTHON=[launcher] ./scripts/install.sh`。这创建本 checkout 的 `.venv` 并
   安装本地包。随后运行 `reverse_fusion install --apply --client codex` 时，CLI 会
   额外写入用户级 Codex 适配层，使任意工作区都能找到这个 checkout 的路由器。
   `--no-global-adapter` 可跳过这一步。
3. 从此使用 `[venv-python]`：Windows 为 `[repo]/.venv/Scripts/python.exe`，
   POSIX 为 `[repo]/.venv/bin/python`。依次执行：

   ```text
   [venv-python] -m reverse_fusion contracts
   [venv-python] -m reverse_fusion plan --client [selected-host] --intent normal-dev
   [venv-python] -m reverse_fusion doctor
   [venv-python] -m reverse_fusion handoff --check
   [venv-python] -m reverse_fusion install --apply --client [selected-host]
   [venv-python] -m reverse_fusion release-check --deployed
   ```

4. 读取 `state/install.json`，确认 selected host 和版本；选择 Codex 时确认
   `global_adapter.enabled=true` 以及用户级 `SKILL.md`、`AGENTS.md` 存在；确认当前
   agent 已读取仓库规则及一次本地 route 的 `skill`、`required_reads`。receipt 记录
   仓库安装和适配层状态，不等于 provider 健康或业务验收。
   首次需要具体逆向工具时，先运行仓库内对应平台的
   `skills/scripts/refresh-tool-index.ps1` 或 `skills/scripts/refresh-tool-index.sh`。
   生成的 `skills/tool-index.md` 是本机观察文件，不进入 Git，也不把缺失工具伪装
   成可用能力；没有它时 skill 的工具路径检查仍保持 `unknown`。
5. 需要独立 CLI transport 时，才对选定宿主执行
   `handshake --client [selected-host] --timeout 45 --record`。固定 sentinel 只
   证明最终 assistant 应答；它不证明目标业务、完整领域加载或所有工具健康。
   缺登录、额度或 provider 时如实记录 blocked/unknown，仍可使用已运行的当前
   会话 agent。无需为了默认 Builder 再启动一个 CLI。
6. REA、官方 Spec Kit 和真实 Craft 是基础部署必需组件，默认 Windows install 自动运行
   `bootstrap-core.ps1`。WABT、JADX 等按目标需要准备。原生组件交接及当前平台范围见
   [NATIVE-COMPONENTS.md](NATIVE-COMPONENTS.md)。保存实际能力、缺失项和下一步；不写旧安装、模型、凭据或
   provider 运行配置。Codex 的受控适配层只写路由指引。Craft companion 的
   `--all-tools` 保持原样。

Reverse Fusion 的正文属于共享 checkout，case 属于当前成果项目。Codex 的用户级适配层在任务涉及
逆向、保护分析、协议复刻、行为重建或用户明确要求 Reverse Fusion 时触发；普通软件
开发保持 `host-native`。当前项目目录始终是输出和候选的工作区，不会被共享 checkout
替代。

## 对话中的动态工作方式

- **normal-dev**：普通网站、APK、桌面软件、服务端或其他项目开发；不强制 case、
  REA、Spec、proof 或 ledger。
- **analysis**：按需建立隔离 subcase，保留目标、route、原版 Evidence/观察、限制
  和结论。未要求复刻时不强制 Spec tasks 或候选。
- **reconstruction**：在分析基础上冻结 spec/tasks，限定单一 Builder workspace
  和 allowed outputs，再独立执行 build/run、comparison、proof 和 ledger。
- **follow-up**：恢复现有 case 与来源引用，按新的证据修订结论或继续任务。

例如开发网站中途需要研究另一个站点，或开发 APK 时发现相关桌面工具，均创建
自己的 analysis/reconstruction subcase。主项目继续 normal-dev；只有经过审查、
Evidence 支持的结论或候选才能带回主项目，临时候选不覆盖主项目源代码。

先用用户原话调用 `bridge --source local --hint [task] --record`，读取返回的 `workflow`、`skill`、
`related_routes`、`next_stage`、`required_reads`、`hard_target` 和
`missing_support`。普通开发的默认结果是 `workflow.stage=host-native`；需要
逆向时进入 analysis，复刻目标也先分析并保留最终意图，就绪后才切换 reconstruction。
首次指定 `--project-root [当前项目] --case-root [project-relative-case]`，后续细化用同一 case。
若首次只读探路，第一次落盘传 `--user-request [用户原话]`。资料缺失即
unavailable，不用旧 receipt 假装具备能力。

任务命令默认以调用时当前目录为成果项目；技能资料仍以共享 checkout 为根。
`required_read_paths` 给出绝对资料路径。跨项目冻结/恢复/验证步骤及组件执行含义见
[CROSS-PROJECT-WORKFLOW.md](CROSS-PROJECT-WORKFLOW.md)。

遇到加壳、混淆、反调试、反 VM、动态加载、反 Hook 或工具触发早退时，按
`RULES.md` 和 runtime manifest 加载困难目标资料。静态、动态、dump、脱壳、
hook、模拟及设备的顺序由目标证据决定；路由和技能辅助模型判断，不限制为固定
流水线。保全方法与 helper 不等于提前验证所有保护器。

## 实际 Craft Builder 与附加观察

宿主负责推理，通过真实 Craft engine 写候选并运行冻结的检查命令；必须先执行官方 Spec
生成的工作流与交接审查。完整 `native-craft prepare/build/check/refine/return_summary/cleanup`
命令见 [真实组件交接](NATIVE-COMPONENTS.md)。prepare 自带附加 session，不重复创建；
检查完成后对同一 receipt 执行 session check/refine/finish，退出后再更新任务进度。
文件边界观察与业务行为验收分别记录。选定路径限制不构成通用 OS 隔离。

面向用户的说法与开场示例见 [白话使用指南](BEGINNER-GUIDE.md)，智能体的选择依据见
[工作合同](AGENT-WORKFLOW.md)。不要让新用户通过专业术语手工接线。

## 组件与目标边界

Reverse 是唯一 route/case owner；REA 管理 Evidence/comparison/ledger；Spec
管理任务与来源引用；宿主推理通过原生 Craft 单一写入候选；独立 verifier
负责业务验收。Craft 当前分发真实固定 engine 的接入源码、可重放补丁和已核验 Windows x64 原生包；
四个旧 patch 名称仅作历史参考。模型、provider 和登录始终属于当前宿主。

REA pin 为 `6.9.0`，Node engine 精确为 `^22.23.4 || ^24.22.1 || >=26.12.1`。
如果 PATH 中的 Node 过旧，可以向 `scripts/bootstrap-rea.ps1 -NodePath [绝对路径]`
传入本机另一个满足要求的 Node；无需替换全局 Node。bootstrap 在校验版本和包完整性后，
将选定路径记入本 checkout 的 `state/rea-runtime.json`。后续 doctor、bootstrap、
Windows provider runner 和 WASM 验收按“显式参数/环境变量、有效本仓库 receipt、PATH”
的顺序使用运行时。receipt 不进入 Git，换电脑必须重新发现；路径消失或 receipt 属于
另一个 checkout 时回退到本机 PATH。缓存路径仍存在但版本变化时，doctor 会重新核版本，
bootstrap 仍执行精确 engine 门。receipt 不代表 provider 健康或目标验收。
WABT pin `1.0.42`，JADX headless MCP pin `0.7.1`。Spec source 为
`1.4.1.dev0`，历史 CLI execution 为 `1.4.0`；RF-28 实际安装 1.4.1.dev0，并要求正式生成工作流参与。
实际现场可用性看 `PROVIDER-STATUS.md` 和当前 checkpoint，不从 source pin 推断。

当前代表性范围是 WASM 有限执行、Web answer 有限重放、.NET 有限方法执行，
以及 APK 构建/manifest/member 静态对比。完整 Web graph 有 4 个 required open
义务，Android 设备运行未知。PowerShell provider runner 已在审计机执行；POSIX
agent 选择等价本机命令或记录 unsupported/blocked，不能把 Git Bash 当成原生
Linux/macOS 实机验收。

## 维护、卸载与回滚

上游更新只读比较 `SOURCE-MANIFEST.json`、official manifest 和实际变化，只有
改善真实 capability gap 时才在本仓库选择性吸收；无需跟随每次上游发布。
允许受控 adapter、patch 或 fork，保留 source identity、focused checks 和回滚点。
完整过程见 [UPSTREAM-MAINTENANCE.md](UPSTREAM-MAINTENANCE.md)。

CLI `uninstall --apply` 会按 receipt 删除本次安装写入的 Codex 适配层和 receipt；
Windows `scripts/uninstall.ps1 -Apply` 或 POSIX `scripts/uninstall.sh` 删除仓库 venv
和 receipt，vendor 资产保留。用户在全局 `AGENTS.md` 中已有的其他内容会被保留。
案例、原版 Evidence、Spec 与候选不属于通用卸载垃圾。回滚按 Git revision 和
provider manifest 处理，项目没有自动全局恢复或 receipt transaction journal。
具体边界见 [ROLLBACK.md](ROLLBACK.md)。
