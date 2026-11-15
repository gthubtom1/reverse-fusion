# 真实组件链有限交付报告

本feature已完成官方Spec工作流、真实Craft实现、开发49与维护79有限对照、错误变体检验及官方converge审查。最终converge结果另见evidence/final-integration/converge-report.md，不能从任务checkbox推导。整软件没有复刻完成。

## 三项结果分别记录

| 结果层 | 实际证据与范围 | 结论 |
|---|---|---|
| 规格符合 | FR-001～FR-007的K/q/R转换、类型、顺序、fallback、zh-CN、浅复制、精确异常；FR-008～FR-010治理与历史停止/后续授权；52项原生检查 | 有限feature范围符合 |
| 原版行为对照 | 49具名开发场景分别运行原/候选，49/49；维护预承诺79场景79/79；7故意错误变体真实失败 | 只支持固定49＋79集合及固定环境 |
| 独立运行 | 候选纯ESM，无导入原worker/定义；开发候选独立Node进程执行；维护独立读取/比较固定候选 | 纯函数候选可独立运行；不等于完整软件或OS隔离 |

正式候选为case内craft/app/grouping.mjs，SHA256 e56f763198367f7ab9c764c633c574d607638ac0c6858cb07090fd41028bed43；测试craft/app/tests/grouping.test.mjs，SHA256 2e8b9d1f601a2bd839af54a854216e1169e9d515696cc254be90bc0e347c1d64。候选仅导出K/q/R；独立分步判断与父子循环实现，没有导入/复制原worker定义，所有写/编辑/检查通过真实native Craft。

原生prepare仅一次，宿主提供推理/内容；实际Workspace/write/edit/command来自固定Craft engine。K/q测试先退出1后22/22；R合同测试先退出1后独立实现，最终52/52。最后修改后的全部冻结检查已重跑；return_summary、cleanup成功，同receipt session check/refine/finish成功、phase finished、result candidate。50冻结输入在finish时摘要未变，全部Spec补充preflight摘要也未变；退出后才更新tasks/context，旧manifest/任务/时间线原字节与receipt保留。

## 独立维护验收

维护结果绑定同一候选SHA、fixture d3e7248bcbd5700645b6953780fdf3ca078a54d195dccb2c9c921e029eecd0a7与comparator 1a3544acc188423dda2651c55b8fc8bc888c872f92863bd6745570079db027aa，79/79匹配。原件在verification内；作者在session finished后按用户新增授权只读取independent-result.json、negative-controls.json和native-static-run/summary.json三份结果，并原样归档。不读取fixture、比较器源码或其他私有原始文件。

| 故意错误变体 | 实际差异数（79场景） |
|---|---:|
| base-inversion | 9 |
| reverse-filter-order | 1 |
| stringify-ids | 55 |
| fallback-deduplicate | 14 |
| reverse-child-sort | 26 |
| deep-clone-alias | 52 |
| swallow-errors | 6 |

7/7变体均expected-fail，说明维护比较器确实检出这些具体错误。没有将故意错误源写入正式候选，没有更改比较预期。

环境固定Windows x64、Node24.22.1、V813.6.233.17-node.58、ICU78.3、CLDR48.0、Unicode17.0；异常name/message精确，不比较stack。对象键顺序可规范化，数组顺序/类型/重复/缺失键/错误和alias不得隐藏。原worker SHA9219fce4e182f2f52d4009955099bf6d0cfc71e9a52af775e6f89a10e64dc849不变。

## REA实际参与与证明边界

真实原始JS静态分析、完整bundle、读回与reviewed ledger均有旧Evidence。本轮维护方实际分析候选和派生reference wrapper，并官方compare_javascript_export_shapes；K/q/R各返回真实Evidence ID但coverage均partial、paired_variants=0。作者只接收获准summary，未凭summary伪造完整native bundle；wrapper是派生材料，不是改过的原worker。维护方曾因Windows GBK辅助传输损坏中文被完整性门拒绝，失败原件保留；UTF8保真适配器重跑成功。此为传输适配问题，不刷新原ID、不将partial改等价。

本作者实际调用官方evaluate_reconstruction_coverage，声明3个非零surface/claim与真实候选owner摘要，不提交伪造verifier/package proof。结果status unknown，8项原因：三个owner distribution unknown、两个package proof missing、三个verifier missing。该输出原样保存，不能以命令exit0解释为通过。首次将jsrg_unknown图ID误用于coverage lifecycle Unknown引用字段被官方拒绝；失败输入/输出保留，第二次按schema纠正引用命名空间。全部140个图unknown仍在完整原bundle内，原顶层lifecycle Unknown数组为空；没有关闭或删除任何图unknown。

实际官方build_reconstruction_obligation_ledger再次返回33required_open、0verified、status unknown、coverage partial。原完整bundle和原7行为v2＋3治理v1声明未变，没有owner/proof关闭新增。verify_reconstruction在实际MCP catalog存在，但其schema消费既有官方process/structural comparison Evidence，不能把本有限Node harness JSON直接当原生runtime proof；CLI同名探测不存在亦保留。此workflow没有可提交的相应原生runtime proof，明确unsupported，不声称REA已经原生证明128输入等价。

T021的“可用则提交真实proof/coverage；不支持保留unsupported”条件已按实际能力完成记录，不是取得native ready。原REA开放义务和完整语义图1621unknown（本范围140）保留；有限harness验收与native readiness分别报告。

## 保留未知、退出与后续

原scope、原worker、旧feature、原生输出与E-019历史pin修正前后不变。FR-010/SC-004保留Spec交接先停止，维护接受后同feature实现的真实顺序。后端授权/服务器/游戏/设备行为仍Unknown，WI-008挂起；没有网络、完整worker、目标授权、服务器或游戏操作。不依赖纯函数切片的未知不新增此切片许可门。

原生Craft报告无常驻server，直接命令与开发比较子进程均返回；session观察器不启动helper。未认证OS隔离或完整后代包含。当前receipt已finished，不会在更新过的Spec进度上复用旧租约。

后续原生证明若需要，应单独提交真实受支持verifier/package Evidence并通过官方接口，保持旧失败/partial/open历史；若继续整软件目标，应恢复WI-008并以原case确定下一个已授权分析/验证切片，不能把此纯函数模块当完整SkinForge。无需为已接受维护结果再次询问用户。
