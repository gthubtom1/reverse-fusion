# AGENTS.md

这是 Reverse Fusion 独立仓库。先读取：

1. `README.md`
2. `docs/PROJECT-CONTEXT.md`
3. `docs/CURRENT-STATE.md`
4. `docs/DECISIONS.md`
5. `components/official/manifest.json`
6. 当前阶段对应的 `docs/DEVELOPMENT-MASTER-PLAN.md` 和 checkpoint

工作规则：

- 旧 `reverse-skill`、旧 installer、REA、Craft、Spec Kit 和当前宿主配置只读。
- 不根据聊天历史猜测状态；以 docs/CURRENT-STATE.md、SOURCE-MANIFEST.json 和 checkpoint 为准。
- 每个阶段只有一个下一步动作。
- 任何来源、schema、scope、baseline、model、provider 或 writer 变化都要更新 checkpoint。
- 不把安装成功、工具可见、Craft Ready、exit 0 或模型自述写成业务 acceptance。
- 先做最小可验证纵向切片，再扩展模块。
- 上游更新走 `docs/UPSTREAM-MAINTENANCE.md`，不要盲目合并。
- 普通开发使用 normal-dev profile，不强行创建 reverse case。
