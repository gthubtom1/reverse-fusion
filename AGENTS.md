# AGENTS.md

这是 Reverse Fusion 独立仓库。先读取：

1. `README.md`
2. `docs/DEPLOYMENT-GUIDE.md`
3. `docs/CODEX-INTEGRATION.md` when the selected host is Codex
4. `docs/PROJECT-CONTEXT.md`
5. `docs/CURRENT-STATE.md`
6. `docs/DECISIONS.md`
7. `components/official/manifest.json`
8. `skills/` 中与当前 route 对应的领域技能
9. 当前阶段对应的 `docs/DEVELOPMENT-MASTER-PLAN.md` 和 checkpoint
10. `RULES.md`；调用本地路由后读取返回的 `skill` 和 `required_reads`
11. `docs/AGENT-BOOTSTRAP.md`；只给仓库 URL 时，以此文件作为唯一部署入口
12. 跨项目分析/复刻读取 `docs/CROSS-PROJECT-WORKFLOW.md`
13. 核心部署与真实 Spec/Craft 交接读取 `docs/NATIVE-COMPONENTS.md`
14. 白话任务承接、目标保留与自适应分析/交付读取 `docs/AGENT-WORKFLOW.md`；用户使用说明见 `docs/BEGINNER-GUIDE.md`

工作规则：

- 旧 `reverse-skill`、旧 installer、现有 REA/Craft/Spec Kit 安装和当前宿主配置只读；
  本仓库自己的 adapter、runner、patch 或受控 fork 可以按记录的能力缺口增强。
- 不根据聊天历史猜测状态；以 docs/CURRENT-STATE.md、SOURCE-MANIFEST.json 和 checkpoint 为准。
- 每个阶段只有一个下一步动作。
- 任何来源、schema、scope、baseline、model、provider 或 writer 变化都要更新 checkpoint。
- 不把安装成功、工具可见、Craft Ready、exit 0 或模型自述写成业务 acceptance。
- 完整部署必须实际安装 REA、官方 Spec Kit 和原生 Craft engine；缺核心组件即部署未完成。
  复刻实现执行官方生成的 Spec 工作流，并通过真实 Craft 工具写入、编辑、运行检查；
  手写同名规格、session 观察器和离线复制不能替代实际组件。当前宿主负责推理，不另启模型。
- RF-25 全量审计与 RF-26 聚合架构复核已闭合；当前完成范围和保留边界以
  `docs/CURRENT-STATE.md`、`docs/FINAL-RELEASE-ACCEPTANCE.md` 和最新 checkpoint 为准。
- 安装只面向当前选定的一个宿主，并使用仓库 `.venv` 的 Python。Codex 部署还会写入
  一个用户级 `reverse-fusion` 技能和带标记的全局 `AGENTS.md` 指引；它们只指向当前
  checkout 的路由器，不复制技能正文，也不写入其他项目。宿主发现不等于安装。
- fresh clone 必须同时拥有 route descriptor 和对应的 `skills/<domain>/SKILL.md`；
  只有分类元数据而没有领域正文时，route 状态必须是 unavailable。
- 路由返回的 `missing_support` 必须为空；困难目标资料在任务文本命中或后续证据
  发现加壳、混淆、反调试时按需加载。保留来源与有意适配的清单见
  `components/reverse-core/preservation.json`，更新增强内容时同步记录适配原因。
- 先做最小可验证纵向切片，再扩展模块。
- 上游更新走 `docs/UPSTREAM-MAINTENANCE.md`，不要盲目合并。
- 普通开发使用 normal-dev profile；不自动强行创建 reverse case，但主项目开发
  中途可以按需创建隔离 analysis/reconstruction subcase，并把经过 Evidence
  支持的结果带回主项目。
- analysis case 不强制 Spec、candidate、proof 或 ledger；只有 reconstruction case
  才进入冻结 tasks、Builder、comparison、proof 和 ledger 完成门。
- `bridge` 返回 `workflow`、`related_routes` 和 `next_stage`；普通开发保持
  `host-native`，follow-up 必须从现有开放 case 恢复。不要把一次 route pass 当成
  REA、Builder 或业务等价通过。
- `bridge/session/build/craft/native-craft --project-root` 指向当前成果项目，默认当前目录；共享仓库
  只提供代码和资料。复刻案例进入 `native-craft prepare` 时绑定原 handoff 与语义审查记录，
  关键未知项阻断受影响功能，不能在编码后补造冻结记录或自行缩减原定交付范围。
