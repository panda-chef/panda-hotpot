# 🍲 给 AI Agent 上把锁——你的 API Key 正在裸奔

> **菜品编号**：`2026-08-03-给-AI-Agent-上把锁——你的-API-K`
> 📢 公众号：硅基饲料 · 🗓️ 发布：2026-08-03 · 状态：✅ 已发布
> **热度**：🔥🔥

---

## 📝 摘要

上周我开始让三个 Agent 同时干活。

一个用 Claude Code 写后端，一个用 Hermes Agent 管部署，一个用 Kimi K3 做代码审查。

很爽。尤其是 Graph Engineering 那套流程搭好之后，三个 Agent 各司其职，产出比我自己写快了两倍不止。

但爽了三天之后，我发现一个让我后背发凉的事。

我的 DeepSeek API Key，躺在至少四个地方。每个 Agent 的配置文件里一份，每个 MCP 服务器的环境变量里一份，还有个 shell 脚本为了方便直接硬编码了。

我当时盯着终端，脑子里只有一个念头：

这他妈跟把银行卡密码写在便利贴上贴显示器有什么区别。

---

## 📎 参考资料

- https://github.com/onecli/onecli
- https://github.com/surya-koritala/sigbound
- https://github.com/cocofhu/approving
- https://github.com/risa-labs-inc/BossConsole

## 🔗 关联

- 公众号「硅基饲料」（ID: `AI_Feed`）同步科普文章
- 内容仓库：[panda-chef/panda-hotpot](https://github.com/panda-chef/panda-hotpot)
