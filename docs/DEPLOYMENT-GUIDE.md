# Reverse Fusion 部署与使用指南

这份指南是交给任意 Codex、Pi、Claude Code 或兼容 coding agent 的部署契约。
它不假设固定盘符、固定用户目录、固定 shell、固定 Python 路径、固定智能体
工作区或固定模型。智能体必须先发现本机能力，再选择本机可用的命令和 provider。

## 产品边界

Reverse Fusion 是一个独立的 GitHub 产品仓库。它拥有 Reverse 路由、case
生命周期、宿主适配、Builder transport、Evidence/Spec/acceptance 合同、
runner、文档和状态记录。REA、Spec Kit、JADX MCP、WABT 等官方组件保留
官方身份，通过 manifest、bootstrap 和 adapter 接入。旧 reverse-skill、旧
installer、旧 REA/Craft/Spec Kit 安装及宿主全局配置是只读外部环境。

模型、账号和 provider 始终属于当前宿主：

- Codex 使用当前 Codex 登录状态和当前模型。
- Pi 使用当前 Pi provider、账号和模型。
- Claude 使用当前 Claude 登录状态、provider 和模型。

仓库不选择模型、不下载模型、不把模型名称写入路由条件。provider 或登录
缺失时，智能体记录 `blocked`、`unsupported` 或 `unknown`，继续完成与该能力
无关的工作。

## 给任意智能体的部署提示词

把仓库 URL 和下面的指令一起交给智能体：

```text
把这个 GitHub 仓库部署到当前工作区：
https://github.com/gthubtom1/reverse-fusion

先读取 README.md、AGENTS.md、docs/DEPLOYMENT-GUIDE.md、
docs/PRODUCT-GOAL.md、docs/CURRENT-STATE.md、docs/DECISIONS.md、
docs/PROVIDER-STATUS.md、docs/TARGET-CAPABILITY-MATRIX.md、
SOURCE-MANIFEST.json、components/official/manifest.json 和最新 checkpoint。

先发现当前 OS、架构、shell、Python、Node、Java、.NET、Android SDK、
Codex/Pi/Claude CLI 和可用 provider。不要假设固定路径；所有路径使用当前
工作区的绝对路径计算。

先执行仓库本地的 contracts、plan、doctor 和 handoff 检查，再按当前宿主
选择可用安装入口。安装只写仓库自己的虚拟环境、vendor、state 和 case 目录，
不修改旧仓库、旧安装、宿主凭据或全局配置。

normal-dev 是主项目的默认基线。开发过程中如果需要研究另一个网站、APK、
桌面软件、API、协议或其他项目，创建隔离的 analysis/reconstruction subcase；
不要把 subcase 的临时 candidate 写回主项目。只有经过 Evidence 支持的结论、
接口约束或 Spec tasks 才能回到主项目。

不要把逆向工作固定成单一顺序。根据目标能力选择静态分析、动态观察、dump、
脱壳、hook、模拟、设备或其他 provider；Reverse 路由负责分类和上下文，REA
负责证据，Builder 只执行冻结任务，acceptance 保留 pass/fail/unknown。

不要把工具可见、exit 0、Craft Ready 或模型自述写成业务通过。
完成部署后报告实际工作区、安装入口、provider 状态、未满足能力和下一步操作。
```

## 智能体部署步骤

1. **发现工作区和宿主**

   智能体先确定当前仓库根目录、OS、架构、shell 和可用命令。仓库脚本使用
   当前脚本位置计算相对路径；不要把 `C:\...`、`/home/...` 或某个固定用户目录
   写进项目配置。

2. **运行只读检查**

   ```text
   python -m reverse_fusion contracts
   python -m reverse_fusion plan --client auto --intent normal-dev --format json
   python -m reverse_fusion doctor --format json
   python -m reverse_fusion handoff --check --format json
   ```

   如果系统没有 `python` 这个命令，智能体使用本机对应的 Python launcher，
   并把实际命令记录在部署报告中。Plan 和 doctor 不启动 provider，也不写全局
   配置。

3. **创建仓库本地安装环境**

   Windows 使用 `scripts/install.ps1`，Linux/macOS 使用 `scripts/install.sh`。
   两个入口默认只使用仓库内的虚拟环境；先 dry-run，再根据宿主实际情况执行
   apply。Linux/macOS 如果默认命令名不是 `python`，可通过 `RF_PYTHON` 指向
   当前 Python 3.11+ launcher。REA、WABT、JADX 等较大的 provider 由各自
   bootstrap 按 manifest 校验，只落在仓库 `vendor/`；当前 WABT/APK/REA
   vertical runner 以 PowerShell 为主，POSIX 宿主由 agent 选择等价的本机
   provider 命令，或明确记录 `unsupported`/`blocked`。核心路由、领域技能、
   contracts、case 和普通开发仍可独立使用。

4. **完成正常开发部署**

   部署完成后，智能体可以直接在当前工作区和用户对话。普通开发不强制创建
   Reverse case，也不强制启动 REA 或 Builder。需要时再创建嵌套 subcase。

5. **创建嵌套分析或复刻 subcase**

   路由后读取 `RULES.md`、返回的 `skill` 和 `required_reads`。
   `missing_support` 非空时处理缺失资源。困难迹象来自任务文本或后续证据时，
   按 `components/reverse-core/runtime.json` 加载资料，不固定工具顺序。
   `contracts` 同时核对来源文件和有意适配清单。CTF/Burp 源码随仓库保留，
   运行工具按需准备；本机生成的工具索引属于被忽略的本地状态。

   ```text
   当前主项目继续保持 normal-dev。
   创建一个隔离 subcase：
   - 目标：[target path or URL]
   - 目的：[analysis / reconstruction / comparison]
   - 需要回到主项目的结果：[接口、行为、设计经验、Spec task 或 candidate]
   只把经过 Evidence 支持的结果带回主项目。
   ```

   subcase 使用独立的 case root、route、Evidence、Spec tasks、candidate 和
   ledger。需要持久化路由和恢复点时使用 `bridge --record`；它会在仓库内的
   case root 写入 `case.json`，并拒绝越过仓库边界的路径。主项目源代码、构建
   目录和工作树保持隔离。

## 对话中的动态工作方式

Reverse Fusion 不是一条强制的“每次都要走完整逆向流程”的流水线。智能体根据
   用户目标和当前证据动态组合能力：

- 只想了解外部网站行为：创建 analysis subcase，只做静态/动态观察和报告。
- 想学习一个参考项目的接口：先做 analysis subcase，再把已确认的接口约束转成
  主项目 Spec task。
- 想复刻某个功能：升级为 reconstruction subcase，冻结任务后调用 Builder、
  构建 candidate、运行和 comparison。
- 正在开发 APK、桌面软件或服务端项目，中途发现相关依赖：创建对应目标族的
  subcase，不要求主项目整体切换成 APK 或 Native 模式。
- 遇到壳、混淆、反调试或 provider 缺失：选择合适 probe；若仍缺证据，留下
  unknown 和下一步 probe，不把静态相似度当成等价结论。

## 组件调用关系

```text
主项目对话
  -> normal-dev host-native baseline
  -> 按需创建 subcase
       -> Reverse local route/case
       -> REA official Evidence
       -> Spec Kit project tasks
       -> 当前宿主 Builder/model
       -> candidate build/run
       -> original/candidate comparison
       -> proof + obligation ledger
  -> reviewed result 回到主项目
```

Reverse 是唯一的 route/case owner；REA 是 Evidence owner；Spec Kit 是任务和
项目意图 owner；Builder 是单一 candidate writer；acceptance 是独立验证面。
这种职责划分防止多个上游工具争夺同一个主项目路由。

## 二开、增强和上游更新

本项目不要求永远保持上游原样，也不要求上游每次更新都同步。更新流程是选择性
的，而不是定时镜像：

1. 用户提出“检查上游更新”时，智能体读取 `SOURCE-MANIFEST.json` 和
   `components/official/manifest.json`，记录当前 pin。
2. 智能体只读比较上游 commit、release、schema、API、provider 行为和 changelog，
   不直接合并。
3. 对每个上游变化回答：它是否解决本项目真实 capability gap？是否改善当前目标
   族？是否会破坏本地 route、Evidence、Spec、Builder 或 ledger 合同？
4. 没有帮助的上游变化保持原 pin，不做更新。
5. 有帮助的变化先建立 detached comparison 或本地 patch，运行 focused tests、
   代表性 acceptance、fresh-clone 检查和 rollback 检查。
6. 只有结果改善且合同保持兼容时，才更新本地 manifest、adapter、checkpoint、
   provider status 和 handoff。

当前策略：

- Reverse core 已经是本仓库拥有的增强实现，可直接继续二开。
- REA 默认保持官方；出现重复且有 Evidence 的能力缺口时，再做本地 adapter 或
  受控 fork。
- Spec Kit 默认保持官方 CLI；项目级 artifacts 和连接逻辑由本仓库维护。
- Craft 使用本仓库的 bounded adapter、patch identity 和 host-owned Builder；
  native backend 只有在实际资格化后才提升为产品路径。
- JADX/WABT 使用官方版本和 checksum manifest；需要更新时选择性比较并重新验收。

## 卸载和回滚

卸载默认只生成计划。apply 模式只删除或更新仓库自己的 state、虚拟环境和
vendor 资产；宿主凭据、旧项目和全局配置保持原样。回滚优先恢复最近一次
reverse-fusion Git commit，再恢复对应的 manifest、checkpoint 和 provider
状态记录。
