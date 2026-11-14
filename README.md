# Reverse Fusion

证据驱动的逆向分析、独立复刻和多宿主部署编排器。

这个仓库是一个独立项目。它不修改旧的 `reverse-skill`、旧 installer、当前 REA 安装、当前 Craft 安装或当前 Codex 配置。

GitHub：<https://github.com/gthubtom1/reverse-fusion>

## 当前状态

仓库目前处于 `RF-10`：合同、路由桥、Spec Kit 项目层、Craft bounded gate、宿主发现和代表性验收切片已具备；真实 provider 按宿主实际能力标记。

已经提供：

- 单仓库项目结构。
- 官方组件 source manifest。
- 版本化 handoff、external baseline、candidate result 合同。
- `plan`、`doctor`、`contracts`、`handoff` 静态入口。
- `install`、`update`、`uninstall` 生命周期入口（默认 dry-run，`--apply` 只写本仓库 `state/`）。
- `bridge` 对接已安装 enhanced reverse router 的 dry-run 路由结果，不复制第二套路由表。
- REA evidence/bundle、Spec Kit pointer、Craft bounded candidate 的 typed adapter。
- `accept --fixture console` 纵向切片：正确候选通过、故意错误候选失败、缺证据返回 unknown。
- `accept --fixture wasm` 纵向切片：REA 原版 Evidence、正确候选通过、错误候选失败、缺证据 unknown。
- `docs/PROVIDER-STATUS.md` 持久化记录每个 provider 的 verified、unsupported 和 unverified 状态。
- `scripts/bootstrap-wabt.ps1` 和 `scripts/run-rea-wasm.ps1` 提供进程级 WABT/REA 复现入口，不写全局配置。
- `scripts/run-wasm-vertical.ps1` 自动重建原版/正确候选/错误候选 Evidence 并运行三态验收。
- normal-dev、analysis、reconstruction、follow-up profiles。
- 上游更新和上下文交接文档。

还没有把真实 provider、模型、目标或宿主配置接入这个新仓库。分析和复刻执行会在后续阶段按 `docs/DEVELOPMENT-MASTER-PLAN.md` 逐步加入。

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

`install`、`update`、`uninstall` 默认只生成计划；需要写入本仓库状态时显式增加 `--apply`。真实 REA/Craft provider、宿主加载和目标级行为验收保留为 `unverified` 或 `unsupported`，不会被静态命令伪造为通过。

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
- `docs/CONTEXT-HANDOFF.md`
- `docs/ACCEPTANCE-MATRIX.md`
