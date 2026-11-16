# 当前发布验收

当前版本**1.3.0**，维护阶段RF-35。实现与本机协议/分析/浏览器资格已有实际记录，
最终工程回归、部署绑定、资产发布与远端新克隆结果以[CURRENT-STATE](CURRENT-STATE.md)
和[RF-35 checkpoint](../checkpoints/RF-35-20261116-001.md)为准；未记录的后续门不预先判通过。

RF-35补齐此前真实缺口：旧CLI/受控writer验证未证明REA/Craft MCP向Codex可达。
新实现登记官方REA server和原版Craft engine MCP，保留现有Spec/native冻结writer。
原版AI17项/setup4项有意由当前宿主及自有installer替代；原版README宣传320不是
实际registry推导。详细范围见[MCP接入](MCP-INTEGRATION.md)与[1.3说明](RELEASE-1.3.md)。

## 当前发布门

1. 本地路由、领域正文、必需引用、来源/保全清单一致，fresh clone不依赖旧receipt。
2. 默认安装真实REA、官方Spec、原生Craft writer与Craft engine MCP启动器；固定
   来源/二进制身份有效，缺任何必需组件不能报安装成功。
3. Codex用户级技能/指引及两项自有MCP登记指向当前checkout；无关配置、模型和
   凭据保留。登记、更新、移除和故障回退遵循归属，不删除其他checkout的新指针。
4. `mcp-check`按实际登记命令执行initialize、完整工具/提示目录和真实工具调用，
   记录绑定本配置/二进制的结果；`release-check --deployed`验证必要门，不能只看文件存在。
5. 当前源码/实际回归日志摘要绑定；结果数量、零跳过、最终部署checks取自记录，
   不复制旧版本数字。工程检查不冒称新业务样本或当前旧聊天已热加载。
6. 共用核心保留代表性完整运行；分析/证据/官方Spec/native写入/检查/比较/修正/
   cleanup及恢复的职责不因MCP加入而绕过。每个具体目标仍有独立行为验收。
7. 宿主范围明确：Codex自动登记MCP；Pi/Claude已有项目adapter＋CLI/native接入，
   不自动登记其全局MCP，三宿主项目检查不能说成三宿主MCP都已部署。
8. 文档、入口、版本、发布资产和GitHub记录一致，远端新克隆按当前默认步骤安装
   并保存最终结果；协议/目录/本机成功与远端复现分别留证，不用旧记录代替新门。

## 本轮实际记录

- `release/verification.json`：最终源码绑定回归结果和日志摘要，以文件实际值为准。
- `evidence/rf35/deployed-release.json`：最终本机部署检查与MCP登记/调用身份绑定。
- `evidence/rf35/tool-qualification.json`：REA255工具/6prompts、Craft303个engine工具/
  6prompts；REA分析、Craft打开目标/应用图/provider发现与Chrome双尺寸捕获/关闭。
- `evidence/rf35/rea-catalog.json`、`craft-catalog.json`及对应`*-mcp-calls.json`：
  原目录与实际调用，保留原生partial/static、截图one_state等限制。
- `evidence/rf35/config-preservation.json`：无关配置原5189字节完整保留，新增两项自有登记。
- `evidence/rf35/provider-settings-restart.json`：独立state中的provider设置恢复，
  不证明未安装provider已就绪；JADX未被现场发现仍按需准备。
- `evidence/rf35/clean-install.json`：远端新克隆41ac0ba按默认步骤下载固定组件，
  120+39零跳过，隔离用户真实MCP登记/协议调用与22项部署门通过；主用户配置保持不变。

## 保留的历史资格

RF-33完整自有应用的Codex/Pi运行、原版比较/修正/打包、原生记录及旧远端安装分别
保留在`evidence/rf33/`，支持已有共享工作流，不回写成当时已登记MCP。
RF-34全量静态收尾见[历史收尾记录](FINAL-CLOSEOUT.md)，其104/39、19等数字仅属于
1.2.1当时资格，不能覆盖本轮代码或新增MCP门。旧状态档案位于`docs/history/`。

当前客户端可能需要重载/新对话才发现新服务器；独立协议通过不等于旧聊天热加载。
不将有限记录扩张成所有外部provider已安装、任意软件必定复刻成功或所有平台均支持。
