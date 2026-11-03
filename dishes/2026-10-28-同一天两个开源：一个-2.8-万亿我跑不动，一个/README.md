# 🍲 同一天两个开源：一个 2.8 万亿我跑不动，一个 1.7B 今晚就能跑

> **菜品编号**：`2026-10-28-同一天两个开源：一个-2.8-万亿我跑不动，一个`
> 📢 公众号：硅基饲料 · 🗓️ 发布：2026-10-28 · 状态：✅ 已发布
> **热度**：🔥🔥

---

## 📝 摘要

昨晚十一点多，我拿到一个空字符串。

我写了个小脚本，把一段有 bug 的 Python 函数丢给刚出的 Kimi K3.1 Pro，让它修好。返回 200，没报错，没超时，打印出来的正文是空的。

第一反应是我自己写错了。把整个返回体 dump 出来看 usage，一眼看到两行：

completion_tokens 900，reasoning_tokens 897。

它把整个输出预算用来思考了，一个字都没留给我。

我盯着那两个数字看了十几秒。不是愤怒，是一种很熟悉的感觉——工具变得太聪明之后，你原来的用法就开始出问题了。

## 📎 参考资料

- https://www.liquid.ai/blog/lfm3
- https://huggingface.co/collections/LiquidAI/lfm3

## 🔗 关联

- 公众号「硅基饲料」（ID: `AI_Feed`）同步科普文章
- 内容仓库：[panda-chef/panda-hotpot](https://github.com/panda-chef/panda-hotpot)
