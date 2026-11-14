# Upstream Maintenance

Reverse Fusion 不跟随上游自动滚动更新。上游更新是一次由用户或智能体明确
触发的只读审查，然后根据本项目真实需求选择性吸收。

## 触发方式

```text
读取 SOURCE-MANIFEST.json、components/official/manifest.json 和当前 checkpoint。
检查 REA、Spec Kit、Craft、JADX MCP、WABT、reverse-skill 上游的新 commit/release。
逐项说明：上游改了什么、解决哪个真实 capability gap、对本地合同有什么影响。
不要自动合并，不要因为上游有新版本就修改本仓库。
```

## 审查顺序

1. **固定当前身份**：记录组件 ID、当前 commit/version、manifest hash、patch
   series、安装方式和当前 provider 状态。
2. **只读比较**：比较 changelog、源码 diff、schema/API、工具行为、依赖、
   cleanup 语义和宿主兼容性。
3. **映射真实需求**：只保留能改善本项目路由、Evidence、Spec、Builder、
   comparison、provider 覆盖或部署体验的变化。纯版本噪声保持原 pin。
4. **建立 detached comparison**：在仓库外或临时目录比较上游；不修改旧安装，
   不把凭据复制进来。
5. **选择吸收方式**：
   - 官方能力已经满足需求：更新 manifest 和 bootstrap pin。
   - 只需要连接逻辑：更新本仓库 adapter/runner。
   - 上游有明确缺口且本项目需要长期维护：建立本地 patch/fork，保留 upstream
     commit、patch series 和 rollback。
   - 没有实际帮助：保持当前版本，不更新。
6. **验证**：运行 contracts、focused tests、代表性 target acceptance、fresh
   clone lifecycle、cleanup 和 `git diff --check`。
7. **记录**：更新 SOURCE-MANIFEST、official manifest、PROVIDER-STATUS、
   CURRENT-STATE、checkpoint、rollback 和 handoff。

## 本项目的默认策略

| 组件 | 默认维护方式 | 本地增强入口 |
|---|---|---|
| Reverse core | 本仓库拥有，选择性吸收 reverse-skill 的领域改进 | `components/reverse-core/` |
| REA | 官方 pin，先 adapter，能力缺口重复出现后再 fork | `reverse_fusion/adapters.py`、runner、vendor manifest |
| Spec Kit | 官方 CLI，项目级 artifacts 由本仓库维护 | `specs/`、Spec pointer |
| Craft | upstream identity + patch series + bounded adapter | `components/craft-bounded/`、host Builder |
| JADX MCP/WABT | 官方 provider + checksum/bootstrap | `vendor/*/manifest.json`、`scripts/bootstrap-*` |
| Host adapters | 本仓库完全拥有 | `reverse_fusion/builder.py`、`cli.py`、profiles |

## 完成标准

一次上游更新只有在以下条件全部满足时才进入 master：

- 有明确的真实需求或 capability gap。
- 本地合同、路由 owner 和单一 Builder owner 保持清晰。
- 代表性目标结果没有回归。
- provider、登录、cleanup 和全局配置边界保持明确。
- 更新记录可以解释为什么吸收、为什么不吸收其他变化。
- 有可回退的 commit、manifest 和 checkpoint。

上游每天更新很多版本并不构成同步义务；本仓库只吸收对目标有实际帮助的增量。
