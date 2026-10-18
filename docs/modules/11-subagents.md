# 子代理 subagents

> 对应 Muse 设计站章节：ch07 子代理编排

## 职责
子代理是一个完整的 Agent 实例，为一件自包含任务而生：派生时拿到父上下文的**全量快照副本**（深拷贝，不是共享引用、不是切片），做完以「事件 + 返回值」交回，父上下文不被子代理改动。深度默认上限 2。

## 对外接口
- SubagentManager(parent_session, max_depth=2).spawn(task) -> SubagentResult
- 事件：subagent.spawned / subagent.finished

## 与谁交互、传什么
runtime/agent 同构复用（子代理内部还是同一个 Agent 循环）；通过 EventBus 向父会话报告。

## 数据与状态
输入是任务简报字符串 + 快照；输出是 SubagentResult(task, output, session_id, ok)。

## 边界与代价
进程内实现是参考形态：长任务应换线程/进程/远程执行器，接口不变。子代理之间不直接通信，一切经主代理中转。
