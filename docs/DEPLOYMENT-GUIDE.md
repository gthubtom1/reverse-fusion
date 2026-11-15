# Reverse Fusion 部署与使用指南

把仓库链接交给正在使用的 Codex、Pi、Claude Code 或兼容 coding agent，并说
“部署到当前工作区”即可。完整部署动作只在
[AGENT-BOOTSTRAP.md](AGENT-BOOTSTRAP.md) 维护；这份指南解释使用与维护逻辑。
无需用户另存长提示词。所有路径根据当前 checkout 计算，不固定盘符、用户目录、
shell、模型或工具安装路径。

## 部署范围与顺序

1. 智能体读取 README、AGENTS 和 `docs/AGENT-BOOTSTRAP.md`，发现 OS、架构、
   shell 和 Python 3.11+ launcher。正在对话的宿主即 `[selected-host]`，无需为
   本产品另选模型或账号。发现其他 CLI 不代表安装或登录。
2. Windows 先 dry-run `scripts/install.ps1 -DryRun -Python [launcher]`，再运行
   `scripts/install.ps1 -Python [launcher]`。POSIX 先
   `RF_PYTHON=[launcher] RF_DRY_RUN=1 ./scripts/install.sh`，再
   `RF_PYTHON=[launcher] ./scripts/install.sh`。这创建本 checkout 的 `.venv` 并
   安装本地包。脚本不是部署其他全局宿主的入口。
3. 从此使用 `[venv-python]`：Windows 为 `[repo]/.venv/Scripts/python.exe`，
   POSIX 为 `[repo]/.venv/bin/python`。依次执行：

   ```text
   [venv-python] -m reverse_fusion contracts
   [venv-python] -m reverse_fusion plan --client [selected-host] --intent normal-dev
   [venv-python] -m reverse_fusion doctor
   [venv-python] -m reverse_fusion handoff --check
   [venv-python] -m reverse_fusion install --apply --client [selected-host]
   ```

4. 读取 `state/install.json`，确认 selected host 和版本；确认当前 agent 已读取
   仓库规则及一次本地 route 的 `skill`、`required_reads`。receipt 是仓库内状态，
   不是宿主全局注册，也不是业务验收。
5. 需要独立 CLI transport 时，才对选定宿主执行
   `handshake --client [selected-host] --timeout 45 --record`。固定 sentinel 只
   证明最终 assistant 应答；它不证明目标业务、完整领域加载或所有工具健康。
   缺登录、额度或 provider 时如实记录 blocked/unknown，仍可使用已运行的当前
   会话 agent。无需为了默认 Builder 再启动一个 CLI。
6. REA、WABT、JADX 等按具体任务需要 bootstrap 到本仓库 `vendor/`，不在基础
   安装时下载全部工具。保存实际能力、缺失项和下一步；任何旧安装和全局配置均
   不写入。Craft companion 的 `--all-tools` 保持原样。

本 checkout 的规则加载只作用于当前工作区。另一个项目需要显式让 agent 读取
本 checkout 的 `AGENTS.md` 和 `docs/AGENT-BOOTSTRAP.md`，或在该工作区部署
自己的 checkout。项目不会暗中全局注入所有其他会话。

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

先调用 `bridge --source local --hint [task]`，读取返回的 `skill`、
`required_reads`、`hard_target` 和 `missing_support`。需要持久恢复点时增加
`--case-root [repo-relative-case] --mode analysis --record`。资料缺失即
unavailable，不用旧 receipt 假装具备能力。

遇到加壳、混淆、反调试、反 VM、动态加载、反 Hook 或工具触发早退时，按
`RULES.md` 和 runtime manifest 加载困难目标资料。静态、动态、dump、脱壳、
hook、模拟及设备的顺序由目标证据决定；路由和技能辅助模型判断，不限制为固定
流水线。保全方法与 helper 不等于提前验证所有保护器。

## 当前会话 Builder

默认 writer 就是用户正在对话的宿主 agent。冻结目标任务、研究文件与输出白名单
后，让它用已有工具编写候选，不启动另一个账号、模型或 CLI。示意命令：

```text
[venv-python] -m reverse_fusion session prepare --receipt work/[case]/session.json --workspace work/[case]/candidate --tasks T-001 --task-file specs/[feature]/tasks.md --research-file work/[case]/accepted-research.json --allowed-output src/main.ext
# 当前宿主读取冻结文件，实际编写白名单内的候选
[venv-python] -m reverse_fusion session check --receipt work/[case]/session.json
# 当前宿主审查候选，必要时只修改白名单内文件
[venv-python] -m reverse_fusion session refine --receipt work/[case]/session.json
[venv-python] -m reverse_fusion session finish --receipt work/[case]/session.json
```

`--allowed-output` 相对于 candidate workspace，可重复。receipt 必须在 workspace
外。该观察器核对冻结输入和文件边界，不能阻止 agent 自己工具的越界操作，也不
证明候选行为正确。随后必须独立构建、运行或明确记 unknown，再做原版/候选对比
和 ledger。可选 `build --host ...` 是独立子 CLI transport；`craft --source ...`
是离线确定性复制 worker，均不可替代真实业务证明。

## 组件与目标边界

Reverse 是唯一 route/case owner；REA 管理 Evidence/comparison/ledger；Spec
管理任务与来源引用；当前宿主 Builder 是单一 candidate writer；独立 verifier
负责业务验收。Craft 当前只分发 bounded interface，历史 patch 名称未分发或
replay，native R46 unsupported。模型、provider 和登录始终属于当前宿主。

REA pin 为 `6.9.0`，Node engine 精确为 `^22.23.4 || ^24.22.1 || >=26.12.1`。
WABT pin `1.0.42`，JADX headless MCP pin `0.7.1`。Spec source 为
`1.4.1.dev0`，历史 CLI execution 为 `1.4.0`；本地任务文件不要求每次装 Spec CLI。
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

CLI `uninstall --apply` 只删 receipt；Windows `scripts/uninstall.ps1 -Apply`
或 POSIX `scripts/uninstall.sh` 删除仓库 venv 和 receipt，vendor 资产保留。
案例、原版 Evidence、Spec 与候选不属于通用卸载垃圾。回滚按 Git revision 和
provider manifest 处理，项目没有自动全局恢复或 receipt transaction journal。
具体边界见 [ROLLBACK.md](ROLLBACK.md)。
