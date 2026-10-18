# 技能系统 skills

> 对应 Muse 设计站章节：ch08 Skills 技能系统

## 职责
Skill 是数据不是代码：一个目录 + SKILL.md（frontmatter 写 name/description/triggers，正文是 playbook）。系统只把索引（名+描述）注入提示词，用到时才全文加载——渐进披露省上下文。

## 对外接口
- `Skill 数据类 / parse_frontmatter / load_skill_file`
- `SkillRegistry.discover(*dirs) / index_lines() / match(text) / get(name)`

## 与谁交互、传什么
runtime/session 发现 home/skills 与示例目录；prompts 注入索引行；CLI skills 子命令列出。

## 数据与状态
SKILL.md 文件。frontmatter 只解析 name/description/triggers 三键，不引完整 YAML 依赖。

## 边界与代价
触发匹配是关键词版：简单、可预测。语义路由以后在 match() 后替换，不改 skill 格式（格式要跨 Agent 通用）。
