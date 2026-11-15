# Reverse 增强能力迁移审计

日期：2026-11-15。阶段：RF-24。范围：旧增强版的内容、辅助实现与新项目的
接入关系；此次不运行受保护目标。

## 来源与逐文件对比

来源为 `https://github.com/gthubtom1/reverse-skill`，固定提交
`3fdbb927b474dc23ef2e19403d5464dcb9702cec`。直接读取 Git blob，与新工作树
逐文件比较；Git 文件列表使用 NUL 分隔与 UTF-8 解码，避免漏掉中文文件名。
文本仅统一 CRLF/LF；JAR 用原始字节 SHA-256。

修复前，来源 `skills/` 下 **453 个已跟踪文件全部存在且内容一致**，包含
47 份 `SKILL.md`（45 个路由入口、总入口和一个子技能）。因此“只搬了技能正文、
丢了加壳/反调试脚本”的说法不成立。参考资料、领域脚本、通用工具发现、进程
租约、case 与 Evidence 辅助脚本也在这 453 个文件内。

实际缺口及修复如下：

| 缺口 | 实际影响 | 本轮处理 |
|---|---|---|
| 根 RULES.md 缺失 | 领域正文引用的行为入口无法解析 | 新增适配当前宿主与新产品职责的规则 |
| 路由只给 descriptor/skill | 资料存在但未明确交接，恢复 case 后只见路由 | 返回 required_reads、missing_support、hard_target，并持久化引用 |
| 两套有效路由数据不同 | 原生 PS/Bash 与产品 CLI 的 Web 分诊可能不同 | 原生入口优先读取产品 routing.json；保留原 baseline |
| R41 的 CTF sidecar 缺失 | PRIMARY 存在，下一层打不开 | 补入来源 136 个 sidecar 文件，保留独立声明和许可 |
| 工具发现引用 Burp 资源缺失 | 能力描述存在，bridge/build source 缺失 | 补入来源 14 个文件；不构建、启动或注册 |
| Kali/平台文档及旧审计断链 | 指向未提供的旧安装树 | 使用已复制的通用 shell 入口、当前指南与固定历史审计链接 |
| 只检查 SKILL.md 存在 | 配套资料/脚本丢失仍可能被判完整 | 在既有 contracts/doctor 加入内容清单校验 |
| 工具索引未忽略 | 本机路径可能误提交 | 忽略 tool-index、egg-info 和 Burp 构建目录 |

## 重点能力

| 能力 | 保留的实际资源 | 接入与结论 |
|---|---|---|
| PE 壳、OEP、dump/IAT、自校验 | reverse-engineering/references 下 high-difficulty-pe-playbook、hard-target-decision-framework、re-agent-workflow；tools-advanced | 内容保全；R0/IDA/r2/Ghidra 等困难提示带入对应资料 |
| 反调试、反虚拟机、反 Hook、工具触发早退 | reverse-engineering/anti-analysis.md、tools-dynamic.md、references/provider-neutral-failure-matrix.md | 内容保全；保留无观察/最小观察/当前观察对照及失败路径 |
| OLLVM/CFF/VM 局部语义 | reverse-engineering/references/ollvm-deobfuscation.md、dsl-vm-reverse/ | 内容保全；按证据选方法，局部恢复不等于全量去虚拟化 |
| Android 加固、动态 DEX、JNI/native、反 Frida | apk-reverse/references 的高难/advanced/cookbook；scripts/frida-run.ps1 和 .sh | 正文与脚本保全；R1 困难提示可达；设备/provider 独立检查 |
| .NET 混淆、anti-tamper | dotnet-reverse/SKILL.md、references/obfuscators.md | 内容保全；R5 可达，工具适用性按目标判断 |
| JS 混淆、反 debugger、JS VM/WASM | js-reverse/references 的 AST、高难 playbook；通用 nonpe-format-cookbook | 内容保全；R3 带入对应资料 |
| 卡住后的重新规划、覆盖与置信度 | ops/analysis-decision-framework、analysis-blindspot-cookbook、authorization-coverage | 内容保全；ADF 是决策叠加层，不增加 PRIMARY |
| 动态工具与生命周期 | ida-reverse/scripts/、APK Frida helper、scripts/process-lease.ps1 与 lib/ | 原实现保全；旧全局安装/常驻服务副作用不进入默认安装 |

表中相对路径均位于 `skills/`。旧增强能力由方法、证据与失败转场规则、工具
wrapper 共同构成，并没有内置已验证能自动处理任意保护器的脱壳引擎。本轮保全
这些能力和接入，REA 不作为唯一可用分析工具。

## 清单与有意适配

`components/reverse-core/preservation.json` 固定 **603 个来源文件**：skills
453、CTF sidecar 136、Burp 14。RF-24 时 592 个保持来源内容，7 个集成适配和
4 个纯行尾空白清理。RF-25 又适配 reconstruction 的 backend descriptor 和版本测试，
并明确当前会话 Builder 与有限 proof 适配边界；现在 590 个保持来源内容，9 个集成
适配与 4 个空白适配共 13 个均记录上游摘要、本地摘要及原因：

- skills/SKILL.md、skills/reconstruction/SKILL.md：通用 shell 入口与本地部署边界。
- skills/ops/skill-supply-chain.md：当前能力审计与固定历史审计链接。
- skills/scripts/master-route.ps1 和 .sh：同一有效路由来源。
- skills/scripts/bootstrap-reverse.sh、refresh-tool-index.sh：当前平台文档。
- skills/reconstruction/references/execution-backend-contract.json：审查后更新必需文件摘要。
- skills/reconstruction/tests/test_backend_routing.py：产品版本和领域合同版本分离。

另有 4 个来源文件仅清除已有行尾空白（CTF 资料一处、Burp 的 JS/Java 三处），
以通过默认 git diff --check；执行逻辑未变。加壳、反调试和混淆技术资料及对应
工具 helper 的正文没有删减或简化。以后增强
来源文件时，同步更新清单与适配原因；来源版本不是永远冻结。

## 未照搬的旧根目录内容

- 旧 AGENTS、README_AI、RULES 的宿主/安装引导：由本项目 AGENTS、RULES、
  DEPLOYMENT-GUIDE 替代，沿用当前宿主。
- 旧 plugins、Kali quick-setup 与全局接入：不是新项目依赖。Linux/macOS/Kali
  使用已复制的通用 shell 工具；历史全局安装动作服从当前写入范围。
- 根 scripts/refresh-tool-index.ps1 只做转发，底层 skills/scripts 入口及依赖
  完整保留。
- 旧发布 CI、宣传资源、旧 docs/examples：使用固定来源链接；新项目有自己的
  docs/specs/Evidence/验收。部分原仓维护检查仍针对旧根布局，不作为本产品的
  部署验收入口；没有通过删除旧断言伪造其通过。

## 本轮有限验证

- 22 个项目测试通过，包括全部 192 条原路由期望。
- 原兼容检查通过：44 条原路由、178 条原 benchmark、原相对优先级和 fallback。
- 16 条困难目标 eval 契约检查通过：PE 4、Android 4、JS 3、协议 3、provider
  失败 2。它们检查决策与证据字段，不是 16 个目标运行成功记录。
- 缺失 anti-analysis.md 时困难路由为 unavailable；内容改动未登记时 contracts
  为 fail，防止静默丢失增强。
- PowerShell 原生入口与产品入口对新增 Web 词一致；Git Bash Web/APK 分诊和
  三个改动 shell 脚本语法检查通过。此项不等于 Linux/macOS 实机验证。
- 实际 bridge --record 将反调试、PE、OLLVM、provider/cleanup 引用写入本地 case。
- Burp bridge 自带测试通过：loopback 假服务的断连恢复与工具调用；不等于
  真实 Burp 扩展已加载或目标业务通过。
- 本机从提交 `4ccddf5eac2f14b31992fb21f574d9b77bd0dcc5` 建立干净副本，
  重新创建本地虚拟环境、实际 install、contracts、doctor、handoff、22 个测试
  和 APK/反 Frida 资料的 bridge record 均通过。该副本 `reverse_root=null`、
  历史握手为 unrecorded，说明没有拿旧安装或旧宿主记录冒充此次迁移验证。
  临时副本随后清理；这仍是本机的干净副本检查，不是另一台电脑实测。

## 环境与目标边界

Windows process-lease 没有 Job Object containment。旧增强版已经明确
cleanup_completed=false，只能报告 observed cleanup；这是原有能力限制，
并非此次迁移丢失。REA PTY 的当前宿主限制继续保留。

本轮未新验证实际脱壳、反调试处理、完整去虚拟化或 Android 设备运行。
商业保护器、OLLVM 变体、反 IDA/Frida 和浏览器目标的成功结果仍在对应 case
记录，不能由内容摘要或流程测试推导。

旧增强版 checkout、旧 installer、现有安装和全局宿主配置均未写入。
