# 目标族能力与运行观察

本表区分领域入口、通用分析方法和具体运行资格；不把旧样本未覆盖项写成当前产品
未完成，也不把路线存在写成任意目标已通过。当前1.3.0的整体功能/适配结果见
[需求核对](USER-REQUIREMENTS-REVIEW.md)，新目标按自己的case建立Evidence与比较。

| 目标族 | 可用入口/方法 | 已观察的有限范围 | 新目标按需条件 |
|---|---|---|---|
| WASM | WABT/REA接口与模块分析、解释器重放 | 原始answer fixture正确/错误/缺证三态，有限ledger ready | 分析实际模块/宿主依赖并运行选定输入，不由接口相似推断全部行为 |
| JavaScript/Web | REA应用/导出分析、浏览器/Node观察与独立比较 | RF-33普通白话完整自有应用交付，Codex/Pi原版比较/修正/打包，独立留出UI通过；RF-25旧静态完整graph的4项open保留 | 当前目标的DOM/存储/网络/状态和运行环境分别调查，静态unknown不抹除 |
| Electron/混合桌面 | 页面/场景、资源、IPC、JS/native交叉分析 | 路由和相关资料可达；没有独立Electron完整运行资格声明 | 发现实际封装、后端与设备/provider后选择观察方法 |
| PE/.NET | managed artifact/member检查、native PE布局/代码与保护方法 | RF-25 managed方法构建/有限重放；RF-33独立自有C实现10输入比较、真实系统调试附加差异及官方REA PE检查 | 实际架构、依赖、保护与观察者影响逐项确认；不是所有保护器都已突破 |
| APK/DEX | pinned JADX/REA包/类检查，动态DEX/JNI/native与设备方法 | RF-25构建和manifest/member静态投影通过；方法体等价、Activity启动和设备运行未实测 | 需要运行声明时准备实际设备/模拟器及相关provider；安装工具不等于设备行为通过 |
| Native ELF/其他架构 | 布局/安全加固/反汇编与按需动态工具 | 当前分发以Windows x64为主；不声明Linux/macOS目标或所有架构已运行 | 准备对应架构与工具；REA PTY、旧process-lease和新的owned Job runner各有边界，不能互相冒充 |
| 协议/API | 包/HAR与静态契约、真实capture/replay、状态和服务依赖 | RF-33自有状态协议5组迹线、错误候选拒绝，设备/密钥拒绝/过期/取消/离线；真实HTTP200/400/404及官方HAR分析 | 实际服务权限、会话、时钟、设备、错误路径和副作用逐项确认 |

当前代表性材料：`evidence/rf33/owned-desk-completion.json`、`pi-full-use.json`、
`native-qualification.json`、`protocol-qualification.json`。RF-25的有限WASM/Web/.NET/
APK原始身份与文件摘要仍在`evidence/rf22/manifest.json`；RF-28的外部K/q/R有限
组件衔接在对应checkpoint，不能冒称整个外部软件完成。

加壳/混淆/反调试/动态加载的方法资料与helper保存在增强来源清单中，路由按证据
加载所需上下文。来源保全与实际困难目标成功是不同结论；按当前工具、设备和输入
记录pass/fail/unknown/blocked/unsupported，并保留下一证据动作。

宿主适配不是新的目标族：共用核心与薄入口检查见
[HOST-PROJECT-CONNECTION](HOST-PROJECT-CONNECTION.md)。不强制每个宿主重跑完整
目标，也不从历史CLI sentinel推导当前目标行为成功。
