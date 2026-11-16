# Reverse Fusion 产品合同

本文件定义产品职责与完成含义；用户的新指示优先。当前版本读取`VERSION`，
当前阶段/结果读取[CURRENT-STATE](CURRENT-STATE.md)和最新checkpoint。
当前22项功能与适配结果见[USER-REQUIREMENTS-REVIEW](USER-REQUIREMENTS-REVIEW.md)，
工程发布门见[RELEASE-1.4](RELEASE-1.4.md)及`release/manifest.json`。
历史阶段的“final”“未完成”和旧资格门均不自动覆盖当前合同。

## 产品要解决的问题

用户用白话提供目标，当前智能体能使用同一套共享核心完成适用的领域调查、
证据整理、任务规划、受限实现、原版/候选比较、差异修正和可恢复交付。
它支持普通开发中按需研究参考目标，也支持独立分析和复刻项目。
普通开发保持host-native，纯分析不强制规格或候选；仅复刻进入完整实现验收链。

```text
当前宿主入口/技能
  -> Reverse唯一路由与成果项目case，保留原始目标和当前阶段
  -> 领域方法与REA/Craft实际MCP或CLI工具、原生Evidence，调查行为、错误路径和依赖
  -> 就绪审查与官方Spec项目工作流，冻结研究/任务
  -> 当前宿主推理 -> 真实Craft engine写入/编辑候选和执行检查
  -> 独立构建/运行/原版比较 -> 修候选或回分析/规格
  -> 原目标范围验收、实际proof/ledger、cleanup与恢复记录
```

这是职责与交接，不是固定逆向工具顺序。方法随真实证据调整；困难目标按需加载
加壳/混淆/反调试/动态加载等资料。声明unknown、缺工具或关键依赖时只阻断受影响
任务，其他独立工作继续。需要用户帮助时问具体材料、操作或产品决定，不让用户选
专业路由/工具，也不把整个目标偷换成演示品或未获同意的切片。

## 共用核心与宿主适配

共用核心由代表性完整运行验证；现有Codex/Pi实际完整使用记录保存在`evidence/rf33/`。
每个宿主的入口文件、技能发现、工具调用/权限、项目路径、官方Spec布局及接入生命周期
必须核对并做针对性检查，不要求每新增宿主就登录并完整重跑样本。
Codex/Pi/Claude项目适配已完成；Claude完整模型运行未实测，是可选观察。
详细完成条件和当前宿主目录映射见[HOST-PROJECT-CONNECTION](HOST-PROJECT-CONNECTION.md)。
未知宿主不因名字相似就自动被判支持；新工具协议、权限/进程语义和新操作系统分发
按实际差异验证，不重做已验证的核心设计。

当前完整预编译分发为Windows x64。新电脑只需按[AGENT-BOOTSTRAP](AGENT-BOOTSTRAP.md)
重建本机环境、必装核心和所选入口，执行工程检查；不能只装包或跳过缺核心后报成功。
不要求新电脑提供目标样本、重做产品开发，或登录另一宿主才能完成安装。

## 组件所有权和模型归属

- Reverse core是唯一route/case owner。fresh clone自带路由descriptor、领域正文与
  required support；缺失时unavailable，不能只依赖旧reverse-skill receipt。
- REA负责实际分析、Evidence、comparison、coverage与ledger；本仓库有明确归属的
  有限integration verifier，不冒称REA原生进程验证权威，不伪造闭合或刷新坏证据身份。
- Spec必须是实际安装的官方CLI及生成的项目工作流；规格/plan/tasks引用原证据，
  实现前审查并冻结，实现后做适用检查与converge，同名手写文档不替代真实阶段。
- Craft是固定真实engine加本仓库接缝/可重放补丁。当前宿主推理和提供内容，
  原生工具执行Workspace/候选写入/编辑/命令/检查/summary/cleanup。
  session仅附加观察，offline fixture copy不替代真实实现；不另启重复Study或模型。
- 接入与安装只管理本仓库资产和受控薄入口；旧安装、无关全局配置和凭据保持不动。
  Codex/Pi/Claude各使用自己的当前模型、账号和provider；项目不选择、下载、绑定或切换模型。

## 完成与目标级验收

产品完成表示上面的部署、所有权、工作流、恢复与宿主接入有实际实现、合同和适用
检查，文档/来源清单/版本/发布一致；不表示所有未来软件、保护器、设备或服务已经
预先执行成功。当前交付以22项明确功能/适配定义为准，不被旧阶段表中的延期决定重开。

每个具体目标仍保留自己的pass/fail/unknown/blocked/unsupported。工具可见、
MCP catalog、文件存在、exit0、Craft Ready或模型自述不是业务效果验收。
原件和候选身份、输入/环境、错误候选检测、真实差异及清理分别留证；有限比较
不能改名成完整原生证明，未测Android设备或未知保护效果也不能预先判通过。

维护仅围绕用户新需求、已复现缺陷或有明确收益的上游增量，按
[UPSTREAM-MAINTENANCE](UPSTREAM-MAINTENANCE.md)记录变更、验证与回滚。
旧合同演进完整保存在[历史快照](history/PRODUCT-GOAL.md)，仅按需追溯。
