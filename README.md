# Reverse Fusion

证据驱动的逆向分析、独立复刻和多宿主部署编排器。

这个仓库是一个独立项目。它不修改旧的 `reverse-skill`、旧 installer、当前 REA 安装、当前 Craft 安装或当前 Codex 配置。

GitHub：<https://github.com/gthubtom1/reverse-fusion>

## 当前状态

仓库已完成 `RF-22`，状态为 `reconstruction-product-v1-final`。WASM、Web/JavaScript、PE/.NET 和 APK/DEX 都有独立的原版 Evidence、Spec tasks、宿主 Builder candidate、构建/运行观察、差分、proof、cleanup 和 obligation ledger。代表性目标用于验证统一逻辑，未来目标通过同一套 pipeline 进入新 case；未知能力仍按 REA 的边界保留为 `unknown`，不会被静态相似度升级成通过。

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
- normal-dev、analysis、reconstruction、follow-up profiles。
- 上游更新和上下文交接文档。

当前宿主事实仍单独记录：Codex/Pi 握手通过，Claude CLI 可启动但当前主机没有登录凭据；Craft 原生 R46 backend 未资格化，但真实 Codex host-owned Builder 已完成六项 transport。模型始终属于当前宿主，仓库不选择或下载模型。

仓库自己的 Reverse 路由不依赖旧 `reverse-workflow` receipt。它从
`components/reverse-core/routing.json` 读取固定版本的声明式规则，并把
PRIMARY 映射到 `components/reverse-core/routes/` 下的本地描述。旧路由包
仍可用下面的显式命令做只读对照：

```text
python -m reverse_fusion bridge --hint "APK reverse" --source local
python -m reverse_fusion bridge --hint "APK reverse" --source external
```

## 给智能体的快速开始

把本仓库 URL 交给智能体，然后使用：

```text
读取 README.md、AGENTS.md、docs/PROJECT-CONTEXT.md、docs/CURRENT-STATE.md、docs/DECISIONS.md 和 components/official/manifest.json。
识别当前宿主、OS、架构和已安装工具，先运行静态 plan/doctor。
不要修改旧 reverse-workflow 安装，不复制凭据，不把官方组件改成本地伪 fork。
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
.\scripts\install.ps1
python -m reverse_fusion plan --client auto --intent analysis --format markdown
python -m reverse_fusion doctor --format markdown
```

Linux/macOS 使用 `RF_DRY_RUN=1 ./scripts/install.sh` 预览，或直接执行
`./scripts/install.sh`；卸载 Windows 使用 `scripts/uninstall.ps1 -Apply`，
Linux/macOS 删除仓库内 `.venv` 即可。所有入口都限制在仓库目录内，不写宿主全局配置。

`install`、`update`、`uninstall` 默认只生成计划；需要写入本仓库状态时显式增加 `--apply`。目标链 runner 对 provider、登录和设备缺失返回 `blocked`、`unsupported` 或 `unknown`，不会把 exit 0、工具可见或模型自述写成业务验收。

## 单仓库边界

- Reverse core、schemas、host adapters、installer、docs 和 evals 由本仓库维护。
- REA 和 Spec Kit 默认通过官方来源和版本 manifest 获取。
- Craft bounded 能力通过固定 upstream identity、patch series、bundle manifest 和 executor 接入。
- 只有真实能力缺口出现后，才把具体 upstream 组件提升成同仓库内的增强 fork。

## 文档入口

- `docs/PROJECT-CONTEXT.md`
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
