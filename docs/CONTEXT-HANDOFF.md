# 当前上下文交接

当前产品版本读取`VERSION`（现为1.3.0），当前阶段和结果读取
[CURRENT-STATE](CURRENT-STATE.md)及最新checkpoint；不从旧聊天或历史“当前”段落恢复任务。

- 新电脑安装以[AGENT-BOOTSTRAP](AGENT-BOOTSTRAP.md)为唯一入口；先安装真实核心，再接所选宿主。
- 当前功能与22条要求见[需求核对](USER-REQUIREMENTS-REVIEW.md)，发布门见
  [版本说明](RELEASE-1.3.md)、`release/manifest.json`和`release/verification.json`。
- 共用核心已有Codex/Pi代表性完整运行；Codex/Pi/Claude项目适配检查已完成。
  Claude完整模型运行未实测且非适配发布门，不自动轮询登录或重新打开已交付目标。
- 普通开发保持host-native；分析与复刻使用当前成果项目的同一case和原始目标。
  仅复刻实现执行官方Spec和真实native Craft；session是附加观察，不能替代真实组件。
- 具体目标的恢复用[RECOVERY](RECOVERY.md)和只读`workflow`；目标未知、工具/设备依赖
  保存在该case，不改写成通用产品缺失，也不要求用户为完成安装再提供样本。
- 源身份和组件固定值见`SOURCE-MANIFEST.json`及`components/official/manifest.json`。
  历史Evidence ID/摘要/绝对路径不可改写；当前原生归档见`evidence/rf33/`，
  RF-25有限归档仍保留在`evidence/rf22/manifest.json`，二者不是互相替代的当前配置。
- 维护只针对实际缺口或有收益的上游变更；遵循[UPSTREAM-MAINTENANCE](UPSTREAM-MAINTENANCE.md)，
  更新受影响文档、配置和checkpoint，不把未来所有目标都变成本轮测试任务。

旧RF-30交接移至[历史快照](history/CONTEXT-HANDOFF.md)，仅用于追溯。
