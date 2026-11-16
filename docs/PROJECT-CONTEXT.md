# Project Context

Reverse Fusion当前版本为 **1.4.0 / RF-36**，主要完整分发为Windows x64，主要本机宿主为Codex。
本轮按原版职责修复provider接线、Craft分析持久化、续作与安装生命周期；
最终源码回归、部署、远端安装和发布状态统一读取[CURRENT-STATE](CURRENT-STATE.md)及
[本轮checkpoint](../checkpoints/RF-36-20261116-001.md)，不沿用旧版本“完整”结论。
当前合同见[RELEASE-1.4](RELEASE-1.4.md)、[职责承接](INTEGRATION-CONTRACT.md)与
[release/manifest.json](../release/manifest.json)。

这是独立GitHub项目。只给仓库URL时，智能体从[AGENT-BOOTSTRAP](AGENT-BOOTSTRAP.md)
安装固定真实组件和选定宿主入口，无需另存聊天或重做开发流程。
普通使用见[BEGINNER-GUIDE](BEGINNER-GUIDE.md)，智能体责任见[AGENT-WORKFLOW](AGENT-WORKFLOW.md)。
22条原需求及实际依据在[需求逐项表](USER-REQUIREMENTS-REVIEW.md)。

## 实际分工

- Reverse是route/case owner，保留原话、交付目标、领域方法、引用和当前阶段；
  case是权威，受控索引只负责发现和恢复，不授权加载越界内容。
- REA使用同一固定安装包的原版技能、方法、官方MCP/CLI和原生Evidence/comparison/proof/ledger。
  需要原生能力时调用真实工具，普通源码解释则使用现有源码工具，不为凑齐组件名称重复分析。
- 官方Spec在成果项目生成并执行当前宿主工作流，管理证据支持的规格、计划、任务及converge反馈。
  手写同名文档或只有init不能替代执行。
- Craft原版engine/MCP提供分析、浏览器、原生/设备/provider及可用插件；
  先通过fusion_case_open绑定成果case的原版Project，持久保存并恢复研究。
  Project与构建Workspace不同，通用分析MCP不绕过正式候选门。
- 当前宿主负责推理、用户问题、权限、进度和补充要求；通过真实native Craft冻结租约
  执行候选write/edit/command/check/summary/cleanup。session观察器不替代实际writer。
  图片/3D按真实producer、预算、密钥和输出条件处理，不用不存在的宿主能力作替代。
- 独立原版/候选比较负责具体行为、状态、界面与副作用验收；REA原生proof/ledger结果
  保留自身authority、coverage、limitations和未决项，局部通过不代替整个产品交付。

## 路径、恢复与边界

MCP、普通REA CLI和有预算入口共享checkout保存的allowlist provider路径；
部署发现、运行恢复与真实操作分别检查，不从终端后设环境推定桌面服务已接上后端。
本机路径和配置receipt不作为另一台电脑的配置提交；新机重新发现现有工具。
原版方法、固定资产、所选provider身份改变时，相关旧资格必须作废并重核。

成果留当前项目。normal-dev不强制创建reverse case；需要时建立隔离analysis subcase，
只有reconstruction进入证据审查、官方Spec、冻结实现和独立比较。
加壳、混淆、反调试、dump、hook、模拟和设备等方法从实际证据选择，不固定为单一路线。
缺失资料只阻断依赖它的任务，恢复时继续原目标与有效批次。

安装仅维护自有入口和托管组件：Codex用户级薄技能/指引及两项MCP指向当前checkout，
保留无关配置与其他checkout指针；缺receipt仍按归属处理，缺维护Python拒绝删除runtime。
旧安装、无关宿主设置、模型和凭据只读，不启动重复AI循环或原版setup越权改配置。

共享核心已有Codex/Pi完整自然使用；Pi/Claude按项目入口、工具与官方Spec布局核适配。
Claude完整模型运行未实测且非强制门；不轮询登录。新宿主或非Windows分发需核实际差异。
历史Evidence、失败、原ID与旧绝对路径保留；历史final标签不覆盖后来发现并修复的问题。
