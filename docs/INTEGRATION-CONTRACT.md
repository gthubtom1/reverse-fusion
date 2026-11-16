# 原版能力到融合实现的验收合同

这份合同用来防止“已安装的部分能运行”被误报为“原版职责已经全部承接”。
每一项原版有用职责都必须能找到来源、融合后的明确负责人、真实入口、完成条件和会失败的反例。
只有工作流图、组件名称、工具目录或绿色安装回执，均不满足这个要求。

机读清单是 [components/integration-contract.json](../components/integration-contract.json)。
它保存 **20项职责映射**，没有 `pass` 或 `complete` 字段。静态检查负责拒绝缺负责人、入口、
条件、必需文件或检查命题的映射；真实运行由对应日志、原生结果和发布记录负责。
检查路径存在不表示其中每个命题已经执行；若现有测试尚未覆盖某个命题，必须补上并实际运行。
1.4.0/RF-36的职责实现和有限操作见[版本说明](RELEASE-1.4.md)；
当前实际结果读取 [CURRENT-STATE.md](CURRENT-STATE.md) 和 [RF-36 checkpoint](../checkpoints/RF-36-20261116-001.md)，
不能从本文件推导本轮所有工作已完成。

## 承接关系怎样核对

先从固定原版的实际注册和调用路径确认职责，再判断融合中的保留、适配或替代：

1. **来源**：读取固定版本的技能、服务、工具实现、运行条件及输出格式，不能只读README宣传。
2. **承接**：确认负责人和真实入口；有意由宿主替代的功能必须有可执行的承接方式。
3. **条件**：把必装核心、外部工具/设备/账号条件、执行结果和目标效果分开。
4. **反例**：实际制造一个应失败的情形，确认系统不会吞错、丢目标或把未知写成成功。
5. **记录**：保存所检查来源、当前版本、真实输入/输出、未覆盖范围与修复；上游或适配改变时重核受影响行。

下表是导航。每项的完整来源路径、入口、完成条件、检查位置和反例在同ID的机读记录中。

| 职责ID | 用户可得到的作用 | 融合承接点 | 不能省略的反例 |
|---|---|---|---|
| `reverse-routing` | 白话目标与领域选择 | Current host plus the owned router/case bridge | A route descriptor without its skill body is unavailable. |
| `reverse-case-continuation` | 继续与案例发现 | Case pointer as authority; bounded discovery index and current host for recovery | Continue with no case cannot return ordinary-development success. |
| `reverse-domain-methods` | 领域正文与困难方法 | Owned domain copies, routing runtime and current host analysis | A packing/anti-debug hint cannot silently drop required hard-target references. |
| `rea-official-methods` | REA原版技能与方法 | Current host reads the installed fixed package skill and selected references | A server catalog without its original usage/recovery instructions is incomplete integration. |
| `rea-mcp-cli-providers` | REA入口与外部后端 | Official REA server/CLI with repository-selected Node and shared provider paths | Catalog visibility is not backend execution. |
| `rea-evidence-persistence` | 原生证据导出与恢复 | Official REA export/import plus original case Evidence refs | A summary projection or transient session ID is not a complete exported bundle. |
| `rea-comparison-proof-ledger` | 原生比较、proof与ledger | Official REA evidence/proof/ledger APIs; independently executed comparison producers | Exit 0 or candidate-only unit tests cannot close original behavior obligations. |
| `spec-official-discovery` | 官方项目阶段发现 | Installed official Spec CLI and integration-aware phase resolver | Handwritten files with official-looking names or only specify init do not prove phase execution. |
| `spec-evidence-native-gate` | 证据到规格和实现门 | Official phase execution plus inherited case/handoff review and native prepare | A mechanical PASS and nonempty review file cannot certify semantic readiness. |
| `spec-converge-feedback` | 实现后收敛和修正 | Current host executes official implement/converge against the actual candidate | Do not edit spec/expected output to make the current candidate pass. |
| `craft-tools-modes-plugins` | 原版工具、模式和插件 | Pinned original engine/MCP plus owned thin launcher and current host permission decisions | The RF35 baseline of 303 engine tools is not 303 successfully exercised operations. |
| `craft-durable-case-project` | 持久分析Project与案例隔离 | Original Craft Project in the outcome case, bound by the owned case-opening adapter | An in-memory MCP Session alone is not persistent project integration. |
| `craft-provider-paths` | 本地工具接线与恢复 | Allowlisted shared provider discovery plus owned Craft state settings | An engines_list path or configured setting is not a successful decompile/debug/device operation. |
| `craft-native-writer` | 真实构建写入与检查 | Current host supplies content; actual native engine uses the reviewed single-writer lease | Generic build tools without a rebuild Inbox/Workspace cannot be represented as a working leased writer. |
| `craft-host-build-orchestration` | 宿主承接独立AI编排 | Current host conversation/progress plus official Spec and native writer; no duplicate upstream AI loop | Do not call standalone rebuild_start expecting another model or direct MCP build_file_write without its required Workspace. |
| `craft-host-questions-consent` | 宿主提问和授权 | Current host user-input and permission flow; original tool effects/errors remain informative | A tool returning missing Inbox/consent_required is not a completed user question or approval. |
| `craft-assets-and-3d` | 图片与3D资产生成条件 | Current host media tools or an explicitly configured compatible external asset provider; native writer integrates resulting files | Directory/tool visibility cannot assert a paid provider key or a functioning 3D generator. |
| `independent-comparison` | 独立行为和界面对照 | Current host plus independent process/UI/runtime comparators and official REA claims where applicable | Unit tests for only the candidate or a screenshot at one state do not establish whole-product equivalence. |
| `failure-cleanup-recovery` | 失败、清理和继续 | Current host case recovery, official provider remediation and owned process runners | Client timeout is not proof of provider cleanup. |
| `deployment-ownership` | 新机安装、迁移和卸载 | Repository bootstrap/runtime identity checks plus owned selected-host lifecycle | Package-only, catalog-only, receipt-only or detected-host-only is not complete deployment. |

## REA：保留方法、后端与证据链

REA同时有官方技能、MCP、CLI和外部分析后端。接上MCP仍不等于接上了Ghidra、Java、
WABT、JADX、浏览器或设备。宿主先读安装包同版本的 `skills/reverse-engineer-anything/SKILL.md`，
按目标读取其原版references；例如普通完整源码仓库的结构解释可以直接使用源码工具，
需要出厂制品、反编译、运行行为和差分事实时才选择相应REA能力。不能为了让四个名字
都出现而重复分析，也不能在真正需要原生能力时让模型手写解析器冒充工具执行。

外部工具路径从本checkout的`state/provider-runtime.json`恢复给MCP和CLI。
`providers --refresh`按allowlist保存现有路径，Python launcher与`rea-run`同源恢复；
不运行shell profile、不导入任意环境或读取凭据，桌面服务不依赖终端后来增加的变量。
`providers`显示配置和存在性，原版工具的真实调用才证明该操作能工作。缺失、被替换、
设备未连接、版本或平台不支持时，保留原因；不能把目录可见当作后端就绪。

实际WABT的WASM分析、JADX的APK/class分析、Ghidra的PE伪代码及跨进程bundle恢复已执行，
见[provider-report](../evidence/rf36/provider-report.json)、
[provider-calls](../evidence/rf36/provider-calls.json)和
[原生bundle](../evidence/rf36/provider-bundle.json)。验证刻意移除了终端provider路径键，
从保存配置启动；不是只在已设好变量的shell中运行后宣称桌面已接通。

原生记录需要跨连接恢复时，执行官方 `export_evidence_bundle`，把完整原件放在当前
成果案例中，再用官方读取/导入接口恢复。摘要视图、聊天摘录或Transient ID不替代完整导出。
保持UTF-8、原ID、authority、coverage、limitations和unknowns。引用清单与SHA检查
不会自行认证原生证据，也不会替原版计算proof或ledger。静态结构partial不因进程退出0变成
运行等价；对应范围的required open、实际proof和独立比较都要保留。

## Spec与Craft：职责互补，不能只登记名字

官方Spec的 `init` 负责生成当前成果项目的工作流；宿主还要执行真正生成的阶段、脚本、
checklists和hooks。发现八个阶段文件不表示它们已经执行。实现前的证据/语义审查和
prerequisites、冻结输入是不同检查，关键未知只阻断受影响需求。实现后按官方converge
读取当前代码和原spec/plan/tasks，追加有来源的剩余工作；不能修改预期掩盖差异。

Craft的RF35目录基准是303个原版engine工具；RF36增加`fusion_case_open`及`fusion_asset_generate`两个自有工具，当前共305个。
它不代表305个操作均已运行，也不代表工具都无需目标、设备、Workspace、Inbox或key。
原版MCP协议、工具结果、分页、Evidence、资源、错误和
可用的插件加载都要保留。Deep模式、toolset和宿主权限要明确；WASM组件插件等编译可选
能力按实际分发声明，不能从MCP插件可用推断所有插件类型都支持。

原版Craft `Project` 是分析持久存储，不是构建Workspace。宿主先使用 `fusion_case_open`
绑定现有成果项目及案例，使Evidence、unknown、investigation、annotations、journal和
目标上下文保存在该案例。新进程重新绑定后要能恢复；切换案例必须隔离旧Session，
不能把A案例记录合并到B案例，或把共享工具仓库当作所有项目的默认成果目录。
目标变化/丢失需要明确报告，不能删除旧研究或假装恢复全部成功。
实际绑定、分析、写brief/finding/handoff、annotation、退出重启恢复、case切换隔离和
变化目标局部拒绝见[craft-memory-report](../evidence/rf36/craft-memory-report.json)及
[craft-memory-calls](../evidence/rf36/craft-memory-calls.json)。
有效Deep模式与保存设置分别报告；MCP补丁源码树独立于native writer源码树。

正式候选仍经过官方Spec与 `native-craft` 冻结租约。真实engine负责Workspace、
write/edit/command/check/summary/cleanup；`session`只是附加边界观察。缺Inbox的普通
Craft MCP不能直接假装它的通用build工具已经绑定正式候选。检查后改动候选必须使旧检查失效。

## 没有原版GUI Inbox时，功能由谁承担

| 原版职责 | 融合后的真实承接 | 需要核实的条件 |
|---|---|---|
| Study/Rebuild、进度、补充要求、修正、停止 | 当前宿主保存原目标并推理；Spec管任务，native租约管实际实现/检查/中止，workflow恢复原批次 | 保留目标、证据、待办、实际调用和失败；不另启一个模型循环；不是只打印命令 |
| `core_person_ask`及操作决定 | 当前宿主对话/用户输入/权限机制 | 无GUI Inbox时明确走宿主；超时不产生回答或授权，已有授权内的正常步骤不重复制造审批 |
| `build_file_write/edit/command` | 原生writer创建真实Workspace与所需Inbox上下文，按冻结租约运行 | 缺Workspace或租约应指出实际入口，不能把missing Inbox视作完成 |
| 图片生成 | 当前宿主现有图片工具，或已配置且兼容的实际资产producer；随后native集成产物 | 先核真实工具、格式、来源和效果，不能把工具名可见当生成成功 |
| 图片/3D原版通路 | `fusion_asset_generate`在绑定case内创建独立暂存Workspace/Inbox，注入显式环境key，调用原版工具和Fal producer | 单次allow/预算和输出，原结果/费用/摘要保留；暂存产物经Spec/native整合，不直接写正式候选；本轮是loopback验证，未付费运行 |
| 模型/密钥配置及独立setup | 当前宿主管模型；本仓库安装器管理自有入口 | 不复制旧密钥、不切换模型、不让原版setup越过归属重写其他宿主 |

原版图片/模型工具还依赖构建Inbox、Workspace、资产允许标志、预算及provider key；
仅链接engine不会自动建立这些条件。当前无Inbox的分析MCP必须报告实际承接入口，
不能把原工具列在目录中就认为该生成路径已经可用。

这里没有宣称真实付费3D已在本轮生成。上游`crates/engines/src/assets/fal.rs`实际实现HTTPS
图片与`tripo3d/p1/image-to-3d`请求、下载及错误处理，不缺底层producer；
`crates/engine/src/tools/asset_tools.rs::job`需要Inbox/Workspace、AssetKeys、允许标志与预算。
当前`fusion_asset_generate`已在单次独立staging中补齐这些上下文，重用原版工具/producer；
专用key仅取显式`REVERSE_FUSION_CRAFT_FAL_KEY`环境，不读旧keychain或接受参数key。
每次限定allow_paid、budget_usd、输出路径，原版估价超预算在网络前拒绝；
原版provider错误保留且清除secret回显。图片与GLB暂存原件/费用/摘要留case，
正式候选由审查后的Spec/native命令集成，不能让资产工具绕过租约。
本地模拟HTTP实测图片、提示到3D、已有图片到3D与拒绝/预算/越界/错误/secret控制，
记录见[asset-report](../evidence/rf36/craft-assets-report.json)及
[asset-calls](../evidence/rf36/craft-assets-calls.json)。
测试模式只允许显式loopback地址并使用假key；默认服务仍使用原版官方HTTPS，未付费运行。
实际服务key/额度/当前任务授权及产物质量属于运行条件和目标验收，不能倒推为未实现connector。
如果用户交付确实需要该资产，必须使用真实通路核实结果或取得明确交付决定。
不能把占位物当完成，也不能写一句“由宿主负责”就视作已经具备不存在的功能。

## 从“能安装”到“能使用”的检查边界

- **静态承接合同**：来源、owner、entry、condition、必需文件和反例齐全；不静默删行掩盖原版能力。
- **部署检查**：固定组件真实安装，所选宿主实际登记；自有更新/卸载和报错回退保留无关设置。
- **具体能力检查**：实际分析、反编译、浏览器/设备或资产调用，读取原版结果及限制；目录数不作替代。
- **目标验收**：对原版/候选独立运行，覆盖声明范围，错误对照会失败；剩余需求仍附着原目标。

新电脑按 [AGENT-BOOTSTRAP](AGENT-BOOTSTRAP.md) 安装固定核心、恢复本机路径并检查所选
入口；不能把PackageOnly、receipt、catalog或CLI发现当完整部署。更新/卸载即使安装
receipt丢失，也要按实际所有权处理自有入口，保留新checkout指针；所有权不明时拒绝破坏。

这些核心检查可使用仓库自有材料和有针对性的反例，不要求用户继续提供样本；宿主
接入差异要核对入口、工具协议、权限、目录和生命周期，不要求每增加一个宿主都登录
模型重跑完整软件复刻。Codex自动登记不等于其他宿主的全局MCP已登记；外部工具、
操作系统和设备条件也不能借其他平台的成功记录直接判通过。

发布记录必须写实际执行了什么、未执行什么，以及哪些条件属于用户环境/目标本身。
主检查通过不能抹去某一行缺接线、失去原版持久能力或只有文档owner却无执行入口的问题。
