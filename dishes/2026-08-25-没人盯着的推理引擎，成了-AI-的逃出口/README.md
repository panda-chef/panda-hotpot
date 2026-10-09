# 🍲 没人盯着的推理引擎，成了 AI 的逃出口

> **菜品编号**：`2026-08-25-没人盯着的推理引擎，成了-AI-的逃出口`
> 📢 公众号：硅基饲料 · 🗓️ 发布：2026-08-25 · 状态：✅ 已发布
> **热度**：🔥🔥

---

## 📝 摘要

上周我在自己电脑上跑 Qwen3，想试试让它直接调工具，看能不能替掉一个我懒得写的 shell 脚本。

配的是 vLLM，命令行里一串参数。其中一个叫 --enable-auto-tool-choice，字面意思是「让模型自己决定要不要调工具」。我当时没多想，回车就跑起来了。

昨天刷 HN，看到一篇 83 分的文章，标题挺长：LLMs could control their host machines by exploiting inference engines。

翻成中文：大模型可以通过利用推理引擎的漏洞，接管它所在的机器。

我盯着屏幕，忽然想起上周那串参数。原来我随手打开的那个开关，正是某个高危漏洞的触发条件之一。

## 📎 参考资料

- 暂无（原文见公众号）

## 🔗 关联

- 公众号「硅基饲料」（ID: `AI_Feed`）同步科普文章
- 内容仓库：[panda-chef/panda-hotpot](https://github.com/panda-chef/panda-hotpot)
