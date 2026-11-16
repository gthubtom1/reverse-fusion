# 当前功能验收说明

当前版本为 **1.4.0 / RF-36**。原22条需求的现行结果统一在
[USER-REQUIREMENTS-REVIEW](USER-REQUIREMENTS-REVIEW.md)；本页说明证据的作用，
不再维护另一张“全部完成”表。原版能力承接读取[20项职责合同](INTEGRATION-CONTRACT.md)，
本轮最终回归/部署/远端门读取[CURRENT-STATE](CURRENT-STATE.md)。

## 几种证据分别回答什么

| 材料 | 可以确认 | 不能据此确认 |
|---|---|---|
| 来源/身份/静态合同及反例检查 | 固定方法和实现存在、归属正确、指定错误不会静默通过 | 工具所有操作或未来目标已成功 |
| 实际安装与MCP协议 | 当前组件、所选登记、真实目录/调用和进程清理 | 所有外部后端已可用，或旧客户端已热重连 |
| RF-36原版工具资格 | Ghidra PE伪代码、WABT模块、JADX class及6条原生记录恢复；Craft Project研究恢复/隔离/变化目标 | Android设备实跑、所有保护器、所有provider或完整业务等价 |
| RF-33自然使用与独立比较 | Codex/Pi在当时共享链上完成自有应用分析、官方Spec、真实native实现、修正和交付 | 当时已完成MCP接入，或后续新增provider/资产能力自动通过 |
| 某一目标的原版/候选对照 | 该目标、范围、输入、环境和产物的实际结果 | 未执行场景或其他目标效果 |

完整Evidence导出、原生Project和case记录各有职责。聊天摘要、文件SHA、原目录可见或
退出0不替原版语义结果；partial/unknown/required open和失败都保留。
资产的本地假provider测试、真实服务调用和最终产物比较也分别记录，不能混作一种通过。

## 宿主、新电脑与实际使用

宿主按[HOST-PROJECT-CONNECTION](HOST-PROJECT-CONNECTION.md)验收：
共用核心已有Codex/Pi代表性完整运行，各宿主核对自己的入口/技能/工具/权限/cwd/生命周期。
Claude完整模型运行未实测是可选观察，不要求登录后重新跑完整样本。
Codex全局MCP登记不扩张成Pi/Claude也已自动登记。

新电脑由[AGENT-BOOTSTRAP](AGENT-BOOTSTRAP.md)准备固定组件、允许的本机工具路径和
选定宿主入口，再实际检查。历史通过不替本机安装；新机器也不必重做产品开发。
当前完整预编译分发为Windows x64，设备/商业provider等按任务的真实环境使用。

已有期限、内存/输出预算、拥有的子进程清理与恢复检查。历史Codex完整应用约26.2分钟，
Pi多次期限后恢复再交付；这些是实际测量，不能宣传任意任务即时完成或永不卡顿。
新目标的效果在自己的case验收，缺依赖只阻断相关任务，其他工作继续。

RF-32的13/8/1与RF-33中间盘点见[历史快照](history/FUNCTIONAL-ACCEPTANCE-REVIEW.md)；
RF-34/RF-35数字按原始checkpoint和Evidence追溯，旧“当前”不覆盖RF-36。
