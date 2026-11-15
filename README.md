# Reverse Fusion

证据驱动的逆向分析、独立复刻和多宿主部署编排器。

这个仓库是一个独立项目。它不修改旧的 `reverse-skill`、旧 installer、当前 REA 安装、当前 Craft 安装或当前 Codex 配置。

GitHub：<https://github.com/gthubtom1/reverse-fusion>

## 当前状态

仓库已完成 `RF-24`，状态为 `reconstruction-product-v1-final`。WASM、Web/JavaScript、PE/.NET 和 APK/DEX 都有独立的原版 Evidence、Spec tasks、宿主 Builder candidate、构建/运行观察、差分、proof、cleanup 和 obligation ledger。代表性目标用于验证统一逻辑，未来目标通过同一套 pipeline 进入新 case；未知能力仍按 REA 的边界保留为 `unknown`，不会被静态相似度升级成通过。RF-23 还补齐了 fresh clone 的本地领域技能正文、跨平台路径边界、持久化 case 指针、规范化 Evidence 和宿主配置快照。

RF-24 已逐文件复核旧增强版的 453 个 skills 文件，并补齐根规则、困难目标上下文交接及 CTF/Burp 辅助资源。603 个来源文件的摘要与 11 个有意适配记录在 `components/reverse-core/preservation.json`；详见 [Reverse 能力迁移审计](docs/REVERSE-CAPABILITY-AUDIT.md)。内容保全与接入检查不等于已运行所有保护器或设备。

已经提供：

- 单仓库项目结构。
- 官方组件 source manifest。
- 版本化 handoff、external baseline、candidate result 合同。
- `plan`、`doctor`、`contracts`、`handoff` 静态入口。
- `install`、`update`、`uninstall` 生命周期入口（默认 dry-run，`--apply` 只写本仓库 `state/`）。
- `bridge` 默认调用仓库自己的 portable Reverse 路由；已安装 enhanced reverse router 只在显式 `--source external` 时作为只读兼容来源，结果区分 `local-route-pass`、`external-route-pass`、`unavailable` 和 `blocked`。
- REA evidence/bundle、Spec Kit pointer、Craft bounded candidate 的 typed adapter。
- `accept --fixture console` 纵向切片：正确候选通过、故意错误候选失败、缺证据返回 unknown。
- `accept --fixture wasm` 纵向切片：REA 原版 Evidence、正确候选通过、错误候选失败、缺证据 unknown。
- `craft --source ... --output ...` 使用 `local-bounded-worker` 生成 typed candidate，官方 Craft backend 资格化后可由原 runner 替换。
- `docs/PROVIDER-STATUS.md` 持久化记录每个 provider 的 verified、unsupported 和 unverified 状态。
- `scripts/bootstrap-wabt.ps1` 和 `scripts/run-rea-wasm.ps1` 提供进程级 WABT/REA 复现入口，不写全局配置。
- `scripts/bootstrap-jadx.ps1` 固定并校验官方 `jadx-headless-mcp 0.7.1`，只写仓库 `vendor/`，用于 APK/DEX REA 分析。
- `scripts/run-wasm-vertical.ps1` 自动重建原版/正确候选/错误候选 Evidence 并运行三态验收。
- `scripts/run-web-vertical.ps1`、`scripts/run-dotnet-vertical.ps1` 和 `scripts/run-apk-vertical.ps1` 分别复现三条真实目标链；它们只在仓库 `state/` 写入运行产物。
- `scripts/run-web-proof.mjs`、`scripts/run-dotnet-proof.mjs` 和 `scripts/run-apk-proof.mjs` 生成 canonical `rea.reconstruction-proof` 与对应 ledger input。
- `scripts/run-rea-ledger.ps1` 将原版/候选 Evidence、接口比较和 WABT 运行结果组装为正式 `rea.reconstruction-proof`，再调用官方 REA ledger 做 fail-closed 闭环。
- `scripts/run-host-handshakes.ps1` 对 Codex、Pi、Claude 执行只读固定 sentinel 探针，记录真实加载、退出码、阻塞原因和 `config_mutation=false`。
- `docs/PRODUCT-GOAL.md` 是最终产品合同；`docs/HANDOFF-PROMPT.md` 是交给下一位智能体的持续交接提示词。
- `docs/DEPLOYMENT-GUIDE.md` 是交给任意 Codex、Pi、Claude Code 或兼容 agent 的宿主无关部署、嵌套 subcase 和选择性上游更新指南。
- `skills/` 保存 Reverse Skills 的本地领域正文；`evidence/rf22/` 保存去除宿主绝对路径后的代表性 Evidence、proof 和 ledger，可在 fresh clone 中复核。
- normal-dev、analysis、reconstruction、follow-up profiles。normal-dev 是轻量主项目模式，但 Reverse/REA/Spec/Builder 可以在开发中途按需创建隔离 subcase，再把经过 Evidence 支持的结论带回主项目。
- 上游更新和上下文交接文档。

当前宿主事实仍单独记录：Codex/Pi 握手通过，Claude CLI 可启动但当前主机没有登录凭据；Craft 原生 R46 backend 未资格化，但真实 Codex host-owned Builder 已完成六项 transport。模型始终属于当前宿主，仓库不选择或下载模型。

## 实际使用逻辑

部署完成后，用户只需要在当前 Codex、Pi、Claude Code 或其他兼容 agent 的工作区
里正常对话。Reverse Fusion 是 agent 的能力层，不是一个要求用户手动选择模型或
逐步点击的独立工作台：宿主负责理解当前意图和调用本仓库，仓库负责路由、case
边界、证据引用、任务冻结、候选输出范围和验收记录。

正常开发从 `normal-dev` 开始。这个模式不会因为仓库已安装就强制启动 REA、Spec
或 Builder；用户可以一直把它当作普通项目开发环境。当开发中途需要研究一个网站、
APK、桌面软件、协议或参考项目时，agent 在当前主项目下创建隔离的
`analysis`/`reconstruction` subcase。subcase 有自己的目标、Reverse route、
原版 Evidence、Spec tasks、candidate、build/run、comparison、proof 和 ledger；
只有经过 Evidence 支持的接口约束、行为结论或任务才回到主项目。这样“开发一个
网站时研究另一个网站”与“开发 APK 时分析一个桌面程序”都走同一个产品边界，
不会把主项目强行改成某一种目标类型。

逆向顺序由 agent 根据目标和证据动态决定。无壳目标可能从静态分析和运行观察开始，
带壳、混淆、反调试或设备依赖目标则可以按需选择 dump、脱壳、hook、模拟、设备或
其他 provider；Reverse 只负责选择并记录上下文，REA 负责 Evidence，Builder 只
执行冻结任务，acceptance 负责保留 `pass`、`fail`、`unknown`、`blocked` 或
`unsupported`。这套仓库不会用固定顺序限制模型，也不会把工具可见、exit 0 或模型
自述当作业务等价。

组件的维护边界如下：

| 组件 | 默认身份 | 本仓库拥有的增强 |
|---|---|---|
| Reverse core | 本仓库实现 | 路由、case、模式、subcase 生命周期和领域路由描述 |
| REA | 官方 pin | Evidence/比较/ledger 的 typed adapter、runner 和本地合同 |
| Spec Kit | 官方 CLI | 项目级 spec/plan/tasks/converge、来源引用和复刻任务边界 |
| Craft | 官方 identity + bounded adapter | patch identity、六项 Builder 合同和宿主 Builder transport |
| WABT/JADX | 官方 provider | 版本、checksum、bootstrap 和 provider 状态记录 |
| Host adapters | 本仓库实现 | Codex/Pi/Claude 探针、动态工作区发现和配置不变性 |

因此本项目既可以继续使用官方 REA、Spec Kit 和 Craft，也可以在出现真实能力缺口
时对对应组件做本地 adapter、受控 patch 或 fork。上游不会自动同步：先只读比较，
再把变化映射到本项目的 capability gap，只有验收改善且合同兼容时才吸收。详见
`docs/UPSTREAM-MAINTENANCE.md`。

“最终完成”表示这条可迁移的分析到复刻产品链已经闭合，并不表示提前测试了所有
未来软件、架构、壳、混淆和设备组合。新目标按同一套 case/Evidence/Spec/Builder/
comparison/ledger 合同进入，目标级结果仍然单独记录；产品完成后主要进行 provider、
probe、规则和部署适配的小版本演进。

仓库自己的 Reverse 路由不依赖旧 `reverse-workflow` receipt。它从
`components/reverse-core/routing.json` 读取固定版本的声明式规则，并把
PRIMARY 映射到 `components/reverse-core/routes/` 下的本地描述。旧路由包
仍可用下面的显式命令做只读对照：

```text
python -m reverse_fusion bridge --hint "APK reverse" --source local
python -m reverse_fusion bridge --hint "APK reverse" --source external
python -m reverse_fusion bridge --hint "APK reverse reconstruction" --source local --case-root work/apk-case --record
```

## 给智能体的快速开始

把本仓库 URL 交给任意智能体，然后使用下面的宿主无关提示词。它不指定固定
盘符、用户目录、shell、Python、Node、模型或 provider：

```text
读取 README.md、AGENTS.md、docs/DEPLOYMENT-GUIDE.md、docs/PRODUCT-GOAL.md、
docs/PROJECT-CONTEXT.md、docs/CURRENT-STATE.md、docs/DECISIONS.md、
docs/PROVIDER-STATUS.md、SOURCE-MANIFEST.json、components/official/manifest.json
和最新 checkpoint。
发现当前工作区、OS、架构、shell、Python、Node、Java、.NET、Android SDK、
Codex/Pi/Claude CLI 和 provider，再运行 contracts、plan、doctor、handoff。
所有路径根据当前工作区动态计算，不写固定路径；只写仓库自己的 venv、vendor、
state 和 case 目录。
normal-dev 是主项目基线，但可以在开发中途创建隔离 analysis/reconstruction
subcase，把经过 Evidence 支持的结论带回主项目。不要修改旧 reverse-workflow
安装，不复制凭据；如果真实能力缺口需要二开，先记录 upstream identity 和
patch/fork 边界，再只修改本仓库自己的增强内容。
```

本地运行：

```text
python -m reverse_fusion contracts
python -m reverse_fusion plan --client auto --format markdown
python -m reverse_fusion doctor --format markdown
python -m reverse_fusion handoff --check
python -m reverse_fusion install --client auto
python -m reverse_fusion accept --fixture console --candidate correct --record
python -m reverse_fusion accept --fixture wasm --candidate correct --record

# 目标链（先准备对应宿主 Builder candidate）
.\scripts\run-web-vertical.ps1
.\scripts\run-dotnet-vertical.ps1
.\scripts\run-apk-vertical.ps1

# 在已准备好本地 REA/WABT 后生成正式 obligation ledger
.\scripts\run-rea-ledger.ps1
```

在新电脑上的最短部署路径：

```text
git clone https://github.com/gthubtom1/reverse-fusion.git
cd reverse-fusion
.\scripts\install.ps1 -DryRun
.\scripts\install.ps1
python -m reverse_fusion plan --client auto --intent analysis --format markdown
python -m reverse_fusion doctor --format markdown
python -m reverse_fusion handoff --check --format json
```

Linux/macOS 使用 `RF_DRY_RUN=1 ./scripts/install.sh` 预览，或直接执行
`./scripts/install.sh`；如果系统没有 `python` 这个命令，设置
`RF_PYTHON=python3`（或当前 Python 3.11+ launcher）。卸载 Windows 使用
`scripts/uninstall.ps1 -Apply`，
Linux/macOS 删除仓库内 `.venv` 即可。所有入口都限制在仓库目录内，不写宿主全局配置。

`install`、`update`、`uninstall` 默认只生成计划；需要写入本仓库状态时显式增加 `--apply`。目标链 runner 对 provider、登录和设备缺失返回 `blocked`、`unsupported` 或 `unknown`，不会把 exit 0、工具可见或模型自述写成业务验收。

## 单仓库边界

- Reverse core、schemas、host adapters、installer、docs 和 evals 由本仓库维护。
- REA 和 Spec Kit 默认通过官方来源和版本 manifest 获取。
- Craft bounded 能力通过固定 upstream identity、patch series、bundle manifest 和 executor 接入。
- 只有真实能力缺口出现后，才把具体 upstream 组件提升成同仓库内的增强 fork。

## 文档入口

- `docs/PROJECT-CONTEXT.md`
- `docs/DEPLOYMENT-GUIDE.md`
- `THIRD-PARTY-NOTICES.md`
- `evidence/rf22/README.md`
- `docs/CURRENT-STATE.md`
- `docs/DECISIONS.md`
- `docs/DEVELOPMENT-MASTER-PLAN.md`
- `docs/PR-PLAN.md`
- `docs/UPSTREAM-MAINTENANCE.md`
- `docs/TARGET-CAPABILITY-MATRIX.md`
- `docs/FINAL-COMPLETION-SPEC.md`
- `docs/FINAL-RELEASE-ACCEPTANCE.md`
- `docs/PRODUCT-GOAL.md`
- `docs/HANDOFF-PROMPT.md`
- `docs/CONTEXT-HANDOFF.md`
- `docs/ACCEPTANCE-MATRIX.md`
