# Reverse Fusion 最终产品合同

本文件是项目的最高层产品目标。它高于阶段性 checkpoint、fixture 通过记录和 provider 的当前状态。任何阶段都不能用“框架合同通过”替代本文件定义的产品完成。

## 产品要解决的问题

Reverse Fusion 最终要提供一套可迁移的智能体工作流：用户把仓库地址交给 Codex、Pi、Claude 或兼容宿主，宿主按本机能力完成安装和适配；用户提供一个真实目标后，系统能够把逆向分析、证据整理、复刻任务、候选生成、运行和差分验收连成一条可恢复链路。

最终链路必须是：

```text
宿主适配
  -> Reverse 唯一路由和 case
  -> REA 原版 Evidence
  -> Spec Kit 项目任务（复刻模式）
  -> 当前对话中的宿主 agent 执行 bounded Builder
  -> 候选构建与运行
  -> 原版/候选差分
  -> 修正任务
  -> obligation ledger 闭合
```

WASM fixture 只能证明这条链的一个最小样本，不能代表任意目标已经完成。

## 最终完成的含义

`reconstruction-product-v1-final` 的完成标准是产品逻辑和工作流已经闭合：
路由、case、REA Evidence、Spec tasks、宿主 Builder、候选构建/运行、差分、
修正任务、proof、obligation ledger、cleanup、provider 边界和交接文档都由
同一套可迁移合同连接起来。

代表性目标用于验证这些合同和组件之间的连接关系，不要求预先执行每一种未来
软件、架构、加壳、混淆或反调试变体。未来目标通过相同的路由和证据合同进入新
case；目标级结果仍按 `pass`、`fail`、`unknown`、`blocked` 或 `unsupported`
记录。产品完成表示面对新目标有正确的处理逻辑和恢复路径，不表示所有未来目标
已经提前得到 pass。

完成后的正常工作是新 provider、工具版本、目标专用 probe 和分析规则的小版本
演进；基本架构、职责划分、证据链和部署合同不再重做。

## 模型归属

Reverse Fusion 不选择、不绑定、不下载模型，也不把某个模型名称写成产品依赖。

- Codex 使用 Codex 当前账号、配置和模型。
- Pi 使用 Pi 当前 provider、账号和模型。
- Claude 使用 Claude 当前登录状态、provider 和模型。
- Reverse Fusion 只负责宿主适配、任务上下文、Evidence 引用和结果合同。
- `model_id` 只能作为宿主返回的运行观测，不得成为安装或路由选择条件。

如果宿主没有登录或没有可用 provider，状态必须是 `blocked` 或 `unavailable`，不能被写成 Builder 成功。

## 组件职责

- **Reverse core**：唯一入口、路由、case、模式和复刻任务生命周期。它既支持独立 reconstruction case，也支持在 normal-dev 主项目中按需创建隔离的 analysis/reconstruction subcase；`bridge --record` 持久化仓库内的 `case.json` 恢复点；新电脑没有旧 receipt 时也必须有仓库自己的可用路由和本地领域技能；旧 reverse-skill 可以作为固定版本的来源或可选增强，但不能是唯一运行前提。
- **REA**：原版分析、静态/动态 Evidence、comparison、unknown 和 obligation ledger。REA 保持官方版本，除非有证据支持的能力缺口。
- **Spec Kit**：复刻模式的项目级意图、plan、tasks 和 converge 记录。normal-dev 默认按需启用；任何嵌套 subcase 一旦进入复刻阶段，就必须保留冻结任务和来源引用。
- **Craft/Builder**：按冻结任务生成候选项目、执行构建、检查、修正和清理。默认 writer 是当前对话中的宿主 agent，`session prepare/check/refine/finish` 冻结输入并观察候选文件边界；无需另启 CLI、账号或模型。子 CLI 是按需独立资格化的可选 transport。Craft 当前只分发 bounded interface，历史 patch 名称不是已发布 patch；离线复制 fallback 只用于合同测试，不代表真实复刻能力。
- **Acceptance**：独立读取原版和候选 Evidence，输出 pass、fail、unknown、blocked 或 unsupported。模型自述、工具可见和 exit 0 都不属于业务验收。

## 最终完成门

只有以下条件全部成立，才能把项目标记为 `reconstruction-product-v1-final`：

1. fresh clone 在 Windows、Linux 或 macOS 的支持宿主上完成仓库本地安装、plan、doctor、update、uninstall；没有旧 reverse-workflow receipt 也能执行仓库自己的路由入口。
2. Codex、Pi、Claude 至少完成宿主加载协议验证；每个宿主的登录缺失单独记录，不能把宿主阻塞伪造成通过。
3. Reverse、REA、Spec Kit 和 Builder 只有一个明确 owner；每个本地 route 都同时拥有 descriptor 和领域技能正文，所有 Evidence、任务、candidate 和差分结果都有持久引用。
4. 至少四类代表性目标完成端到端链：WASM、Web/JavaScript、PE/.NET 或 Native、APK/DEX。每类都必须有原版分析、冻结任务、真实候选输出、构建/运行观察和差分结果。代表性链验证产品合同和变体处理逻辑；未来目标不需要穷举，目标族也不能只停留在 planned。
5. 至少一条真实 Builder 链使用宿主自己的 agent/model 生成或修改候选文件，并完成 prepare、build、check、refine、return_summary、cleanup 六项能力；复制 fixture 的 fallback 只能作为测试路径。
6. 至少一个正确候选、一个行为错误候选和一个 Evidence 缺失候选分别得到 pass、fail、unknown；至少一个构建或 provider 缺失场景得到 blocked/unsupported。
7. 加壳、混淆、动态行为或 provider 缺失时，系统保留 unknown 和下一步 probe，不把静态相似或模型自述升级成等价结论。
8. 所有 host/global 配置写入都有明确 scope；默认安装、探针、卸载和失败清理不改变旧仓库、宿主凭据或全局配置，并通过已知配置文件哈希前后对照记录观察结果。
9. `evidence/rf22/manifest.json` 对代表性 Evidence/proof/ledger 文件做 hash 校验；官方 REA 还要通过身份解析、bundle links 闭合与实际篡改反例。不得改写 hash 覆盖的绝对路径却保留旧 ID。`docs/CURRENT-STATE.md`、`docs/FINAL-RELEASE-ACCEPTANCE.md`、checkpoint、README、manifest、测试和 GitHub remote 对同一完成状态；历史记录不覆盖当前结论。
10. 只有完成以上门后才允许写 `final product complete`。此前只能写 `framework-v1-baseline`、`reconstruction-v1-in-progress` 或明确的 `blocked/unsupported`。

## 当前版本的正确标签

RF-22 的 `reconstruction-product-v1-final` 是历史标签，RF-23/RF-24 随后增加
部署和 Reverse 保全。RF-25 全量审计发现旧 Builder/归档/runner/文档结论仍需
修正，故当前状态以 `docs/CURRENT-STATE.md` 与
`checkpoints/RF-25-20261115-001.md` 为准，不根据历史 final 推断本轮已经通过。
产品版本为 `1.0.0`；本轮所有有限完成门闭合后才恢复当前发布完成声明。

本轮声明范围：WASM 有限执行与三态；Web answer 有限重放 ledger ready，而完整
graph ledger 为 unknown、4 个 required open（2 packaging、2 application/parser）；
PE/.NET 有限方法运行 ledger ready；APK 构建与 manifest/member 投影 ledger ready。
APK 的设备运行、方法体等价和有效 Activity 启动均不由静态证明建立。未知项保留，
不靠移除 comparison links 或缩写报告把它们升级成完整目标等价。未来目标沿用
同一合同建立 case、probe 或 provider，无需预先穷举每种变体。
