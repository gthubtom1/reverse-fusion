# 真实组件部署与实现交接

RF-28 起，完整部署要求实际安装 REA、Spec Kit 和 Craft engine。路由、手写规格、
`session` 文件观察器和 `craft --source` 离线复制均不能替代这些组件。
普通开发仍使用宿主原有工具；分析不强制进入规格或编码阶段。
当前bridge返回当前项目cwd和组件argv；恢复同一案例/批次用只读
`workflow --project-root [当前项目] --case-root [原case] --receipt [原session]`。
中断、失败和独立任务继续规则见 [RECOVERY.md](RECOVERY.md)，不需要另找用户样本。

## 部署

Windows x64 的 `scripts/install.ps1` 默认安装全部核心组件；默认运行时不兼容时，
自动准备仓库本地、摘要固定的 Node v24.22.1；不覆盖全局 Node。已有 venv 可直接执行
`scripts/bootstrap-core.ps1 -NodePath [兼容Node绝对路径]`，然后
`[venv-python] -m reverse_fusion install --apply --client codex`。
`-PackageOnly` 仅供维护，不表示部署完成。`doctor.core_deployment` 单独报告组件安装；
总 `doctor.status` 仍是仓库合同结果。缺核心组件时 `install --apply` 拒绝写成功 receipt。

- REA：官方 6.9.0，固定完整性；精确 Node engine 见 manifest。执行真实 MCP doctor。
- Spec Kit：官方固定 commit `2ee2b1e8005905db05f5717300a469b3068b908f`，
  版本 1.4.1.dev0，固定依赖装入工具仓库 venv。无需全局 PATH 中有 specify。
- Craft：固定源码 `8374ad71544f2cc44698ea74ef990aa31600bac6` 的真实 Rust engine，
  通过仓库自有 `components/craft-native` 接入，附可重放 Windows 命令补丁。
  发布包及源码身份在该目录 manifest；原版 GUI/CLI 的 0.6.1 release 是另一个 commit，
  不能混用身份。本接入不启动原版 Study/模型会话，当前选定宿主提供推理和文件内容，
  实际 Workspace、写文件、编辑、运行检查由原生 Craft 工具执行。

目前发布构建只资格化 Windows x64。其他平台不能声称完整安装；保留现有平台支持代码，
通过源码适配和实机验证再增加对应分发。没有自动改变模型、账号、凭据或全局运行时。

从源码构建使用 Rust 1.97+ GNU Windows 工具链及 MinGW，显式传
`bootstrap-craft.ps1 -BuildFromSource -CargoPath [cargo] -RustcPath [rustc] -GccDirectory [gcc目录]`。
脚本校验固定 HEAD、补丁摘要和补丁后文件摘要，拒绝额外源码变化；使用 Cargo.lock。
源码构建 receipt 绑定本 checkout、二进制和全部适配源码摘要，不能复制到另一个 checkout
冒充已安装。维护者格式化后重建，通过测试，再运行 `scripts/package-craft.py` 打包。
打包需要 `RF_CARGO`、`RUSTC`、`RF_MINGW_LICENSES`，包含 267 个依赖包的声明及许可正文。
预编译包的二进制/归档/声明摘要均固定；不把可重复构建等同于逐字节一致构建。

## Spec 到真实 Craft

在成果项目执行工具仓库的`specify init`，选择当前宿主integration。
Codex示例为`specify init --here --non-interactive --integration codex
--integration-options=--skills --script ps`；Pi/Claude对应目录与参数见
[HOST-PROJECT-CONNECTION](HOST-PROJECT-CONNECTION.md)。已有项目先检查冲突，保留原规格和证据。
随后读取该项目真实生成的工作流（Codex为`.agents/skills/speckit-*`），执行constitution、specify、
必要的 clarify、plan、tasks、analyze。这些大多是 agent 工作流，不是同名 CLI 子命令。
记录真实脚本输出及 Evidence→需求→任务对应，关键未知回到分析；原生 prepare 还会运行固定官方 Spec prerequisites，并冻结实际 feature/spec/plan/tasks、
constitution 和生成的技能；这一机械门不能证明需求语义充分。实现后继续 implement
要求的检查、任务状态和 converge。仅运行 init 或写同名 Markdown 不算执行完整 Spec。

交接仍使用原 case-review、handoff checker 和语义审查；冻结 Spec 任务、原版身份、
研究、检查命令及租约。所有路径都属于当前成果项目，技能正文属于共享工具 checkout。

同一完整feature中仅部分功能的依赖已满足时，可在语义审查明确独立性后，为prepare
重复传`--requirement FR-001`等选择本批需求。选中task的唯一任务行必须显式写出
对应FR编号，不能引用未选需求；每个选中FR都要映射选中task。完整spec与handoff
所有引用仍检查和冻结，其他需求保存在`handoff.deferred_requirements`，不会删除。
关键unknown仍阻断受影响的选中需求；默认不选子集时保持全量阻断。依赖独立性
本身仍由真实调查和语义审查判断，不能靠重新标号隐藏远程/授权依赖或取消原目标。

```text
[python] -m reverse_fusion native-craft prepare --project-root "[成果项目]" --lease work/case/native-lease.json --workspace work/case/craft --receipt work/case/session.json --case-root work/case --handoff-manifest work/case/notes/handoff-manifest.json --review-file work/case/notes/semantic-review.md --tasks T001 --task-file specs/feature/tasks.md --research-file work/case/research.json --allowed-output app/main.ext --check-command "[已审查的构建或测试命令]" --command-timeout 60
[python] -m reverse_fusion native-craft build --project-root "[成果项目]" --lease work/case/native-lease.json --params-file work/case/write-request.json
[python] -m reverse_fusion native-craft check --project-root "[成果项目]" --lease work/case/native-lease.json --params-file work/case/check-request.json
```

write request 为 `{"path":"app/main.ext","content":"实际候选源码"}`；
check request 为 `{"command":"与冻结清单完全相同的命令","timeout_secs":60}`，运行 cwd
是 Craft workspace 的 `app/`。不把原版源码复制冒充独立实现。必要时 `refine` request 为
`{"path":"app/main.ext","old_text":"原候选片段","new_text":"修改后片段"}`。
修改会撤销过去检查的资格；重跑全部冻结检查后才能 `return_summary`、`cleanup`。
官方 implement 的 hooks、checklists、任务依赖、失败检查和最终检查仍需执行。一个租约
期间 Spec 输入保持冻结，逐任务结果先写该批独立日志；session finish 后才更新 tasks
勾选和 converge。后续改规格或研究需要新批次，不能边改冻结任务边继续旧租约。
失败退出/超时不通过，操作系统锁拒绝同一工作区并发写入。构建命令有真实 shell 效果，
清单是审查边界，不是通用 OS 沙箱。不要将目标文本直接拼成命令。

RF-31的adapter0.1.1增加 `native-craft abort`，请求文件为
`{"reason":"调查或规格变化，需要终止本批并保留现场"}`。它使用相同租约和OS写锁，
保留文件和原冻结摘要，将session标为aborted，禁止后续写入/完成。研究缺失或改变
仍能正式中止，租约本身必须保持原身份。prepare拒绝已有非空工作区，避免失败重试
创建另一份指向旧候选的记录。完整处理步骤见RECOVERY.md。
各检查记录候选摘要；cleanup要求最后通过的每项检查对应当前候选，session finish再
绑定cleanup后的候选与craft.json摘要，防止检查后修改或仅完成文件观察就冒称原生交接。

接着对同一 receipt 执行 `session check/refine/finish` 观察额外文件边界。日志保存原生调用、
结果、二进制摘要及请求摘要；`candidate` 仍不代表等价。独立比较原版/候选、故意错误
对照、实际 REA comparison/proof/ledger 以及 Spec converge 分别记录实际范围和未决义务。
某个纯函数切片通过不表示整个软件、在线授权、设备或游戏运行通过。

REA 原生 JSON/bundle 按 UTF-8 读取（Python 显式 `encoding="utf-8-sig"`，Node 显式
UTF-8），不要用 Windows 默认代码页重存证据。中文可能变成另一段合法文本，随后原生
Evidence ID 完整性校验会正确拒绝它；不能刷新 ID 把误读内容伪装成原事实。
已有两侧真实 application bundle 的 JS 导出静态比较可运行
`[兼容Node] scripts/compare-js-exports.mjs [左bundle] [右bundle] [左模块] [右模块] [新输出目录] K q R`。
该工具保留 UTF-8、原生结果和输入摘要；`coverage=partial` 继续保持 partial，不由
exit 0 提升为运行等价。派生的原版导出 wrapper 要单独保留其源跨度与适配身份。

需要把 scope 等活动文档作为带摘要的 Evidence 引用时，保留不可变版本快照，活动范围
另存当前文档。后续范围追加不刷新旧 Evidence 的摘要或重写原生对象；历史指针迁移
必须记录旧路径、相同字节摘要和原因，当前范围另立引用。用户已允许的同范围技术步骤
无需每轮制造一次新的授权决定或重写 scope。
