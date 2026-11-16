# 当前发布验收

当前版本 **1.2.1**，Windows x64完整组件分发；Codex主部署，Pi/Claude按薄入口适配。
当前功能、安装、任务交接和宿主适配按已约定范围完成。当前权威状态见
[CURRENT-STATE.md](CURRENT-STATE.md)，逐项功能见[USER-REQUIREMENTS-REVIEW.md](USER-REQUIREMENTS-REVIEW.md)。

## 发布完成需要的依据

1. 仓库本地路由、领域正文、保全/来源清单与合同一致，fresh clone不依赖旧安装记录。
2. 默认安装真实REA、官方Spec和原生Craft；缺任何核心不得安装成功。
3. 选定宿主完成正确入口：Codex用户级指引，Pi/Claude显式成果项目连接；
   安装记录或发现CLI不能代替入口。命令仅由[唯一部署入口](AGENT-BOOTSTRAP.md)维护。
4. 共用核心有代表性完整运行，宿主适配有实际接口合同检查；不强制每宿主完整模型实测。
5. 当前工程检查与当前源码/日志绑定；本机部署检查、来源/二进制身份及路径边界可核实。
6. 规格来源、冻结任务、真实Craft写入/检查/清理、独立比较、失败修正和恢复路径已连通；
   组件参与、exit0或模型自述不能替代具体目标的行为验收。
7. 当前入口只有一个有效版本；历史状态/失败/未知保留为有范围的档案；文档、代码、
   清单与安装要求同步GitHub。最终静态收尾覆盖和修复见[FINAL-CLOSEOUT.md](FINAL-CLOSEOUT.md)。

## 实际记录

- `release/verification.json`：104产品+39复刻检查，0跳过，包含源码和日志摘要。
- `evidence/rf33/deployment-final.json`：已记录本机19项部署检查；快照不是新机器证明。
- `evidence/rf33/clean-install.json`：明确提交上的远端新克隆默认完整安装及重复检查。
- `evidence/rf33/owned-desk-completion.json`：无维护者专业追加的Codex完整应用交付。
- `evidence/rf33/pi-full-use.json`：Pi真实完整交付及多次期限退出后恢复；不宣称一次顺畅完成。
- `evidence/rf33/pi-native-identity.json`及归档索引：原生记录身份和原始字节保留。
- 三宿主项目入口/移除与官方Spec布局检查覆盖宿主接入；Claude完整模型运行未实测，
  该事实仍保留，但不是适配未完成或强制登录待办。

不将这些有限记录扩张成任意软件必定复刻成功、所有保护器可处理、所有系统可安装，
或永远无缺陷的承诺。当前边界由[能力矩阵](TARGET-CAPABILITY-MATRIX.md)和具体案例Evidence决定。
历史版本的验收段落移至[历史档案](history/RF-33-STATE-AND-ACCEPTANCE.md)，不再整段注入当前入口。
