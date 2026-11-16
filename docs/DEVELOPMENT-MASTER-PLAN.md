# 当前开发与维护计划

当前产品版本为1.2.1，阶段结果以[CURRENT-STATE](CURRENT-STATE.md)和最新checkpoint为准。
当前约定功能/适配范围已完成；没有因为Claude未登录而遗留的强制开发任务。
完成清单见[需求核对](USER-REQUIREMENTS-REVIEW.md)，交付说明见[RELEASE-1.2](RELEASE-1.2.md)。

接下来的工作由用户的新项目、已复现缺陷或有明确收益的上游能力更新驱动：

1. 从当前版本和实际文件确认问题及影响范围，不复用历史“下一步”。
2. 保留原目标、来源和模型归属，选择最小相关实现/资料修改；需要上游变更时按
   [UPSTREAM-MAINTENANCE](UPSTREAM-MAINTENANCE.md)核身份和回滚点。
3. 更新互相关联的入口、合同、记录和适配原因，执行与改动相称的检查。
4. 新安装按[AGENT-BOOTSTRAP](AGENT-BOOTSTRAP.md)，实际目标按其case验收，
   发布结果和目标级unknown分别保存，不靠追加用户样本才能发布工程版本。

RF-01至RF-33的阶段叙述和旧任务顺序移至[历史计划](history/DEVELOPMENT-MASTER-PLAN.md)，
仅用于理解演进；原始checkpoint仍保留在`checkpoints/`。不自动恢复旧样本对话。
