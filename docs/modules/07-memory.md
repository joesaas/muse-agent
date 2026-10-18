# 记忆 memory

> 对应 Muse 设计站章节：ch15 Memory 设计

## 职责
两层文件记忆：精选长期记忆 MEMORY.md（紧、原地编辑）与每日笔记 memory/YYYY-MM-DD.md（只追加）。检索是关键词打分，接口先行，向量检索以后可替换实现而不动文件格式。

## 对外接口
- `MemoryStore.append_daily / append_curated`
- `MemoryStore.search(query) -> [MemoryHit(source, line, text, score)]`
- `MemoryStore.index_text()（注入提示词的精选记忆）`
- CLI：muse-agent memory <词>

## 与谁交互、传什么
prompts 的 memory 段消费 index_text；CLI 与未来的工具层消费 search。

## 数据与状态
用户拥有的 Markdown 文件。命中带来源文件与行号，可追溯——记忆必须能说清出处。

## 边界与代价
关键词检索召回有限，这是刻意的起步选择：先保证格式与写入纪律，再升级检索。记忆内容是上下文，不是授权来源。
