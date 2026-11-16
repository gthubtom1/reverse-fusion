# 独立运行原版与候选

当行为可以通过程序参数、标准输入与输出观察时，使用共享工具的 `compare`，
避免每个项目重新拼接执行、超时、摘要与比较逻辑。界面、文件副作用、协议和设备
效果仍要用相应观察方法；不能拿命令输出一致代替它们。

在当前成果项目保存经过审查的计划，所有cwd和sources是该项目相对路径。
argv是独立参数数组，第一项为实际运行时路径，不拼接shell文本：

```json
{
  "version": 1,
  "scope": "明确的本次输入输出行为范围",
  "original": {"argv": ["实际Python路径", "main.py"], "cwd": "original", "sources": ["original/main.py"]},
  "candidate": {"argv": ["实际Python路径", "main.py"], "cwd": "candidate", "sources": ["candidate/main.py"]},
  "cases": [{"id": "正常输入", "stdin": "实际输入\n"}, {"id": "错误输入", "stdin": ""}],
  "timeout_seconds": 5
}
```

`[venv-python] -m reverse_fusion compare --project-root [当前项目] --plan [计划相对路径] --output [新记录目录]`

工具分别运行两侧，保留原始stdout/stderr字节(base64)、退出码、耗时、Windows
Job峰值内存、计划与源码摘要。不同源路径和不同源码身份是最低独立性要求，仍需
审查是否偷用了原件或只覆盖表面功能。比较后输入变化、缺运行时或超时返回unknown；
输出/退出不一致返回fail；有限观察全部相同才pass。已有记录拒绝覆盖。
Windows进程先暂停创建，加入Job后才运行，结束/超时均清理其拥有的后代；该机制
不限制程序可写路径或网络行为，计划必须符合用户范围。工具不执行shell展开。

为了核实比较器有效，使用单独错误候选运行一份新计划，必须确实失败；不能修改原
计划摘要、过滤失败字段或改预期凑通过。源码、补丁、混合交付都要保留不同原件与
产物身份，并另外核实对应副作用、安装/回滚和实际界面行为。

结果是仓库自有的有限比较记录，不是REA原生proof。需要官方proof/coverage/ledger时
继续使用实际接口和经过审查的来源映射，保留真实的unknown及未闭合义务。
