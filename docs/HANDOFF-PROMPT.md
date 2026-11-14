# 交给下一位智能体的最终目标提示词

下面的内容可以直接复制给下一位 Codex、Pi、Claude 或兼容的 coding agent。

```text
你正在继续维护 reverse-fusion。先完整读取：

1. README.md
2. AGENTS.md
3. docs/PRODUCT-GOAL.md
4. docs/PROJECT-CONTEXT.md
5. docs/CURRENT-STATE.md
6. docs/DECISIONS.md
7. docs/FINAL-COMPLETION-SPEC.md
8. docs/FINAL-RELEASE-ACCEPTANCE.md
9. docs/PROVIDER-STATUS.md
10. docs/TARGET-CAPABILITY-MATRIX.md
11. components/official/manifest.json
12. 当前最新 checkpoint、SOURCE-MANIFEST.json 和 Git 状态

你的最终目标不是再做一个框架演示，而是把 reverse-fusion 完成成一套可迁移的真实分析到复刻产品：用户只给仓库地址，当前宿主自行提供它的账号和模型，系统负责把 Reverse、REA、Spec Kit、Builder、候选构建和差分验收连成一条可恢复链。

硬约束：

- 不修改旧 reverse-skill、旧 installer、旧 REA/Craft/Spec Kit 安装和任何全局配置。
- 不选择、不下载、不绑定 Codex/Pi/Claude 的模型。模型、账号和 provider 属于当前宿主；仓库只读取运行结果和能力状态。
- 不把工具可见、MCP connected、exit 0、Craft Ready 或模型自述写成业务验收。
- 不把 WASM fixture、local-bounded-worker 或一个 console 测试扩展成任意目标等价。
- 不把 `framework-v1-baseline` 改名为最终产品。只有 docs/PRODUCT-GOAL.md 的全部门闭合后才可以标记 `reconstruction-product-v1`。
- 每个真实目标必须有原版 Evidence、冻结任务、candidate、运行/比较结果、unknown 和 cleanup 记录。

模型和宿主规则：

- Codex 使用当前 Codex 账号和当前模型；不要给它强行传 --model。
- Pi 使用当前 Pi provider 和模型；不要在仓库里写 provider key。
- Claude 使用当前 Claude 登录状态；未登录时记录 blocked，继续完成不依赖它的工作。
- Builder 的 model_id 只能记录宿主返回的观测，不能作为产品安装依赖。

必须先完成的实施顺序：

阶段 A：恢复真实目标合同

- 把 docs/PRODUCT-GOAL.md 当成最高优先级完成合同。
- 重新检查当前所有“final”字样和文档漂移，把状态统一为 framework-v1-baseline，直到真实 Builder 和代表性目标链完成。
- 给每个阶段增加单一下一步动作和完成门，禁止在一个 fixture 上循环测试而不前进。

阶段 B：让 Reverse 真正可迁移

- 让 fresh clone 在没有旧 receipt 时也能调用仓库自己的 Reverse 路由。
- 可以固定版本引入或仓库本地安装 enhanced reverse source，但旧安装只能只读来源。
- bridge 必须区分 local route pass、external route pass、unavailable 和 blocked。

阶段 C：接入真实 Builder

- 继续使用官方 Craft 身份或仓库自己的 bounded adapter，但必须让当前宿主的 agent 真实产生/修改候选文件。
- 完成 prepare/build/check/refine/return_summary/cleanup 六项能力。
- local-bounded-worker 只保留为离线合同测试，不作为最终复刻能力。
- 至少完成一个真实目标的“分析 → Spec tasks → Builder 输出 → 构建 → 运行 → 差分 → 修正”闭环。

阶段 D：扩展代表性目标

- 保留 WASM 已有闭环。
- 增加 Web/JavaScript、PE/.NET 或 Native、APK/DEX 中至少三个真实代表性目标，优先使用本地小目标和可复现 fixture。
- 不要求穷举所有未来软件，但 capability matrix 中标为 supported 的类别必须有真实 Evidence 和 candidate 验收；没有 provider 的类别写 unsupported/blocked。

阶段 E：最终验收

- 正确候选 pass。
- 行为错误候选 fail。
- Evidence 缺失 unknown。
- provider/登录/cleanup 缺失 blocked 或 unsupported。
- fresh clone、install、plan、doctor、update、uninstall 通过。
- 旧仓库和全局配置前后摘要一致。
- tests、contracts、docs、checkpoint、manifest、GitHub remote 一致。

工作方式：

- 先读真实源码和当前状态，再修改最少的文件。
- 每一个声明都要对应直接 Evidence；无法验证就保留 unknown 或 blocked。
- 每完成一个阶段，更新 CURRENT-STATE、checkpoint、provider status 和回滚记录。
- 不要因为 token、上下文压缩或局部测试通过就提前宣布完成。
- 只有 PRODUCT-GOAL.md 的全部完成门闭合，最终回复才可以使用“最终产品完成”。

交付回复必须明确列出：

1. 已完成的真实目标类别。
2. 每类的原版 Evidence、candidate 和差分结果。
3. 使用的宿主 transport，以及模型由宿主提供的事实。
4. 仍然 blocked、unsupported 或 unknown 的能力。
5. fresh clone 和全局配置不变的直接证据。
6. 最终 Git commit、GitHub URL 和回滚点。
```
