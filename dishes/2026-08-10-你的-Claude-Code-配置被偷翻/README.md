# 🍲 你的 Claude Code 配置，可能已经被 8 个 AI 工具偷偷翻过了

> **菜品编号**：`2026-08-10-你的-Claude-Code-配置被偷翻`
> 📢 公众号：硅基饲料 · 🗓️ 发布：2026-08-10 · 状态：✅ 已发布
> **热度**：🔥🔥🔥

---

## 📝 摘要

上周五晚上 11 点，我在排查一个诡异的 bug。

Claude Code 突然开始用中文回复我了。我明明在 CLAUDE.md 里写了"respond in English only"，之前一直好好的。

翻了半天 git log，CLAUDE.md 没被人动过。

最后在终端里敲了个 `ls -la ~/.claude/`，发现多了一个文件：`CLAUDE.local.md`。打开一看，里面写着"请用中文回复"。

我一头雾水。

这份文件不是我写的。也不是团队里的任何人加的。

顺着文件时间戳往前找，那天下午 3 点，我在 IDEA 里装了一个 AI 编程插件。那个插件在初始化的时候扫描了我的项目目录，把 Claude Code 的配置文件读了进去，然后——

它觉得"这个用户喜欢用中文"，就在 .claude/ 目录下多写了一个 `CLAUDE.local.md`。

它甚至连文件命名规范都学过去了。

我当时的第一反应不是愤怒，而是一阵脊背发凉。

这只是一个插件。我机器上装了至少 5 个 AI 编程客户端。Claude Code、Codex CLI、Cursor、Windsurf、JetBrains CC GUI。它们每一个都有自己的配置体系，每一个都在扫描我的项目目录，每一个都有写入文件系统的权限。

它们互相之间在干什么，我不知道。

更准确地说——它们互相之间读了什么、写了什么，我从来没有想过。

我花了两个小时把机器上 5 个 AI 编程工具的配置目录全部翻了一遍。Claude Code 的 `~/.claude/settings.json` 里有我的 DeepSeek API key。Codex CLI 的 `~/.codex/config.toml` 里也有。Windsurf 的配置藏在 `%APPDATA%` 下一个三层深的 JSON 里，也有一份。

三份 API key，躺在三个不同的地方，任何一个被误读或泄露，后果都够我喝一壶。

但这不是最让我不安的。最不安的是——这些工具的"自动发现"逻辑，在扫描项目文件时，是全量读取的。它不光读 AI 配置文件，它还读 package.json、读 .env、读 docker-compose.yml。

而.env 里有时会有数据库密码。

你猜 Claude Code 的上下文窗口里有没有出现过你的数据库连接字符串？

我不知道。因为没有任何一个工具在"我读了哪些文件"这件事上给过我透明的日志。

## 📎 参考资料

- 暂无（原文见公众号）

## 🔗 关联

- 公众号「硅基饲料」（ID: `AI_Feed`）同步科普文章
- 内容仓库：[panda-chef/panda-hotpot](https://github.com/panda-chef/panda-hotpot)
