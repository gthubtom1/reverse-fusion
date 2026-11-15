# AGENTS.md

这是 Reverse Fusion 独立仓库。先读取：

1. `README.md`
2. `docs/DEPLOYMENT-GUIDE.md`
3. `docs/PROJECT-CONTEXT.md`
4. `docs/CURRENT-STATE.md`
5. `docs/DECISIONS.md`
6. `components/official/manifest.json`
7. `skills/` 中与当前 route 对应的领域技能
8. 当前阶段对应的 `docs/DEVELOPMENT-MASTER-PLAN.md` 和 checkpoint
9. `RULES.md`；调用本地路由后读取返回的 `skill` 和 `required_reads`
10. `docs/AGENT-BOOTSTRAP.md`；只给仓库 URL 时，以此文件作为唯一部署入口

工作规则：

- 旧 `reverse-skill`、旧 installer、现有 REA/Craft/Spec Kit 安装和当前宿主配置只读；
  本仓库自己的 adapter、runner、patch 或受控 fork 可以按记录的能力缺口增强。
- 不根据聊天历史猜测状态；以 docs/CURRENT-STATE.md、SOURCE-MANIFEST.json 和 checkpoint 为准。
- 每个阶段只有一个下一步动作。
- 任何来源、schema、scope、baseline、model、provider 或 writer 变化都要更新 checkpoint。
- 不把安装成功、工具可见、Craft Ready、exit 0 或模型自述写成业务 acceptance。
- 当前阶段是 RF-25 全量审计修复中；RF-22 的 final 是历史发布标签，当前完成声明以
  `docs/CURRENT-STATE.md` 和最新 RF-25 checkpoint 的未决项为准。
- 安装只面向当前选定的一个宿主，并使用仓库 `.venv` 的 Python。宿主发现不等于安装；
  本仓库不会全局注册到其他工作区，其他项目必须显式让 agent 读取本仓库入口。
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
