# 交给下一位智能体的维护提示词

把下面内容直接交给下一位 Codex、Pi、Claude 或兼容 coding agent：

```text
你正在维护 reverse-fusion。先完整读取 README.md、AGENTS.md、
docs/PRODUCT-GOAL.md、docs/CURRENT-STATE.md、docs/DECISIONS.md、
docs/PROVIDER-STATUS.md、docs/TARGET-CAPABILITY-MATRIX.md、
docs/FINAL-RELEASE-ACCEPTANCE.md、SOURCE-MANIFEST.json、最新 checkpoint 和
Git 状态。

当前标签是 reconstruction-product-v1-final（RF-22 已闭合）。这不是重新设计框架
或再次宣布 framework-v1-baseline 的任务。任何新工作都必须先建立新的
target case 和完成门，并保留旧 case 的 Evidence、ledger 与 converge 记录。

硬约束：

- 不修改旧 reverse-skill、旧 installer、REA/Craft/Spec Kit 现有安装、Craft
  companion 的 `--all-tools` 参数、宿主凭据或全局配置。
- 不选择、下载或绑定 Codex/Pi/Claude 的模型。模型、账号和 provider 属于
  当前宿主；仓库只记录宿主返回的运行观察。
- 不把工具可见、MCP connected、exit 0、Craft Ready 或模型自述写成业务验收。
- 每个新目标都必须有唯一 Reverse route、原版 REA Evidence、冻结 Spec
  tasks、host-owned Builder candidate、build/run、comparison、pass/fail/unknown、
  cleanup、canonical reconstruction proof 和 obligation ledger。
- provider、登录、设备、PTY 或加壳/混淆能力缺失时写 blocked、unsupported 或
  unknown，并保留下一步 probe。

当前已闭合的代表性链（它们验证统一产品合同，不要求穷举未来目标）：

- WASM：WABT interpreter 与 official REA ledger ready。
- Web/JavaScript：Node finite traces pass；静态 partial 和 package/parser
  unknown 保留在 acceptance；reviewed export ledger ready。
- PE/.NET：.NET 8 build、REA managed comparison、四组 runtime traces 和 ledger
  ready。
- APK/DEX：JADX headless MCP 0.7.1、javac/D8/AAPT、REA package/class static
  comparison 和 static ledger ready；无 adb/emulator 时 Android runtime 为
  unknown。

维护流程：

1. 先运行 `python -m reverse_fusion contracts`、`plan`、`doctor`、`handoff`
   并检查 provider 状态。
2. 新目标先通过 `bridge --source local` 建 case，再在 `specs/` 写 spec、plan、
   tasks、converge；不要复制旧 ledger 当作新目标证据。
3. Builder 使用宿主当前模型，调用中不得加入 `--model`；候选输出必须限制在
   case workspace 和 allowed outputs。
4. 用对应 runner 生成 REA Evidence、proof 和 ledger；把静态未知、设备缺失、
   PTY 缺失写入 acceptance。
5. 完成后更新 CURRENT-STATE、PROVIDER-STATUS、TARGET-CAPABILITY-MATRIX、
   FINAL-RELEASE-ACCEPTANCE、checkpoint、manifest 和 README，然后运行 tests、
   contracts、fresh-clone lifecycle 和 `git diff --check`。
6. 上游更新只做只读比较；只有新的 capability gap 有直接证据时，才在本仓库
   增加受控增强或 fork，并记录 rollback。

交付必须列出：新目标的原版/候选/比较/proof/ledger ID，宿主 transport 和模型
归属，pass/fail/unknown/blocked/unsupported，cleanup 与全局配置摘要，commit、
GitHub URL 和回滚点。没有直接 Evidence 的结论保持 unknown。
```
