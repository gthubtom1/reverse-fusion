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

工作规则：

- 旧 `reverse-skill`、旧 installer、现有 REA/Craft/Spec Kit 安装和当前宿主配置只读；
  本仓库自己的 adapter、runner、patch 或受控 fork 可以按记录的能力缺口增强。
- 不根据聊天历史猜测状态；以 docs/CURRENT-STATE.md、SOURCE-MANIFEST.json 和 checkpoint 为准。
- 每个阶段只有一个下一步动作。
- 任何来源、schema、scope、baseline、model、provider 或 writer 变化都要更新 checkpoint。
- 不把安装成功、工具可见、Craft Ready、exit 0 或模型自述写成业务 acceptance。
- fresh clone 必须同时拥有 route descriptor 和对应的 `skills/<domain>/SKILL.md`；
  只有分类元数据而没有领域正文时，route 状态必须是 unavailable。
- 先做最小可验证纵向切片，再扩展模块。
- 上游更新走 `docs/UPSTREAM-MAINTENANCE.md`，不要盲目合并。
- 普通开发使用 normal-dev profile；不自动强行创建 reverse case，但主项目开发
  中途可以按需创建隔离 analysis/reconstruction subcase，并把经过 Evidence
  支持的结果带回主项目。
