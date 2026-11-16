# 1.4.0 / RF-36收尾说明

本轮从原版职责到真实入口复核，修复了“服务已登记但未接上现有后端”和
“分析只留在内存、没有原版Project恢复”等确定缺口。
20项职责的来源、承接人、实际入口、条件和反例见
[承接合同](INTEGRATION-CONTRACT.md)。合同是核查对象，不是20项全操作通过的计数。

本页保存收尾范围；最终回归、部署、远端安装及发布结果只由
[当前状态](CURRENT-STATE.md)、[发布门](FINAL-RELEASE-ACCEPTANCE.md)和
[RF-36 checkpoint](../checkpoints/RF-36-20261116-001.md)裁定。
最终门正在执行时，不以文档收尾预写发布通过。

## 本次具体闭合的关联

- 原版REA方法和工具属于同一固定包；宿主按问题读取相关方法，再选择实际工具。
  源码已能回答的问题使用源码工具；需要制品、反编译、运行和差分事实时调用对应能力。
- MCP、普通CLI和有预算入口同源恢复本机工具路径；保存只含allowlist路径和来源，
  不带账号或任意环境。删除/替换工具使旧资格失效，迁移电脑重新发现路径。
- 实际Ghidra/WABT/JADX调用和6条原生Evidence的导出/重启导入已记录；
  原ID、链接、authority、限制和原始失败均保留，不把静态结果扩张为运行等价。
- Craft先在成果case打开原版Project，再分析和更新研究；Evidence、调查、未知、
  annotation、journal与目标跨进程恢复，case切换隔离，变化目标局部拒绝而不丢研究。
- 原版AI编排、问答、权限和进度由当前宿主实际承担；Spec/native继续执行正式候选。
  资产能力按真实producer、预算、密钥与产物验证，不能仅登记名称就认为功能具备。
- 白话、普通开发、嵌套case、索引/并发/失败回退有正反例；原话、完整目标和引用不被续作覆盖。
- 全局技能、指引、MCP和receipt按归属维护；无receipt仍处理自有入口，缺Python拒绝
  破坏性卸载。版本资产按manifest安全路径检查，无关内容、旧失败和其他checkout指针保留。

## 本轮材料与换电脑使用

本轮原始工具结果、provider bundle、Project恢复和相关检查归档到`evidence/rf36/`；
具体清单、最终回归数、部署门和远端来源在当前状态/checkpoint补齐，以实际文件为准。
RF-33的Codex/Pi完整自有应用链仍按原始范围解释，不能改写成当时已经登记MCP。

新电脑只从[AGENT-BOOTSTRAP](AGENT-BOOTSTRAP.md)开始，安装固定核心、发现本机工具、
部署所选宿主并检查实际入口；不需要重做历史开发、重跑所有业务样本或复制聊天。
实际使用读[白话指南](BEGINNER-GUIDE.md)，智能体职责读[AGENT-WORKFLOW](AGENT-WORKFLOW.md)。
新目标自身的行为、保护、外部服务和交付效果仍由该case的独立比较决定。

RF-34原收尾正文已移至[历史原文](history/RF-34-FINAL-CLOSEOUT.md)，仅重定位Markdown链接，
保留当时文字、数字和后来发现的边界。历史“当前/下一步/完整”不驱动现行安装。
原22条现行结果见[需求逐项表](USER-REQUIREMENTS-REVIEW.md)，不保留多张竞争的当前状态表。
