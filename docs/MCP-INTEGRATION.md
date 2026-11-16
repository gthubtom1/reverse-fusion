# REA、Craft MCP与现有聚合链路

本文件是RF-36 / 1.4.0的实际工具接入合同。RF-35接通了MCP协议和有限工具调用，
RF-36进一步修复本地provider路径没有带进桌面服务、Craft分析没有绑定持久Project等缺口。
当前安装结果以真实登记、诊断和[CURRENT-STATE.md](CURRENT-STATE.md)为准；
文件存在、CLI可用或工具数量均不代替后端操作。唯一部署入口是
[AGENT-BOOTSTRAP](AGENT-BOOTSTRAP.md)，职责逐项见[INTEGRATION-CONTRACT](INTEGRATION-CONTRACT.md)。

## 原版、旧融合和本轮接入的区别

| 部分 | 固定原版实际提供 | 旧融合的实际边界 | 1.4.0实际承接 |
|---|---|---|---|
| Reverse领域技能 | 路由指令、领域正文、参考资料和辅助脚本 | 本地路由、case、困难目标资料、目标恢复 | 仍是instructions/skills层，不虚构一个名为Reverse的独立MCP server |
| REA | 官方技能/方法、CLI/MCP、外部后端和原生Evidence | RF-34及以前未登记Codex MCP；RF-35有限调用未验证全部后端 | 官方server和同源CLI共用保存的provider路径，读取同版本官方技能；原生bundle实际导出、跨进程导入 |
| Spec Kit | 官方CLI、生成的各宿主项目工作流和脚本 | 官方初始化/阶段执行、冻结spec/plan/tasks、implement/converge | 保持现有工作流，不把Spec称作MCP或用同名自写server替代 |
| Craft | 原生engine/MCP、分析Project、构建Workspace；CLI/GUI另组合AI、setup、Inbox及插件 | native writer已实际运行；RF-35的分析MCP尚缺案例持久绑定 | 原版engine/MCP与运行时MCP插件；`fusion_case_open`绑定原版Project并恢复分析；Spec/native租约继续负责正式候选；独立AI/GUI职责按下表由宿主承接 |

因此，先前四组件CLI/原生构建的完整运行记录仍然有效，但**它们没有证明Codex已经
接入REA/Craft MCP，也没有证明原版完整工具目录已向当前模型可达**。RF-35补的是
这一真实接入缺口，不能只换UI名称或给窄接口添加MCP外壳后宣称原能力全量接通。

## REA使用官方server

固定安装包的`vendor/rea/package/scripts/rea.mjs`在导入普通CLI前分流：
`mcp`或`--mcp`进入`dist/mcp/main.js`的`runEntrypoint()`，通过stdio服务；
带`--http`则走官方HTTP入口。融合默认使用安装时核实的兼容Node绝对路径与固定
entry脚本，参数为`mcp`，不依赖另一项目的cwd或临时npx缓存。

固定6.9.0的真实`initialize`、`tools/list`和`prompts/list`观测为
**255工具、6个prompts**，与固定目录基准核对。这里的数量不是
所有provider已就绪或255项业务效果均通过。原官方`setup`的全局改动流程不作为
融合默认安装的旁路；融合管理自己登记的项，保留其余服务器、设置和凭据。

REA默认紧凑输入schema仍保留完整工具集和canonical校验；输入/输出schema profile
影响描述体积，不应静默删减工具。原生Evidence、coverage、unknown和输出限制继续
读取实际结果；CLI与MCP只是到同一官方能力的不同入口，不能互相伪造运行记录。

### 本地provider接线与重启恢复

两项登记都通过仓库venv的Python执行`scripts/mcp-launch.py`，由它启动固定原版服务。
它继承stdio句柄，不解析或改写MCP消息，并通过本仓库进程所有权机制清理服务及子进程。
安装或显式`providers --refresh`将允许的现有工具路径保存在本checkout的
`state/provider-runtime.json`。`rea-run`、MCP启动器和实际诊断共用同一恢复函数，
因此桌面应用启动时没有某个终端后来设置的变量，也能拿到已经保存的路径。

刷新只发现/校验本地工具路径、固定仓库provider和显式选择；不执行shell配置文件、
不导入任意环境变量、不读取或迁移凭据。部署时的allowlist路径变量和PATH可以作为
发现来源，`--set-path KEY=绝对路径`可以显式选择；这些来源只保存审核允许的路径键。
启动时先去除继承环境中同名provider键，再恢复保存结果，不借临时终端变量冒充接通。
路径丢失或受管WABT/JADX身份改变要报告并刷新，不能继续使用陈旧的绿色回执。

```text
[仓库venv-python] -m reverse_fusion providers --format json
[仓库venv-python] -m reverse_fusion providers --refresh --set-path GHIDRA_INSTALL_DIR=[实际Ghidra目录] --set-path JAVA_HOME=[实际JDK目录] --format json
[仓库venv-python] -m reverse_fusion mcp-check --format json
```

Ghidra/Java、WABT/JADX、浏览器和各具体工具有各自的有效路径键；
实际allowlist以`reverse_fusion/provider_runtime.py`为准。它是路径接线，不是所有后端
安装器或兼容性证明。新电脑重做该机发现，不复制旧机state或绝对盘符。

## Craft的目录不能按宣传数量判断

固定上游README宣传“320 tools”，并明确包含engine及AI/setup层。实际源码分层：

- `crates/engine/src/lib.rs`的`Engine::new`只注册engine工具。
- 原CLI的`apps/craft-anything-cli/src/main.rs`组合engine、
  `craft_anything_ai::tools()`、`craft_anything_setup::tools::specs()`和运行时插件，
  通过`Engine::shared_with`服务。把`Engine::new`暴露为MCP不能称作原CLI所有层的全量复刻。
- `crates/mcp/src/lib.rs`还按toolset、Clean room/Deep和restricted选项过滤可见目录。
  默认只列Core/Essentials及已启用组；`enable_toolset`可增加组并发送
  `notifications/tools/list_changed`。`--all-tools`展开工具组，**不会绕过Clean room或
  restricted过滤，也不代表外部引擎/设备已经可用**。
- `crates/engine/src/settings.rs`中Deep默认关闭，`ask_before_running`默认开启。
  Clean room仅允许从外部观察，Deep可读取目标内部。运行代码、改设备等仍依照原生
  effects/consent约定；模式和授权归属必须在登记配置中明确，不能把数量变化隐藏成漏装。

目录验证应保存当时的上游commit、启动器身份、模式、选项、启用toolset、完整工具名
集合和prompts，再对照对应上游registry。不能在文档里预写“融合必有320个工具”，
也不能凭某次Clean room少于宣传数量就判定漏装。本轮启动器通过`plugins::install`与
`Engine::shared_with(session, case_tools(), runtime_plugins)`保留原版运行时MCP插件，
在303个engine工具上增加`fusion_case_open`及`fusion_asset_generate`两个自有工具；当前基准为**305工具、6个prompts**。
它不是原CLI含AI/setup所有高层工具的全量。README的320是宣传旧统计，不用于相减或
推导当前registry数量；启用插件后新增工具仍按运行时目录另记。

### 有意不加载的原版高层工具

原版AI层17项和setup层4项未装进融合MCP；这是明确替代，不是遗漏后声称全部接入：

| 原版层 | 原始工具ID | 融合中的职责归属 |
|---|---|---|
| AI/rebuild（10） | `rebuild_start`、`rebuild_status`、`project_builder_set`、`rebuild_activity_show`、`rebuild_note`、`rebuild_note_withdraw`、`rebuild_stop`、`rebuild_question_ask`、`rebuild_questions_list`、`rebuild_check` | 当前宿主保留目标/推理/问答，官方Spec及native冻结writer完成实现/检查/恢复；不另启原版后台模型循环 |
| AI/key（3） | `assets_key_status`、`assets_key_set`、`assets_key_remove` | 不加载原版密钥管理、不读旧keychain；`fusion_asset_generate`只从显式服务环境注入专用fal key，key不进入工具参数/日志/回执 |
| AI/model（2） | `ai_models_list`、`ai_model_set` | 使用当前宿主模型，不由Craft发现/切换另一套后端 |
| AI/model options（2） | `ai_model_options_show`、`ai_model_options_set` | 当前宿主管理自身模型上下文配置 |
| setup（4） | `setup_plan`、`setup_apply`、`setup_doctor`、`setup_uninstall` | 本仓库安装器/诊断/卸载只管理自有登记，避免另一安装器重写其他宿主配置 |

源位置分别为`crates/ai/src/rebuild/tools.rs`（含`QUESTION_TOOL`常量）、
`key_tools.rs`、`model_tools.rs`、`model_options.rs`与`crates/setup/src/tools.rs`。
因此不能将“320－303”当作被排除层数量，实际分层必须从源码注册列表核对。

Craft MCP本身提供工具调用、Evidence和investigation resources、guided prompts、
进度与取消；原生错误以实际结构返回。原版还含浏览器/CDP、网站、Android/ADB、
Frida、native/.NET/Java、Apple、固件、数据库等工具组。是否可以调用某项取决于
具体target、OS、可执行程序/外部引擎、设备、会话及当前授权，必须保留真实缺失理由。

### 融合默认登记的运行模式

RF-35对照发现，仅传`--all-tools`并不能让逆向内部分析工具可达：本机Clean room
目录观测为88项，并不包含`core_target_open`。这是原版Clean room过滤的结果，
不是`--all-tools`失效或引擎未编译。具体目录、次数与身份以RF-35实际记录为准。

融合的Codex默认登记显式传`--all-tools --deep-mode --allow-run`：

- `--deep-mode`只设置该服务进程的`session.deep_for_run`，使原版内部分析工具可用，
  不改用户原版Craft配置或替其他进程开启Deep。它表明此接入用于用户要求的实际逆向分析。
- `--allow-run`沿用原版MCP语义：服务信任外部宿主负责调用授权。没有原版GUI审批
  inbox时，若始终保留`Consent::NotAsked`，所有需要执行/设备变更的工具会持续返回
  `consent_required`，仅“目录存在”无法用于实际任务。
- 这不授予模型对任意目标的全局许可。Codex仍须按用户当前任务、环境和宿主审批
  决定是否调用；具体服务、设备和持久影响操作不能由工具可见性推定已获授权。
- 启动器不传`--deep-mode`或`--allow-run`时，分别保留Clean room和原版未授权拒绝行为；
  可以显式选择这种模式，不用修改上游工具实现来凑目录或吞掉拒绝错误。

展开全部工具组、开启内部分析能力与授权某次真实调用是三个不同决定。当前宿主
继续负责推理和权限判断；这些参数不启动第二模型，也不绕过现有Spec/native租约门。

### Craft分析先绑定原版Project

首次分析或服务器重启后，先从bridge恢复当前成果项目/case，再调用：

```json
{"project_root":"<成果项目绝对路径>","case_root":"<该项目内已存在的case绝对路径>"}
```

工具名是`fusion_case_open`；case目录由bridge建立，相对case_root需先解析为绝对路径。
它在case内创建或打开`craft-analysis.cany`，使用原版Project保存Evidence、unknowns、
investigation、annotations和journal，并保存原版目标上下文。绑定不是候选Workspace，
也不会启动Rebuild。未绑定时分析/调查更新明确拒绝；设置和诊断仍可使用。

重新连接同case恢复原生ID和研究；切换case建立全新Session后只装入选中Project，
不合并前一case记录。缺失或变化的目标以`unavailable_targets`明确返回并另存，
其他目标和保存的研究继续可用。没有明确导出的旧未绑定分析不得静默并入新case。
默认登记拒绝把共享工具checkout变成成果项目，输出放当前成果项目。

`engines_list.deep_mode.enabled`现在报告实际进程模式，`saved_enabled`单独保留保存值。
MCP使用独立`vendor/craft/mcp-upstream`补丁树，避免其持久绑定改动破坏既有native writer重建。

### GUI/AI职责的真实替代与可选扩展

| 原版运行条件或职责 | 当前实际入口 | 不能混淆的边界 |
|---|---|---|
| 独立Study/Rebuild、进度、补充要求与停止 | 当前宿主对话/任务恢复，官方Spec，native `prepare/build/check/refine/abort` | 不启动第二模型；实际native执行不由目录或流程图替代 |
| `build_file_*`、`build_command_run`所需Workspace/Inbox | 冻结native租约在独立构建进程建立真实Workspace和Inbox | 分析Project不提供构建Inbox；不能直接调用分析MCP中的build工具绕过租约 |
| `core_person_ask`、GUI审批卡片与操作决定 | 当前宿主用户输入/权限机制 | 分析MCP无GUI Inbox；`feature_missing`不等于问题已问出，超时不产生新授权 |
| 图片生成 | 当前宿主实际图片工具；生成后记录来源、格式并按冻结任务集成 | 不宣称原版`assets_image_generate`在分析MCP已能直接运行 |
| 图片/3D原版通路 | `fusion_asset_generate`建立单次case内staging Workspace/Inbox、显式预算和AssetKeys，调用原版图片/3D工具及Fal producer | 必须先绑定case并明确本次付费允许；结果不直接写正式候选，后续经审查的Spec/native命令整合；本轮只验证本地模拟服务，未消耗真实额度 |
| 原版模型设置、密钥、setup | 当前宿主模型与本仓库归属明确的安装器 | 不复制凭据，不运行另一安装器重写宿主 |

具体来源：`crates/engine/src/tools/asset_tools.rs::job`先要求构建Inbox/Workspace，
再要求`AssetKeys`、允许生成和预算；`crates/engines/src/assets/fal.rs`已经实现图片与
`tripo3d/p1/image-to-3d`请求和产物下载。原CLI的`mcp --inbox`会注入Inbox并从原版
keychain装入AssetKeys；本融合不执行这条keychain通路。当前通过新增适配工具执行：

```json
{"kind":"model3d","prompt":"一个待生成物体的描述","save_as":"models/object.glb","budget_usd":1.0,"allow_paid":true,"faces":1000,"textured":true}
```

工具名`fusion_asset_generate`，`kind`为`image`或`model3d`，图片输出`.png`，模型输出`.glb`。
模型也可提供`image`为当前case内的相对图片路径或显式HTTP(S)图片URL。
服务进程只读取显式`REVERSE_FUSION_CRAFT_FAL_KEY`；不能把key放在上述参数、提示或路径中。
宿主必须先确认实际任务允许付费生成，`allow_paid`不是自动获得用户授权。
每次调用建立全新`<case>/asset-staging/asset*/`，估价超出本次预算在网络请求前拒绝；
原版Workspace继续记录费用和资产。结果返回产物摘要、原工具结果和独立回执。
暂存区不是正式候选，后续依照Spec/native审查输出和命令整合，不能绕过租约。
缺key准确返回`bad_settings`，未绑定case要求`fusion_case_open`，原始provider错误保留并清除credential回显。

实际原版Fal HTTP producer经显式loopback服务验证图片、提示生成3D、已有图片生成3D，
以及允许/预算/路径/错误/secret拒绝和候选不变，见
[asset-report](../evidence/rf36/craft-assets-report.json)与
[asset-calls](../evidence/rf36/craft-assets-calls.json)。这是接线和失败控制验证，不是付费服务质量承诺。
`--asset-test-base`仅维护者显式loopback测试，使用固定假key，不读取真实key，默认登记不传此参数。
原版MCP插件保留；WASM组件插件是未编译的可选feature。

## 工具如何与现有Spec及native租约协作

```text
当前智能体读取Reverse路由与领域指令，保留同一原始目标/case
  -> 按问题选择REA MCP、Craft MCP、现有CLI或其他可用工具调查与比较
  -> 原始工具记录/Evidence + 语义就绪审查
  -> 官方Spec项目工作流，冻结研究与任务
  -> 现有native-craft租约写候选、运行冻结检查、修正、summary/cleanup
  -> 独立原版/候选比较与实际REA proof/ledger，更新任务/converge并交付
```

两个MCP扩展的是模型可发现、可调用的原版工具面。现有native租约仍负责正式候选
写入与冻结检查，不能被MCP内通用写入/运行工具绕过。工具有重叠时由当前宿主依据
问题、来源、环境与已得证据选择，不固定每个步骤必须重复调用两套工具。

当前宿主继续负责推理，安装不启动第二模型或重复Study/Rebuild代理循环，不读取或
复制原版AI密钥来完成接入。原版AI/setup高层工具按上表有意不加载；外部服务调用
仍由当前任务范围决定，不能通过其他工具可见性扩大原授权。REA和Craft各自原始
Evidence保留其格式/ID，跨组件引用明确标注来源，
不把Craft记录改名为REA proof，也不新造一份与原case冲突的完成账本。

## 新电脑部署和当前对话重载

新电脑的Windows x64/Codex默认完整安装同时完成：固定REA官方server、固定Craft
MCP薄启动器、已有官方Spec和native-craft组件、Reverse入口、两项自有MCP登记及诊断。
Pi/Claude当前仍是项目adapter＋CLI/native组件接入，未自动写入它们的全局MCP配置；
不能把三宿主项目连接检查说成三宿主全局MCP都已登记。未来需要时按各宿主实际
协议配置映射和验证，不复制Codex配置，也不要求重做核心业务样本。
只安装包、只跑CLI或只登记server都不能替代完整接入检查。宿主适配仍按入口/工具
协议检查与代表性核心运行，不要求每个新宿主再完整复刻一个样本。

Codex注册只管理本仓库拥有的命名项，保留无关MCP、宿主凭据和模型设置；更新和
卸载需要按归属管理这些项。实际命令和本机路径由安装位置生成，不把本机缓存路径
或其他电脑的盘符当作配置。其他宿主读取自己的登记约定，不复制Codex配置文件。

配置登记完成后，当前聊天的工具清单可能仍是会话开始时的快照。按宿主要求重载
服务、重开对话或重启应用后，重新确认工具可发现。**不能因为配置文件已写入，
就声称当前聊天已经热加载；独立协议诊断成功也不能替代宿主当前会话加载确认。**
重载前可以记录“注册及独立协议诊断已完成，当前会话加载待刷新”，不能混写为缺包。

## 检查结果要分四层

| 层次 | 可以证明 | 不能据此推导 |
|---|---|---|
| 固定资产安装 | server/启动器/运行时及来源身份存在 | 宿主已加载 |
| 宿主登记与协议诊断 | 托管配置、initialize、目录/提示/资源协议可达 | 当前旧聊天已刷新，或每个工具已实际执行 |
| 具体工具运行 | 某次真实调用的输入、输出、错误、耗时与覆盖 | 其余工具/provider均可用 |
| 业务验收 | 当前目标在所声明范围的独立比较与修正结果 | 所有未来目标、平台或保护器预先通过 |

例如ADB工具列出来不等于有设备，Ghidra工具列出来不等于引擎安装，浏览器工具列出
来不等于已取得CDP连接；Apple runtime在不支持的OS上仍应保留`wrong_os`等实际
限制。诊断只做本机已有、经过审查的有限调用，不安装全部外部工具或运行未知目标。

## RF-36实际操作与恢复证据

[provider-report](../evidence/rf36/provider-report.json)、
[provider-calls](../evidence/rf36/provider-calls.json)和
[provider-bundle](../evidence/rf36/provider-bundle.json)记录真实官方REA服务操作：
WABT分析WASM、JADX分析APK/class、Ghidra打开自有PE并生成`main`伪代码；
完整原生bundle含6条记录，退出后在新进程导入，原ID和链接保留。
运行前移除了终端的allowlist provider变量，再经Python launcher恢复已保存路径；
两次进程均有Job清理记录。这证明选定后端和证据恢复可用，不证明设备、动态运行或业务等价。

[craft-memory-report](../evidence/rf36/craft-memory-report.json)与
[craft-memory-calls](../evidence/rf36/craft-memory-calls.json)记录实际原版Project绑定、
JS分析、brief/finding/handoff/unknown、native annotation和journal，随后退出重启恢复。
同连接切换案例无旧记录串入，目标变化局部拒绝恢复，已存研究继续存在；实际Deep为true而保存值为false。

RF-35的[有限MCP资格](../evidence/rf35/tool-qualification.json)、浏览器捕获和
[远端干净安装](../evidence/rf35/clean-install.json)是历史范围证据，不能替代上述RF-36
provider和Project修复。工程回归、当前部署和远端版本以本轮发布绑定记录为准，
不在此预写固定通过数量，也不把305工具当全部provider健康。

## 本轮对照的固定源码

- REA固定包6.9.0：`vendor/rea/package/README.md`的Quick start/Set up your agent，
  `scripts/rea.mjs`的MCP分流，以及包内`mcp.json`。
- Craft固定commit`8374ad71544f2cc44698ea74ef990aa31600bac6`：`README.md`的
  Agent-ready/Clean room or Deep/Built for agents/Under the hood，
  `crates/mcp/src/lib.rs`的`ServerOptions`、`tools_list`、`listed`、`call_engine`和resources/prompts，
  `crates/engine/src/settings.rs`、`lib.rs`、`session.rs`及`tools/mod.rs`，
  `apps/craft-anything-cli/src/main.rs`的engine组合和`crates/ai/src/lib.rs::tools`。
- 本仓库边界：`components/craft-native/src/main.rs`的租约操作与
  `components/craft-mcp/src/main.rs`的stdio薄启动器。原版工具覆盖以实际registry
组合为准，不能仅从这两个二进制都链接同一engine推断目录相同。

上游工作树和运行时为安装时获取的固定来源，未跟踪文件的本机存在不替代新机分发。
当前修复、诊断和宿主加载结果分别写入RF-36 checkpoint与证据；先前CLI记录保持其
实际范围，不回写成当时已完成MCP接入。
