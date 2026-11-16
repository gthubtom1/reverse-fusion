# 仓库内的维护交接

本文件随 GitHub 仓库保存。新电脑部署只需仓库链接和“部署到当前工作区”；
唯一部署入口是 [AGENT-BOOTSTRAP.md](AGENT-BOOTSTRAP.md)，用户无需另存或复制
长提示词。本文件用于后续维护、恢复任务和选择性更新。

## 接手时读取

读取 `README.md`、`AGENTS.md`、`RULES.md`、`docs/AGENT-BOOTSTRAP.md`、
`docs/PRODUCT-GOAL.md`、`docs/PROJECT-CONTEXT.md`、`docs/CURRENT-STATE.md`、
`docs/DECISIONS.md`、`docs/PROVIDER-STATUS.md`、`docs/TARGET-CAPABILITY-MATRIX.md`、
`docs/FINAL-RELEASE-ACCEPTANCE.md`、`docs/DEPLOYMENT-GUIDE.md`、
`SOURCE-MANIFEST.json`、`components/official/manifest.json`、
`components/reverse-core/preservation.json`、当前 checkpoint 和 Git 状态。
具体目标还要读取本地路由返回的 `skill`、`required_reads` 和当前 case。

当前维护阶段是 RF-33，产品版本为 `1.2.0`，Reverse 领域合同版本为 `1.9.0`。
是否已完成本轮审计，以 `CURRENT-STATE.md` 和
`checkpoints/RF-33-20261116-001.md` 为准。用户要求继续完成原始产品功能，不能只做工程安装；
不再向用户要样本或恢复旧真实目标，使用已保存的自有重复材料。
先读 `docs/REMAINING-PRODUCT-WORK.md`，再读取 `docs/RELEASE-1.2.md` 和 `docs/RECOVERY.md`。
RF-22/RF-23/RF-24/RF-26 的历史 final
标签不覆盖本轮发现的问题或当前 provider 阻塞。

## 保持的职责与边界

- Reverse 是唯一 route/case owner。fresh clone 必须自带 descriptor、技能正文和
  必需资料；缺失时返回 `unavailable`，旧 receipt 不是替代品。
- REA 管理 Evidence、comparison 和 ledger；本仓库的有限 integration verifier
  可使用官方 serializer，但不得冒充 REA 原生进程验证器或靠改 links 闭合。
- Spec 是任务和来源引用层。normal-dev 按需使用，analysis 不强制 Spec/candidate；
  reconstruction 才执行官方生成工作流、冻结 spec/plan/tasks，并保留 converge 和修正记录。
- 宿主负责推理，通过真实 Craft engine 作为唯一候选写入者与命令运行者。
  native-craft prepare/build/check/refine/return_summary/cleanup 使用冻结租约；session
  仅做附加观察。REA、官方 Spec CLI 与原生 Craft 都必须安装。
  接缝/补丁和完整参数见 [NATIVE-COMPONENTS.md](NATIVE-COMPONENTS.md)。
- 模型、provider 和登录属于宿主；不选择、下载或切换模型，不复制凭据。
- 旧仓库、旧安装、宿主运行配置和用户全局指引中的非托管内容只读；Codex 安装只维护
  receipt 记录的 `reverse-fusion` 适配层。Craft companion 的 `--all-tools` 保持原样。
  当前 Craft 分发有真实 engine 接入和可重放 Windows 补丁；四个旧 patch 名称仍仅作历史参考。
- 工具可见、exit 0、MCP connected、Craft Ready 和模型自述不是业务验收。

## 开始一次任务

1. 按部署入口使用仓库 venv Python，运行 `contracts`、当前 host 的 `plan`、
   `doctor` 和 `handoff --check`。doctor 的 provider 状态不是现场业务证明。
2. normal-dev 继续普通开发。需要研究外部项目时，在成果项目内建立隔离 analysis
   subcase；读取路由和困难目标资料，保留原版 Evidence、限制及下一步 probe。
3. 只有用户要求复刻时升级为 reconstruction，冻结 tasks/research，准备唯一
   writer 和明确 allowed outputs。按 `CROSS-PROJECT-WORKFLOW.md` 传入 `--project-root`，
   绑定同一 case、原 handoff 与语义审查记录后使用 `native-craft prepare`，
   由真实 engine 写入、检查、修正与清理，再执行附加 session 观察。文件观察通过后仍需独立 build/run 和对比。
4. 记录原版/候选分析、comparison、有限 proof、清理与 obligation ledger。
   证据、登录、设备或工具缺失时保留 `unknown`、`blocked`、`unsupported`。
   有壳、混淆、反调试时根据证据调整工具顺序，不把方法固定为一条流水线。
5. 只把审查后的 Evidence 支持结论或候选带回主项目；不让临时子案例覆盖主项目。
6. 收口时更新当前状态、provider、能力矩阵、验收表、manifest 和 checkpoint；
   运行与改动相称的有限检查，不重复扩张到无关目标。

代表性验收的准确身份在 `evidence/rf22/manifest.json`。RF-25 原样归档替代了
旧的路径规范化记录；历史观测中的绝对路径不作为部署配置，也不能直接改写后
继续沿用旧 Evidence ID。Web 有限 export ledger 与完整 graph 未知义务分开；
APK 只有构建和 manifest/member 静态证明，设备运行及方法体等价保持 unknown。

## 更新与交付

上游更新按 `docs/UPSTREAM-MAINTENANCE.md` 做只读比较。只吸收改善真实缺口的
变化，记录 source/patch/fork 身份、影响、focused checks 和回滚点；无需跟随
每次上游发布。交付写明实际范围、结果状态、cleanup、commit、GitHub 链接和
尚存 provider 边界。RF-26 还要求阅读 bridge 的 workflow、related_routes 和
next_stage，以便混合任务和 follow-up 不依赖聊天记忆。验收记录与仓库状态一致后停止，不把未来每种目标都变成
本次发布的必做测试。
