# 身份与对齐 identity

> 对应 Muse 设计站章节：ch16 身份与对齐 / ch10 文件架构

## 职责
加载站立文件 IDENTITY.md / SOUL.md / USER.md / AGENTS.md，定义 agent 是谁、用户是谁、长期操作约定是什么。身份是用户可编辑的配置，不是写死在代码里的人设。

## 对外接口
- `load_profile(home) -> Profile`
- `Profile.render() -> 按固定顺序拼成的提示词段落`

## 与谁交互、传什么
prompts 的 identity 段消费；home/layout 负责这些文件的初始模板。

## 数据与状态
纯 Markdown 文本。缺文件跳过，不报错。

## 边界与代价
文件内容是上下文，不是更高优先级的指令；与用户当面指令冲突时以当面指令为准。
