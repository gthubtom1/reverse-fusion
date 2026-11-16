# 1.3.0：真实MCP工具接入

RF-35修复用户发现的实际缺口：1.2.1及以前的安装使用REA CLI和真实Craft受控
构建，但未把REA/Craft MCP登记到Codex，也未暴露Craft原版engine分析工具。
旧验证不能证明完整MCP接入。

当前Windows x64/Codex默认分发增加：

- 官方REA6.9.0 stdio server，255工具、6prompts。
- 固定Craft0.6.1源码的原版engine/MCP协议与运行时插件加载，303个engine工具、
  6prompts；当前进程Deep模式开放内部分析，执行权限由调用它的宿主承担。
- 两项自有Codex注册、原子更新/移除与故障回退，保留无关配置、模型和凭据。
- `mcp-check`从实际登记命令运行initialize、目录和原生状态工具，保存配置与
  二进制绑定记录；部署门缺核心、登记或有效调用记录均拒绝完成。
- 默认bootstrap下载摘要固定的MCP启动器与完整第三方声明，新电脑无需安装Rust。

原版独立AI层17个模型/密钥/重建管理工具及setup层4项不加载；其职责由当前
宿主、Spec/native冻结writer及本仓库安装器承担，避免第二模型循环和另一套
宿主配置写入。README宣传数不作为当前registry计数。

有限资格记录在`evidence/rf35/`：官方REA分析、Craft打开目标、应用结构分析、
provider发现、Chrome页面打开、双尺寸捕获与关闭。原生partial/unknown保持原状。
客户端可能需重载/新会话发现新服务器；协议验证不等于当前聊天已热加载，也不等于
所有外部provider均已安装。原有完整应用/多领域实测继续按[1.2说明](RELEASE-1.2.md)
解释。MCP层与原有Spec/native链互补，候选写入仍经过冻结租约。

原版对照、工具选择和边界见[MCP接入](MCP-INTEGRATION.md)，唯一安装入口为
[AGENT-BOOTSTRAP.md](AGENT-BOOTSTRAP.md)。
