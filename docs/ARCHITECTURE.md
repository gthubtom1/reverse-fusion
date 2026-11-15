# Reverse Fusion 聚合架构

Reverse Fusion 是一个仓库级编排器，包含一份固定来源的 Reverse 能力副本、REA/Spec/Builder 的边界合同和宿主适配入口。它不是把所有上游程序拼成一个常驻进程，也不会把所有 skill 一次性塞进模型上下文。

## 组件如何衔接

```text
当前宿主（Codex / Pi / Claude）
        │ 读取 AGENTS.md、RULES.md 和本仓库入口
        ▼
Reverse Fusion local router（唯一默认路由事实源）
        │ 选择 primary，列出 related_routes 和 required_reads
        │ 困难目标追加 runtime hard-target reads
        ▼
repository-local case.json + workflow contract
        │ analysis：保存原版 Evidence、观察、未知项和结论
        │ reconstruction：进入 R46，冻结 Spec tasks
        │ follow-up：从既有 case.json 恢复，不静默新建 case
        ▼
REA 原版 Evidence / comparison / ledger
        │
        ▼
官方 Spec Kit 生成工作流 → 冻结任务与研究
        │
        ▼
当前宿主推理 → 真实 Craft engine（唯一候选写入者）
        │ native prepare → build/check/refine → summary/cleanup
        │ session 仅附加文件边界观察
        ▼
候选 build/run、独立 proof、差分验收、obligation ledger、cleanup
```

路由只负责识别领域和交接资料。它不因为命中一个关键词就启动 REA、下载工具、调用另一个 CLI 或宣称目标等价。`bridge` 返回的 `workflow` 是可恢复的阶段合同：它说明当前阶段、下一阶段、相关领域、需要的产物和业务验收边界；模型仍然根据证据决定工具和顺序。

## 三种实际使用方式

普通开发使用默认 `normal-dev`。例如“开发一个普通网站”返回 `host-native`，不创建 Reverse case，也不启动 REA、Spec、Builder 或 ledger。只有用户明确提出逆向、分析或复刻，或者显式选择 `--mode analysis` / `--mode reconstruction`，才会激活 Reverse。

分析使用 `--mode analysis`。primary domain skill 是当前入口，混合请求的 secondary route 会出现在 `related_routes`，其 skill 和 required reads 同时写入 case 的 `carry_forward_refs`。这样开发中的“研究另一个 APK、网站、桌面客户端或协议”可以作为隔离 subcase 接入，审查后的事实再回到主项目。

复刻使用 `--mode reconstruction`。目标专业 route 仍然负责先分析；如果请求包含复刻语义，route 返回 `next_stage.id=R46`，并提供 `skills/reconstruction/SKILL.md`。进入 R46 后才冻结 Spec tasks、启动真实 Craft engine Builder、构建/运行候选并执行比较。普通开发不会因为存在 R46 而自动进入复刻。

`--mode follow-up` 必须找到同一 case root 下的开放 `case.json`，然后沿用已记录的 primary、workflow 和 refs。缺少 case 时返回 typed `blocked`，不会按新 hint 伪造一次“恢复”。

## 路由所有权与外部来源

`components/reverse-core/routing.json` 和 `router.py` 是本项目默认路由事实源。`skills/config/routing.json` 及旧安装的 native router 作为固定来源/只读兼容输入，只有显式 `--source external` 或 `--source auto` 的本地路由不可用时才参与；外部结果带 `source=external`，不能静默覆盖本地 owner。旧 `reverse-skill` 不需要存在，fresh clone 仍有自己的 45 个 route、descriptor、skill 和 runtime manifest。

## 能力边界

Reverse Skills 的 603 个增强来源文件已保全，包含加壳/脱壳、反调试/反 VM/反 Hook、OLLVM、动态 DEX/JNI/反 Frida、.NET 混淆和 JS VM/WASM 方法。保全证明内容和入口存在；具体目标仍由 Evidence、provider 和设备状态决定。缺少工具索引、登录、额度、设备或商业工具时，保留 `unknown`、`blocked` 或 `unsupported`。

REA 保持官方版本；Spec 是实际安装的官方 CLI 及生成的项目工作流；Craft 是固定原生 engine
加仓库自有接缝和可重放补丁。宿主推理通过 Craft 原生工具写候选和运行检查。
完整部署要求全部核心组件安装，真实参数和当前平台范围见 [NATIVE-COMPONENTS.md](NATIVE-COMPONENTS.md)。项目不选择模型、不下载模型、不复制凭据，也不修改旧仓库或宿主运行配置；Codex 安装只写一个指向当前 checkout 的受控用户级路由适配层。

安装和卸载只处理当前 checkout 的 `.venv`、repository-local receipt 及按需生成的 vendor/case 内容。换电脑时只需给当前宿主仓库链接；宿主读取本文件和 `docs/AGENT-BOOTSTRAP.md` 后，会按本机 OS、Python、selected host 和 provider 状态完成适配。
