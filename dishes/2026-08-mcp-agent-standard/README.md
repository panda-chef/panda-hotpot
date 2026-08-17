# 🔌 AI Agent 统一标准：MCP 到底是什么？

> **菜品编号**：`2026-08-mcp-agent-standard`
> **热度**：🔥🔥（OpenAI 等五家公司达成 Agent 标准协议）
> **状态**：✅ 已发布（与公众号「硅基饲料」2026-08-07 文章同步）

---

## 这道菜是什么

2026 年 8 月，OpenAI 与四家竞争对手就 **AI Agent 的统一标准**达成协议——围绕 MCP（Model Context Protocol，模型上下文协议）和 Agent 技能/插件的互操作规范。这意味着不同公司的 AI 助手未来可以互相调用工具、共享技能。本菜品从零讲清楚：**MCP 解决什么问题、怎么工作、普通人怎么玩**。

## 科普要点（文章框架）

1. **发生了什么**：OpenAI 与四家对手统一 Agent 标准（Agent plugins / skills / MCP）
2. **MCP 是什么**：
   - 类比 **USB-C**：以前每个设备（工具/数据源）都要专用线（定制集成），MCP 让所有模型用一个统一接口连接所有工具
   - 由 Anthropic 2024 年提出，现已成事实标准
3. **MCP 怎么工作**（架构）：
   ```
   [AI 应用/Host]  ←→  [MCP Server]  ←→  [工具/数据源]
   （Claude/Codex/     （协议层，         （数据库、文件、
     各类 Agent）        负责翻译调用）       API、浏览器…）
   ```
   - **Host**：运行 AI 的应用（Claude Desktop、IDE 插件等）
   - **Server**：暴露工具的中间层（每个工具一个或多个 server）
   - **Client**：Host 与 Server 之间的连接器
4. **实际体验（熊猫厨子亲测）**：
   - 给 Claude 配置了云效 MCP（197 个工具：项目管理、流水线、代码仓库全打通）
   - 给 Codex 配置了 codegraph MCP（代码索引查询）
   - MySQL MCP：AI 直接查询数据库
   - 效果：AI 从"聊天机器人"变成"能干活的操作员"
5. **怎么自己玩**：30 分钟上手一个 MCP Server（demo 见 `code/`）

## 相关资料

- [materials/links.md](./materials/links.md) — 原始链接与规范文档
- [code/](./code/) — 可运行的 MCP demo（✅ 已上架）

## 待补充（TODO）

- [ ] 公众号文章正文
- [x] MCP demo 代码（30 分钟上手）
- [ ] 配置教程截图（云效/MySQL 实例）
