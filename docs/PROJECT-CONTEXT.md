# Project Context

Reverse Fusion 是独立 GitHub 项目，不是旧安装仓库的改版。它在当前 coding agent
中提供可恢复的普通开发、分析和复刻辅助能力：enhanced Reverse 领域技能、官方
REA、任务/Spec 层、bounded Builder interface、独立验收与仓库本地安装入口。
部署交接保存在 `docs/AGENT-BOOTSTRAP.md`，用户只需仓库链接，无需另存聊天文本。

Reverse 是唯一 route/case owner；REA 管理 Evidence/comparison/ledger；Spec
管理项目任务和来源引用；默认 Builder 是当前对话的宿主 agent；独立 verifier
负责业务验收。Craft 当前是 interface-only reference，不分发历史 patch，也不
要求启动原版工作台或另选模型。可选子 CLI transport 有独立的登录/额度状态。

normal-dev 默认不启动 REA 或 Builder。开发中途可建立隔离 analysis subcase，
保留 route、原版 Evidence、限制和结论；只有 reconstruction 才冻结 tasks，
生成候选并进行 build/run、comparison、proof、cleanup 和 ledger。只把审查后的
Evidence 支持结论或候选带回主项目，避免子案例污染普通开发目录。

模型可根据目标自适应选择静态/动态、脱壳、dump、hook、模拟、设备及 provider。
本仓库提供上下文、边界与证据恢复，不把逆向固定为单一路径。加壳、混淆、反调试
能力的保全不等于所有变体已执行；未知项保留 unknown 和下一步 probe。

项目不选择或下载模型，不复制凭据，不写旧仓库/旧安装或宿主全局配置。安装只
作用于当前 checkout；其他工作区使用时显式读取本仓库入口。上游仅在实际有益时
选择性吸收，不自动跟随每次发布。当前状态以 CURRENT-STATE 和最新 checkpoint
为准，历史 final 标签不能覆盖后来发现的问题。
