# RF-25 全量复核与修复

日期：2026-11-15。基线：`2bcb7d4bdc02b1edcde5855c40445590822d415c`。
当前发布结果以 `CURRENT-STATE.md`、`FINAL-RELEASE-ACCEPTANCE.md` 和
`checkpoints/RF-25-20261115-001.md` 为准。

## 审查方法与覆盖

先拆成入口/文档、核心代码/合同、上游/provider/Evidence 三个独立分区，再由主代理
整合修复，另一个独立代理复审变更与负控。最终文档又单独统一了一轮。
初始全文件清单逐字节读取了当时 832 个 tracked 文件（约 7.76 MB），60 份 JSON
均可解析；最终新增文件还进入发布前索引、链接、摘要与 fresh-clone 检查。

“全量”包括完整文件清单读取、来源对比、引用检查和分区语义审阅，不表示每一行
继承资料都做了独立人工证明，更不表示所有目标/工具/平台已执行。603 个来源文件
逐份对比 pinned enhanced Reverse，核心代码与调用链做行为审查，代表性 provider
链实际执行。未执行的目标与 provider 范围单独列明。

## 发现与处置

| 实际问题 | 修复与直接验证 |
|---|---|
| 唯一部署交接只在未跟踪工作树，GitHub clone 缺失 | 发布 AGENT-BOOTSTRAP，由 README/AGENTS 明确引用；远端 fresh clone 验收 |
| shell 无执行位、Evidence 导航缺页、当前文档互相冲突 | 保存 100755；补归档说明；统一 RF-25 当前状态，历史 checkpoint 保留历史身份 |
| 旧文本 smoke 被称为 APK 生成，任务 ID 与输入不完整 | 降为历史 transport 观察；当前会话从冻结任务/研究生成八个实际源码文件，保存 receipt/输入版本/候选摘要 |
| Builder 漏掉既有文件修改/删除和旧候选，refine 上下文丢失 | 比较完整摘要 delta，拒绝 stale/越界/链接；refine 保留冻结上下文；.git 变化也计入；反例测试 |
| 子 Codex 长提示词触发 Windows argv 上限 | 使用 stdin；额度/登录/超时分别记录 blocked，超时不宣称完整 cleanup |
| session/CLI/state/case 链接可能越界 | 核最终 canonical 路径；冻结输入漂移、顺序、stale、目录/叶子 symlink 负控 |
| POSIX venv traversal 与 receipt 外链删除 | realpath 后限仓库内，首次删除前核 receipt；Git Bash 外链拒绝与正常卸载均实跑 |
| 旧 Evidence 为替换路径破坏身份，Web 缺 proof、APK ID 摘要截断 | 从真实运行重建；官方 parseEvidence/bundle、所有 links 闭合及实际 tamper 拒绝；manifest 作为唯一 ID 索引 |
| WASM 只比 subject SHA，接受改写 interface/失败 envelope | 要求 ok=true，并通过官方 codec 认证后比较与实跑；真实篡改负控返回 unknown |
| .NET path CLI 比较引用未导出的内部 member IDs | 经官方 MCP 对精确留存的两侧 member Evidence 比较；归档所有父记录 |
| proof 实现与继承技能的官方-only规则矛盾 | 明确窄范围、本仓库归属的 integration serializer 适配；实跑计算 passed；不改原生 closure；官方 CLI 独立建 ledger |
| Web 为闭合缩窄图却没有独立保留完整 ledger | 原样保留完整 analysis/comparison links；有限 export ledger ready；完整 graph ledger unknown/4 required open 单独归档 |
| runner 未核 native exit，可能消费旧 JSON | 每步检查退出码、重置输出、核最终 ledger；WASM 显式检查预期 0/1/2 |
| provider 写路径/删除目标无完整 containment | bootstrap、输出及清理核实际路径；写入限定本仓库 vendor/state |
| schema/validator/producer、descriptor、保全组数不一致 | 合同字段与类型统一；descriptor 身份与 skill 核对；来源计数/摘要及反例测试 |
| reconstruction 测试缺 VERSION、技能 hash 过时 | 产品 1.0.0 与领域合同 1.9.0 分开；审查后更新摘要；39 项测试通过 |
| Node engine 放宽、Spec 版本混写、Craft patch 未分发却称完整 | 保留官方精确 engine；拆 source/历史执行版本；Craft 明确 interface-only，companion unobserved，native R46 unsupported |
| 卸载/回滚文档承诺大于实现 | 明确 venv/receipt 删除、vendor/case 保留；移除不存在的 transaction journal 声明 |

## 当前有意适配与来源

增强来源 `gthubtom1/reverse-skill@3fdbb927b474dc23ef2e19403d5464dcb9702cec`。
保留 skills 453、CTF 136、Burp 14，共 603 个文件；590 个来源内容一致，13 个
记录适配（9 个集成改动、4 个空白清理）。困难目标方法与 helper 没有删减。
完整原因/上游与本地摘要在 `components/reverse-core/preservation.json`。

旧来源的根政策、Kali/global installer、发布 CI 与部分示例不作为当前产品安装依赖。
继承的 `verify-repository-security.py` 检查原仓库根政策/CI/二进制白名单，在本产品
布局中并非适用的 release gate；它的未通过不被隐藏或写成安全通过。
`docs/SECURITY-REVIEW-2026-09-03.md` 只引用固定上游历史报告。本轮通用链接检查
读取 Git index，新增文档必须先纳入 index；payloader 的五层相对链接本身正确。

## 有限验收

- 产品 37 项测试（含 192 条路由期望），reconstruction 39 项测试。
- 44 个原路由/178 个原始兼容 case；16 项困难目标决策合同 eval。
- 当前会话冻结 4 份输入，生成 8 个源码文件，check/refine/finish 观察完成。
- WASM pass/fail/unknown；Web 四组有限重放；.NET 两侧构建及四组运行；APK 构建
  与 manifest/member 静态投影。每条链有独立官方 ledger。
- 官方 Evidence 认证共 28 个去重记录（四目标分别 6/8/7/7），引用闭合，四组篡改
  反例被拒绝；40 份目标归档文件及 Builder 冻结/源码摘要核对。
- 只读 CLI sentinel：Pi pass，Codex credits blocked，Claude login blocked，已知
  全局配置摘要无变化。此探针不替代指令加载或目标业务验收。
- PowerShell 语法、Git Bash 安装/卸载及路径边界；remote fresh clone 的最终结果
  与提交身份保存在 RF-25 checkpoint。

## 保留范围

完整 Web graph 有 4 个 required open；APK 设备运行、方法体等价与 Activity 启动
未知。Craft native R46、Windows REA PTY descendant cleanup 未资格化。
当前会话 file observer 不提供 OS 级写入沙箱，已返回子进程不等于证明所有后代退出。
Linux/macOS 物理主机及全部受保护目标未逐一执行。它们属于目标/provider 状态，
不是用旧 smoke 或单个 pass 填平的缺口。

本轮在有限门完成后停止；后续只做实际目标任务或有明确收益的上游增量维护。

## RF-26 聚合架构补充复核

RF-25 之后的独立复核发现，Reverse 内容保全和代表性链路已通过，但旧 `bridge`
返回的主要是一次性 route 结果，混合领域、R46 复刻阶段和 follow-up 依赖 agent
记忆。RF-26 已补上最小机器可观察合同：

- `components/reverse-core/routing.json` 是默认路由事实源；本地 `LocalRoute` 返回
  `related_routes`、secondary 的 skill/required reads 和 `next_stage`。
- `bridge` 返回并可持久化 `workflow`，列出当前 stage、所需产物、激活边界和业务
  验收边界；复刻语义会显式指向 R46，普通 `normal-dev` 返回 `host-native`。
- `follow-up` 必须读取同一 case root 的开放 `case.json`，缺少记录时 typed
  `blocked`；不会静默新建 route。
- 宿主、安装和 Builder 要求显式 selected host；不按 PATH 顺序猜 Codex/Pi/Claude，
  不选择模型。相关 focused tests 覆盖 mixed route、normal-dev guard、workflow
  round-trip、selected-host 和空/缺 case 边界。
- 本轮扩展了本地产品路由对 WASM/JSVMP、JWT/REST/WebSocket/SOAP、自定义二进制
  协议、Firefox/XPI、Electron/ASAR/Tauri/Qt、SPI/I2C/CAN 和显式重实现语义的
  可达性。`skills/config/routing.json` 仍作为固定上游基线保留，因而与产品本地
  `components/reverse-core/routing.json` 有意存在适配差异；默认执行只认后者，
  compatibility/coherence 门禁不应把上游基线误称为本地事实源。

这层合同仍然是按需提示和恢复点，不是固定逆向流水线，也不自动启动所有 provider。
route 命中只证明本地资料可达；tool-index、具体 provider、设备和商业工具仍按目标
记录 `unknown`、`blocked` 或 `unsupported`。本补充不修改旧仓库、旧安装或全局配置。
