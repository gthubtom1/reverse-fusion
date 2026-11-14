# Project Context

Reverse Fusion 是一个独立 GitHub 项目。它把 enhanced reverse core、官方 REA、项目级 Spec Kit、Craft bounded adapter 和多宿主 installer 组合成一条可恢复的分析到复刻链。

核心原则：Reverse 是 route/case owner；REA 是原版 Evidence owner；Spec Kit 是可选 project intent owner；Craft 是单一 Builder；acceptance 由原 runner 和独立 verifier 完成。

normal-dev、analysis、reconstruction、follow-up 是四种模式。normal-dev
默认不启动 REA 或 Builder，但允许在同一个主项目里按需创建嵌套的
analysis/reconstruction subcase：当前网站、桌面软件、APK 或其他项目可以在
开发中途调用 Reverse/REA，得到的 Evidence、设计结论或接口观察再回到主项目。
复杂分析允许模型自适应切换 provider、静态/动态/脱壳/dump/hook/模拟路径。
Builder 只执行已冻结 tasks，嵌套 subcase 的写入范围和主项目保持隔离。
