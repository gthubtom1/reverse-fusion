# 共享工具仓库与当前成果项目

工具 checkout 提供路由、领域技能、provider bootstrap 和代码；当前成果项目提供目标、
case、规格、候选及测试。`bridge`、`session`、`build`、`craft` 的 `--project-root`
指定成果项目，省略时使用调用时的当前目录。安装、contracts、provider bootstrap、
宿主 handshake 以及 `accept --fixture ...` 仍属于工具仓库；fixture 验收不是用户目标验收。

跨项目命令使用 checkout 的 venv，路径有空格时正确引用。下文 `[python]` 指这个
解释器，`[project]` 指软件A的绝对目录，所有相对任务路径以 `[project]` 为根。

## 按实际阶段接续

1. **识别与分析**：先路由再读取 `required_read_paths`。这些绝对路径指向技能仓库，
   不是软件A。识别目标身份、摘要和实际技术栈后，细化领域路由并记录同一 case：

   ```text
   [python] -m reverse_fusion bridge --project-root "[project]" --source local --hint "真实技术栈及待研究行为" --mode analysis --case-root work/case --record
   ```

   原版只读；恢复或建立同一个 scope/timeline/workitems/evidence，保留网络范围和未知项。
   先做可验证的行为切片，发现 JS/native/设备等边界后读相关领域资料。
   大型目录、二进制字符串和完整反编译写文件，返回摘要与检索结果，避免整份输出挤占上下文。

2. **检查执行能力**：`[python] -m reverse_fusion doctor` 的总 `pass` 只检查仓库合同。
   `components` 分别报告本地 REA、Spec CLI、Builder 和 Craft 的可见状态。
   REA 固定 manifest 不是安装；入口存在不是握手，catalog 可见也不是 provider 实跑。
   按需要准备 REA，再观察它实际支持的接口。缺 REA 可用已安装的原生工具继续分析，
   将原始输出作为明确来源的证据，但 REA 原生 bundle/proof/ledger 不得伪造为已完成。

3. **证据到规格**：选定被证据支持的功能，写 feature 的 spec/plan/tasks，任务引用原
   Evidence、观察与 unknown。区分 observed/inferred/designed。需要官方 Spec CLI 时按
   实际安装版命令执行；当前宿主可编写和冻结任务文件，但这不等于官方 CLI 执行。
   阅读 reconstruction 技能的交接检查和验收规则。关键未知项只阻断依赖它的任务。
   授权/设备标识、启动状态、功能放行、服务端调用、持久化和错误路径属于行为依赖：
   不能因为恢复了 UI 或资源格式就假定它们与所选功能无关。若原本交付是复刻原软件，
   不得自行改成无授权依赖的本地资源管理器；交付差异需有用户的范围决定和来源引用。

4. **冻结后再实现**：切到 reconstruction 仍记录在同一 case。先运行：

   ```text
   [python] -m reverse_fusion bridge --project-root "[project]" --source local --hint "已选定功能的独立实现" --mode reconstruction --case-root work/case --record
   [python] -m reverse_fusion session prepare --project-root "[project]" --case-root work/case --handoff-manifest work/case/notes/handoff-manifest.json --review-file work/case/notes/semantic-review.md --receipt work/case/session.json --workspace candidate --tasks T-001 --task-file specs/feature/tasks.md --research-file work/case/research.json --allowed-output answer.py
   ```

   交接清单格式复用 [handoff-manifest](../skills/reconstruction/references/handoff-manifest.md)，
   不创建第二份 Evidence 或 obligation 账本。先执行原 case-review，审查原版调用关系、
   关键未知和交付差异，再留下语义审查记录。准备阶段会调用已有只读 checker，拒绝
   关键未解决 unknown、文件摘要失配、跨 case 或不同任务文档；把引用文件和审查记录
   一起冻结。receipt 在已记录 case 内时会自动绑定该 case，漏写 case 参数也不能跳过。
   **机械 PASS 和审查记录存在均不证明语义正确**，遗漏关键依赖仍需独立审查发现。
   缺正式交接证据就继续分析，不伪造 REA 输出凑齐清单。

   当前 Codex 是默认单一编码者，不需要第二个模型或 CLI。任务和研究输入先冻结、输出
   白名单先定义，再写候选。只运行 `session --help` 不算 prepare。已有输出采用下一批
   新 receipt，不补造“写入前”快照。`--allowed-output` 可以重复列出本批具体文件。
   不绑定 case 的通用 session 仅观察文件边界，不得作为复刻交接门已通过的证明。

   ```text
   [python] -m reverse_fusion session check --project-root "[project]" --receipt work/case/session.json
   [python] -m reverse_fusion session refine --project-root "[project]" --receipt work/case/session.json
   [python] -m reverse_fusion session finish --project-root "[project]" --receipt work/case/session.json
   ```

   `candidate` 只观察文件边界及冻结输入，不证明功能通过。这些工具不提供 OS 写入沙箱。

5. **独立验收与交付**：实际构建、运行候选，比较原版与候选的选定输入输出，覆盖适用
   的错误/边界/状态与副作用，用故意错误候选检查比较器确实会失败。需要 REA 验收时
   使用真实接口和输出，保留 required open、unknown、unsupported。单侧候选测试通过
   不能证明原版行为等价；静态资源校验不能证明游戏内运行、在线服务或界面行为相同。
   将执行记录、源码与输入摘要、差异、cleanup 和恢复入口留在同一 case。

6. **恢复**：使用相同 project root 和 case root：

   ```text
   [python] -m reverse_fusion bridge --project-root "[project]" --hint "本轮后续问题" --mode follow-up --case-root work/case
   ```

   follow-up 保留先前阶段的规格和验收要求，不会因为“继续”就把它们清空。

## 四个组件实际承担的工作

| 组件 | 何时算实际使用 | 未使用时怎么报告 |
|---|---|---|
| Reverse | 调用路由、读领域正文并执行分析方法 | 仅目录存在不能算已执行分析 |
| REA | 调用真实官方接口，留存该目标的原生输出 | 原生工具 fallback 可继续，REA 验收仍未验证 |
| Spec | 证据引用的需求/任务已产生并冻结；官方 CLI 执行另行记录 | 仅阅读技能、普通待办列表不算已完成规格交接 |
| Craft/Builder | 默认使用当前宿主并执行 session 生命周期 | 原生 Craft R46 仍 unsupported；直接编辑不算 session；`craft` fixture copy 不算原生 Craft |

不用为了“四合一”强行启动四个程序。按阶段启用，并在交付中报告实际执行的部分；
当前产品的可验证路径是 Reverse + 按需 REA + 证据化 Spec 文件 + 当前会话 Builder。
