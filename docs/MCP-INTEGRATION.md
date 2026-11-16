# REA、Craft MCP与现有聚合链路

本文件记录RF-35对照固定上游源码后修复的工具接入边界。当前安装结果以本次
MCP注册记录、诊断和`CURRENT-STATE.md`为准；文件存在、CLI可用或本文件描述均不
等于当前对话已经加载服务。部署步骤统一由[AGENT-BOOTSTRAP](AGENT-BOOTSTRAP.md)维护。

## 原版、旧融合和本轮接入的区别

| 部分 | 固定原版实际提供 | RF-34及以前融合已用到的部分 | RF-35部署必须补齐的接入 |
|---|---|---|---|
| Reverse领域技能 | 路由指令、领域正文、参考资料和辅助脚本 | 本地路由、case、困难目标资料、目标恢复 | 仍是instructions/skills层，不虚构一个名为Reverse的独立MCP server |
| REA | 同一包同时提供CLI和官方MCP server；官方setup会登记MCP并安装工作指引 | 已装固定包、CLI分析、原生Evidence，以及启动服务的诊断；未登记到当前Codex | 默认登记固定包的官方stdio server，让当前宿主可发现原工具和prompts |
| Spec Kit | 官方CLI、生成的各宿主项目工作流和脚本 | 官方初始化/阶段执行、冻结spec/plan/tasks、implement/converge | 保持现有工作流，不把Spec称作MCP或用同名自写server替代 |
| Craft | 原生engine及官方MCP协议；CLI/GUI还组合AI、setup与插件扩展层 | 自有native seam真实执行受租约约束的候选写入、检查与清理；未向宿主提供原版分析工具目录 | 默认安装复用固定engine和官方MCP协议的薄启动器，登记当前宿主；明确原版层次和实际覆盖，不用窄native构建接口冒充整个MCP |

因此，先前四组件CLI/原生构建的完整运行记录仍然有效，但**它们没有证明Codex已经
接入REA/Craft MCP，也没有证明原版完整工具目录已向当前模型可达**。RF-35补的是
这一真实接入缺口，不能只换UI名称或给窄接口添加MCP外壳后宣称原能力全量接通。

## REA使用官方server

固定安装包的`vendor/rea/package/scripts/rea.mjs`在导入普通CLI前分流：
`mcp`或`--mcp`进入`dist/mcp/main.js`的`runEntrypoint()`，通过stdio服务；
带`--http`则走官方HTTP入口。融合默认使用安装时核实的兼容Node绝对路径与固定
entry脚本，参数为`mcp`，不依赖另一项目的cwd或临时npx缓存。

本轮固定6.9.0的真实`initialize`、`tools/list`和`prompts/list`观测为
**255工具、6个prompts**，与固定目录基准核对。这里的数量不是
所有provider已就绪或255项业务效果均通过。原官方`setup`的全局改动流程不作为
融合默认安装的旁路；融合管理自己登记的项，保留其余服务器、设置和凭据。

REA默认紧凑输入schema仍保留完整工具集和canonical校验；输入/输出schema profile
影响描述体积，不应静默删减工具。原生Evidence、coverage、unknown和输出限制继续
读取实际结果；CLI与MCP只是到同一官方能力的不同入口，不能互相伪造运行记录。

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
`Engine::shared_with(session, Vec::new(), runtime_plugins)`保留原版运行时插件/provider
扩展，真实Deep目录为**303个engine工具、6个prompts**。这是原版engine工具面，
不是原CLI含AI/setup所有高层工具的全量。README的320是宣传旧统计，不用于相减或
推导当前registry数量；启用插件后新增工具仍按运行时目录另记。

### 有意不加载的原版高层工具

原版AI层17项和setup层4项未装进融合MCP；这是明确替代，不是遗漏后声称全部接入：

| 原版层 | 原始工具ID | 融合中的职责归属 |
|---|---|---|
| AI/rebuild（10） | `rebuild_start`、`rebuild_status`、`project_builder_set`、`rebuild_activity_show`、`rebuild_note`、`rebuild_note_withdraw`、`rebuild_stop`、`rebuild_question_ask`、`rebuild_questions_list`、`rebuild_check` | 当前宿主保留目标/推理/问答，官方Spec及native冻结writer完成实现/检查/恢复；不另启原版后台模型循环 |
| AI/key（3） | `assets_key_status`、`assets_key_set`、`assets_key_remove` | 资产生成/密钥由当前宿主已有能力与用户配置负责，不复制或另管原版AI密钥 |
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

## RF-35本机实际资格与待收口事项

`evidence/rf35/tool-qualification.json`、两份catalog及`*-mcp-calls.json`保留本轮
真实stdio连接和调用。REA的`binary_session`、自有Web应用分析已执行，原生分析
含partial/static限制，不能提升为完整运行等价。Craft实际执行`core_target_open`、
`js_app_map`、`engines_list`，并使用Chrome打开自有页面、1100/390双尺寸捕获、关闭。
截图记录仍有one_state等原版limitations，不代表所有交互状态验收通过。

现场provider发现包括Ghidra、Chrome、adb；JADX未被发现，需要目标任务另行准备。
provider被发现仍不代表有Android设备、授权服务或每个动态工具已实际运行，不能
宣传“全provider ready”。原版插件/provider配置在本checkout独立state保存，
重启设置恢复检查单独留证，不修改用户原版Craft配置。

`evidence/rf35/config-preservation.json`记录原无关配置5189字节完整保留，仅新增
两项自有登记。工程回归最终数量以`release/verification.json`为准，部署门与绑定
结果见`evidence/rf35/deployed-release.json`；远端新克隆的默认安装仍需最终记录确认，
本机成功不提前充当该轮远端复现。当前聊天工具发现仍按重载后的真实状态确认。

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
当前修复、诊断和宿主加载结果分别写入RF-35 checkpoint与证据；先前CLI记录保持其
实际范围，不回写成当时已完成MCP接入。
