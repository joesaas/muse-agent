# LLM 适配层 llm

> 对应 Muse 设计站章节：ch03 LLM 设计

## 职责
把模型供应商藏在一个方法之后：complete(messages, tools) -> LLMResponse。运行时不感知供应商，换模型只换 adapter。

## 对外接口
- `LLMProvider 协议：complete()`
- `LLMResponse：text + tool_calls + usage`
- `build_provider(config) 工厂`
- `MockProvider（离线、确定性）/ OpenAICompatibleProvider（urllib 实现 OpenAI 兼容协议）`

## 与谁交互、传什么
runtime/agent 调用；读取 config 与 security 提供的凭证名（只读环境变量名，不存值）。

## 数据与状态
输入是 core.Message 列表与 ToolSpec 列表；输出统一为 LLMResponse，供应商私有格式在 adapter 内消化。

## 边界与代价
MockProvider 是规则引擎，只为跑通系统与测试，不是智能来源。真实供应商的特有能力（缓存、流式）应新增 adapter，不要污染运行时。
