# 真实组件部署与实现交接

RF-28 起，完整部署要求实际安装 REA、Spec Kit 和 Craft engine。路由、手写规格、
`session` 文件观察器和 `craft --source` 离线复制均不能替代这些组件。
普通开发仍使用宿主原有工具；分析不强制进入规格或编码阶段。

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
  不能混用身份。本接入不启动原版 Study/模型会话，当前 Codex 提供推理和文件内容，
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

在成果项目执行工具仓库的 `specify init --here --non-interactive --integration codex
--integration-options=--skills --script ps`。已有项目先检查冲突，保留原规格和证据。
随后读取该项目真实生成的 `.agents/skills/speckit-*`，执行 constitution、specify、
必要的 clarify、plan、tasks、analyze。这些大多是 agent 工作流，不是同名 CLI 子命令。
记录真实脚本输出及 Evidence→需求→任务对应，关键未知回到分析；原生 prepare 还会运行固定官方 Spec prerequisites，并冻结实际 feature/spec/plan/tasks、
constitution 和生成的技能；这一机械门不能证明需求语义充分。实现后继续 implement
要求的检查、任务状态和 converge。仅运行 init 或写同名 Markdown 不算执行完整 Spec。

交接仍使用原 case-review、handoff checker 和语义审查；冻结 Spec 任务、原版身份、
研究、检查命令及租约。所有路径都属于当前成果项目，技能正文属于共享工具 checkout。

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
失败退出/超时不通过，操作系统锁拒绝同一工作区并发写入。构建命令有真实 shell 效果，
清单是审查边界，不是通用 OS 沙箱。不要将目标文本直接拼成命令。

接着对同一 receipt 执行 `session check/refine/finish` 观察额外文件边界。日志保存原生调用、
结果、二进制摘要及请求摘要；`candidate` 仍不代表等价。独立比较原版/候选、故意错误
对照、实际 REA comparison/proof/ledger 以及 Spec converge 分别记录实际范围和未决义务。
某个纯函数切片通过不表示整个软件、在线授权、设备或游戏运行通过。
