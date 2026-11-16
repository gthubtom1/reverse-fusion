# Current State

当前版本：**1.3.0**。当前维护阶段：**RF-35 MCP真实工具接入修复**。
Stage: RF-35. Status: MCP integration repair, local deployment and remote clean-install qualification complete.
Acceptance: original-engine MCP tools and retained Spec/native writer; provider and target acceptance separate.
Next action: use the registered servers after client reload; maintain reproduced issues with actual tool evidence.
本轮确认旧融合只使用CLI/受控writer，未登记REA/Craft MCP；旧“完整”结论没有覆盖
该真实缺口。新增范围见[版本说明](RELEASE-1.3.md)与[MCP接入](MCP-INTEGRATION.md)。
收尾结果与覆盖清单见[FINAL-CLOSEOUT.md](FINAL-CLOSEOUT.md)，恢复记录见
[RF-35 checkpoint](../checkpoints/RF-35-20261116-001.md)。

## 唯一当前结论

- Windows x64为已资格化的完整组件分发平台，Codex为主要本机部署。
- Reverse路由/领域正文、真实REA6.9.0、官方Spec1.4.1.dev0、原生Craft adapter0.1.1与MCP启动器0.1.0
  均有实现与安装；REA官方MCP255/Craft engine MCP303工具已登记并实际调用。当前宿主负责推理，真实Craft执行候选写入与检查。
- Codex/Pi已有普通请求下完整分析、规格、实现、独立比较、修正和打包交付记录。
  三宿主项目连接/移除及官方Spec布局检查通过；Claude项目适配完成，完整模型运行未实测。
- 按用户确定的标准，共用核心使用代表性完整运行，各宿主按入口/技能/工具/工作流
  合同适配。无需为每个宿主登录并重跑完整样本；不轮询Claude登录，不重开已结束任务。
- 当前22项功能与适配结果以[需求逐项复核](USER-REQUIREMENTS-REVIEW.md)为准。
  多领域/困难目标能力的完成不意味着所有未来目标、保护器或外部服务都预先通过。

## 入口与文档权威

| 事项 | 当前唯一依据 |
|---|---|
| 新电脑/只给仓库URL安装 | [AGENT-BOOTSTRAP.md](AGENT-BOOTSTRAP.md) |
| 用户白话使用 | [BEGINNER-GUIDE.md](BEGINNER-GUIDE.md) |
| 共用核心与宿主入口差异 | [HOST-PROJECT-CONNECTION.md](HOST-PROJECT-CONNECTION.md) |
| 智能体分析/实现责任 | [AGENT-WORKFLOW.md](AGENT-WORKFLOW.md)、本地路由返回的领域正文 |
| 真实Spec/Craft与跨项目交接 | [NATIVE-COMPONENTS.md](NATIVE-COMPONENTS.md)、[CROSS-PROJECT-WORKFLOW.md](CROSS-PROJECT-WORKFLOW.md) |
| 失败/中断恢复 | [RECOVERY.md](RECOVERY.md) |
| 当前版本与发布门 | [RELEASE-1.3.md](RELEASE-1.3.md)、[release/manifest.json](../release/manifest.json) |

## 已有验证依据及准确边界

- `release/verification.json`绑定当前工程源码与120项产品/39项复刻检查结果（0跳过）。
  收尾若改变检查绑定的源码或元数据，须按对应静态/工程检查更新资格，不冒充新业务运行。
- 已记录的本机Codex部署检查为22项通过（含MCP登记和实际协议调用）；安装核心缺失或用户级入口陈旧时拒绝完成。
- `evidence/rf35/clean-install.json`是提交41ac0ba的全新GitHub克隆默认安装记录；
  自有Node/REA/Spec/native/MCP从远端准备，隔离USERPROFILE/CODEX_HOME执行真实登记与协议调用，
  120+39零跳过、22门ready；主用户配置未改变。不是另一台物理电脑实测。
- Codex自有完整应用运行约26.2分钟，有限1416项比较；Pi曾多次达到期限后恢复，
  最终交付完成。归档身份、独立UI比对及准确限制见[evidence索引](../evidence/README.md)。
- 非Windows原生分发、目标专用IDA/Frida/Android设备或其他商业工具按实际环境准备，
  不从路由存在或Windows安装通过推定它们已可用。

## 后续动作

本轮远端新克隆默认安装及隔离用户登记、真实协议和22部署门已通过。
当前桌面旧聊天仍需客户端重载后确认发现，不冒称本轮已热加载。正常在成果项目按用户目标工作。换电脑执行已保存安装流程，新Pi/Claude成果项目
执行显式项目连接，均不需重做产品设计或历史样本。发现新缺陷时按证据维护共享实现；
不要把某目标的未知解释为当前工程版本未安装完成，也不把工程完成当成目标成功。

历史RF-33及更早状态和验收原文已转至[历史档案](history/RF-33-STATE-AND-ACCEPTANCE.md)。
该档案、旧checkpoint与旧版本的下一步仅供追溯，不能覆盖本页或当前用户决定。
