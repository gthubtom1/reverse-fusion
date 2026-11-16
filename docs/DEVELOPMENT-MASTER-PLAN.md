# 当前开发与维护计划

当前版本为 **1.4.0 / RF-36**。本轮目标是把原版有用职责落实到实际工具、
本地后端、持久分析、宿主承接及安全生命周期，不能仅靠路线图或安装成功交付。
[20项职责合同](INTEGRATION-CONTRACT.md)定义每项负责人、入口、完成条件和反例；
[22条原需求](USER-REQUIREMENTS-REVIEW.md)保留用户目标。

**当前唯一下一步：完成本轮最终源码绑定回归、本机部署与远端默认安装，保存发布身份。**
执行状态和准确剩余项以[CURRENT-STATE](CURRENT-STATE.md)、
[REMAINING-PRODUCT-WORK](REMAINING-PRODUCT-WORK.md)和
[RF-36 checkpoint](../checkpoints/RF-36-20261116-001.md)为准。
不在这些门完成前写成“本轮已全部交付”。

## 收尾顺序与完成定义

1. 对照固定原版核实20项职责的实际承接，保留来源和反例；
   真实适配缺口与外部账号/设备条件分别记录，不能把缺接线改叫缺key。
2. 将相关源码、资产身份、入口、文档、provider配置与恢复路径对齐；
   实际工具结果、原生持久记录和失败保留，不重写旧ID或旧成功范围。
3. 执行与变化相关的最终回归并绑定日志摘要，再检查当前宿主真实部署；
   同一版本从远端新克隆走默认安装，核必需组件、入口、协议和归属。
4. 保存最终commit/tag/资产与本地、远端检查结果，更新当前状态和checkpoint；
   只有这些记录齐全才关闭本轮工程任务，不把具体新目标预先判通过。

此后维护由已复现问题、用户新项目或有明确收益的上游变化驱动。
按[UPSTREAM-MAINTENANCE](UPSTREAM-MAINTENANCE.md)核来源和回滚点，更新互相关联的合同与
必要检查。新安装只走[AGENT-BOOTSTRAP](AGENT-BOOTSTRAP.md)，不追加样本或恢复旧软件对话
作为工程发布前提；宿主适配不要求每个宿主完整模型实跑。

RF-01至RF-33的旧阶段叙述见[历史计划](history/DEVELOPMENT-MASTER-PLAN.md)，
RF-34收尾见[历史原文](history/RF-34-FINAL-CLOSEOUT.md)，RF-35按其原checkpoint追溯。
历史“下一步”仅解释演进，不是当前任务队列。
