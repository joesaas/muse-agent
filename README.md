# muse-agent

一个照 **Muse 的设计思想** 复刻的 super agent：设计完全参考 Muse（材料是 [Muse 设计站 19 章](https://joesaas.github.io/muse-design-site/)），目的是**通过复刻来学习它的架构**。

不追求速度，追求两件事：**模块化设计**与**可长期维护**。底层执行不做重：每个模块先把职责、接口契约和数据流做对，只带最小可运行实现或适配层占位——但整个项目是真能跑的。

- 语言：Python 3.11+，**运行时零第三方依赖**（只有标准库）
- 默认 MockProvider：无 API Key、离线即可跑通全系统与全部测试
- 真实模型：OpenAI 兼容 adapter，按名从环境变量取 Key

## 快速开始

```bash
git clone https://github.com/joesaas/muse-agent
cd muse-agent

# 方式一：免安装直接跑
PYTHONPATH=src python3 -m muse_agent --home /tmp/muse-agent-demo demo

# 方式二：安装为命令
pip install -e .
muse-agent init          # 在 ~/.muse-agent 生成家目录
muse-agent doctor        # 看模块、skills、tools、连接器状态
muse-agent run "你好"
muse-agent chat          # 交互模式
muse-agent demo          # 脚本化演示：对话 + 工具调用 + 子代理
```

demo 片段（mock 模型，确定性输出）：

```
— 2) 工具调用（echo）
工具结果：echo -> 工具调用走通了
— 3) 工具调用（now）
工具结果：now -> 2026-10-18T22:22:14+08:00
— 4) 子代理
工具结果：echo -> 我是子代理，我完成了任务
```

接真实模型：

```bash
export MUSE_AGENT_PROVIDER=openai-compatible
export MUSE_AGENT_MODEL=your-model
export OPENAI_API_KEY=...        # 只按名读取，永不落盘
muse-agent run "你好"
```

## 模块一览

Agent 该有的模块一个不少，每篇设计文档固定五节（职责 / 接口 / 交互 / 数据 / 边界）：

| 模块 | 管什么 | 设计文档 |
|---|---|---|
| core | 全系统数据契约、事件总线、错误类型 | [01-core-contracts](docs/modules/01-core-contracts.md) |
| llm | 模型供应商适配（mock / OpenAI 兼容） | [02-llm-providers](docs/modules/02-llm-providers.md) |
| prompts | 系统提示词分段注册表与拼装 | [03-system-prompt](docs/modules/03-system-prompt.md) |
| identity | IDENTITY/SOUL/USER/AGENTS 站立文件 | [04-identity](docs/modules/04-identity.md) |
| context | 上下文窗口与 token 预算 | [05-context](docs/modules/05-context.md) |
| context | 压缩（摘要替换）与恢复（快照） | [06-compression-recovery](docs/modules/06-compression-recovery.md) |
| memory | 两层文件记忆：MEMORY.md + 每日笔记 | [07-memory](docs/modules/07-memory.md) |
| skills | SKILL.md 技能：发现、索引、触发 | [08-skills](docs/modules/08-skills.md) |
| tools | 工具注册表与内置工具（沙箱内） | [09-tools](docs/modules/09-tools.md) |
| connectors | 外部服务适配契约 | [10-connectors](docs/modules/10-connectors.md) |
| subagents | 子代理派生（全量快照副本）、交回 | [11-subagents](docs/modules/11-subagents.md) |
| approval | HITL 风险分级审批 | [12-approval](docs/modules/12-approval.md) |
| security | 凭证按名取用、输出脱敏、surrogate 缝 | [13-security](docs/modules/13-security.md) |
| scheduling | cron 判定与 hooks 唤醒 | [14-scheduling](docs/modules/14-scheduling.md) |
| goals | 目标与跟踪项（数据而非聊天记录） | [15-goals](docs/modules/15-goals.md) |
| runtime | session 组装与 Agent 循环 | [16-runtime](docs/modules/16-runtime.md) |
| home | 家目录布局（一切所知皆文件） | [17-home-layout](docs/modules/17-home-layout.md) |

总架构与分层：[docs/architecture.md](docs/architecture.md) · 19 章逐章映射：[docs/chapter-map.md](docs/chapter-map.md) · 路线图：[docs/roadmap.md](docs/roadmap.md)

## 目录结构

```
src/muse_agent/
  core/         数据契约、事件总线、错误 —— 全系统唯一地基
  llm/          provider 适配（base 协议 / mock / openai_compatible）
  prompts/      系统提示词分段（sections 注册表 + builder）
  identity/     站立文件加载
  context/      窗口管理、压缩、恢复快照
  memory/       文件记忆存储与检索
  skills/       SKILL.md 加载与注册表
  tools/        工具注册表与内置工具
  connectors/   连接器契约与参考实现
  subagents/    子代理管理器
  approval/     审批策略
  security/     凭证与脱敏
  scheduling/   cron 判定、hooks
  goals/        目标与跟踪
  runtime/      session 组装、agent 循环
  home/         家目录布局
  cli.py        命令行前端（前端可替换，运行时不变）
examples/skills/  示例 skill
tests/            unittest 单测（零依赖）
templates/home/   家目录模板说明
```

## 家目录（运行时数据，归用户所有）

```
~/.muse-agent/
  IDENTITY.md  SOUL.md  USER.md  AGENTS.md   站立文件
  MEMORY.md                                  精选长期记忆
  memory/                                    每日笔记
  skills/                                    用户 skills
  sessions/                                  恢复快照
  goals.json                                 目标与跟踪项
  config.toml                                可选配置（秘密永不写这里）
```

## 测试

```bash
make test        # 或 PYTHONPATH=src python3 -m unittest discover -s tests -v
```

## 诚实边界

这是学习性复刻：借鉴的是 Muse 公开可归纳的设计思想。设计站中证据等级为「未证实 / 无法核实」的 Muse 内部细节，本项目不声称与其一致，只采用设计思想并标注取舍（每篇模块文档的「边界与代价」一节）。真实模型流式、向量检索、多端前端等未完成项都在 roadmap 中，接口已预留。
