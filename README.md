# Reverse Fusion

证据驱动的逆向分析、独立复刻和多宿主部署编排器。

这个仓库是一个独立项目。它不修改旧的 `reverse-skill`、旧 installer、当前 REA 安装、当前 Craft 安装或当前 Codex 配置。

## 当前状态

仓库目前处于 `RF-01`：合同和静态部署入口阶段。

已经提供：

- 单仓库项目结构。
- 官方组件 source manifest。
- 版本化 handoff、external baseline、candidate result 合同。
- `plan`、`doctor`、`contracts`、`handoff` 静态入口。
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
```

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
- `docs/CONTEXT-HANDOFF.md`
- `docs/ACCEPTANCE-MATRIX.md`
