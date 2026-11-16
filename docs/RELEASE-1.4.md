# 1.4.0：本地后端接线与可恢复的原版分析

RF-36对照原版实际实现，修复“服务已登记、目录可见，但本地后端没有带进桌面服务”
和“Craft分析仅在内存中，未承接原版Project持久能力”两项实际缺口。
这是在1.3.0 MCP接入基础上的修复，不把历史有限调用回写成当时所有能力均已接通。

## 本轮交付

- 同一仓库Python launcher启动固定REA官方server及Craft原版engine/MCP，继承原始stdio，
  管理服务进程和子进程；不启动第二模型。
- `providers --refresh`发现、校验并保存允许的本地工具路径；MCP、有预算REA CLI和诊断
  从同一checkout配置恢复。无需依赖桌面应用继承终端后来设置的变量，不运行shell profile、
  不导入任意环境、不搬运凭据；迁移电脑重新发现本机路径。
- Craft MCP adapter0.1.1新增`fusion_case_open`，用绝对成果项目/case绑定原版分析Project。
  原版Evidence、unknown、investigation、annotation、journal与目标上下文保存在case，
  重启同case恢复，切换case隔离；目标变化局部报告，不清掉旧研究。
- 未绑定分析明确拒绝；`engines_list`区分实际Deep模式与保存值。MCP独立源码树和可重放
  补丁不改变native writer的来源身份或既有构建能力。
- 固定registry为REA255工具、Craft303个engine工具加2个自有绑定/资产工具；两者均6prompts。
  **305是目录核对值，不是305项操作或所有provider健康的证明。**
- 原版职责逐项记录来源、实际承接入口、条件及会失败的反例，见
  [承接合同](INTEGRATION-CONTRACT.md)和[机读清单](../components/integration-contract.json)。
- `fusion_asset_generate`实际接通原版图片/3D工具和Fal producer：当前绑定case内独立
  暂存Workspace/Inbox，显式单次预算/允许及环境key；结果经审查的Spec/native命令整合候选。

## 已实际运行的范围

[provider-report](../evidence/rf36/provider-report.json)、
[provider-calls](../evidence/rf36/provider-calls.json)及
[provider-bundle](../evidence/rf36/provider-bundle.json)保存真实官方REA操作：
WABT的WASM分析、JADX的APK/class分析、Ghidra的自有PE打开与`main`伪代码。
完整bundle含6条记录；服务退出后新进程实际导入，原生ID、链接和限制保留。
验证移除了终端allowlist provider变量，从已保存路径启动，两次进程均验证清理。
这是有限静态分析与证据恢复，不是设备、动态运行或目标等价结论。

[craft-memory-report](../evidence/rf36/craft-memory-report.json)及
[craft-memory-calls](../evidence/rf36/craft-memory-calls.json)保存实际Project绑定、
JS分析、brief/finding/handoff/unknown、native annotation与journal，
退出重启恢复、切换案例无串入，以及变化目标的局部拒绝恢复。

[asset-report](../evidence/rf36/craft-assets-report.json)与
[asset-calls](../evidence/rf36/craft-assets-calls.json)记录原版producer的loopback HTTP实测：
图片PNG、提示生成GLB、已有图片生成GLB、缺key、未准备/未允许、超预算、路径越界、
原版provider错误和secret清除。正式候选摘要不变。模拟产物验证实际接线与失败控制，
未调用真实付费服务，不声明其生成质量。

共享核心此前Codex/Pi完整应用交付、Spec/native执行和独立比较仍按原始范围解释。
RF-35的浏览器与有限MCP记录是历史依据；本轮不能仅靠它们宣布provider或Project修复通过。
当前工程/部署/干净安装数量和发布身份读取[CURRENT-STATE](CURRENT-STATE.md)、
本轮checkpoint与发布绑定记录，本页不预写尚未运行的检查结果。

## 原版GUI/AI层与可选能力

当前宿主负责推理、问答、权限、进度、补充要求和方法选择；官方Spec负责真实生成的
规格/计划/任务阶段，native冻结租约提供真实Workspace/Inbox、写入、编辑、检查、中止和清理。
分析Project不等于构建Workspace，不能直接用分析MCP通用build工具绕过该租约。
原版独立Rebuild/模型管理和setup不加载为第二套代理/安装器。

运行时MCP插件保留；WASM组件插件是未编译的上游可选feature。设备、商业分析工具、
其他操作系统和目标服务按真实条件使用，不从目录或另一后端成功推断可用。

图片可以使用当前宿主实际图片工具。原版engine的fal.ai图片和Tripo P1模型producer
已经实现真实HTTP请求与下载，当前适配补齐Workspace/预算/AssetKeys接线。
key只取服务进程显式`REVERSE_FUSION_CRAFT_FAL_KEY`，不进工具参数/提示/日志/回执，
不读旧keychain；每次付费允许仍由宿主依当前任务决定。产物留case暂存区供检查，
不会直接修改正式候选。宿主图片生成不冒充3D；实际付费服务仍需可用key/额度，
实际产物质量按目标验收。本轮没有付费生成，也不要求用户追加软件样本来交付该接线。
若具体交付需要3D资产，使用真实通路并核实效果，不能静默交付占位物。
使用和新机安装入口分别见[白话指南](BEGINNER-GUIDE.md)与[AGENT-BOOTSTRAP](AGENT-BOOTSTRAP.md)。
