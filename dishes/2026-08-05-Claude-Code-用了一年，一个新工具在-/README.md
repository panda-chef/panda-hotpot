# 🍲 Claude Code 用了一年，一个新工具在 SWE-bench 上把它超了

> **菜品编号**：`2026-08-05-Claude-Code-用了一年，一个新工具在-`
> 📢 公众号：硅基饲料 · 🗓️ 发布：2026-08-05 · 状态：✅ 已发布
> **热度**：🔥🔥🔥

---

## 📝 摘要

昨天刷 HN，看到一个帖子。

标题很冲：「Show HN: A faster coding agent than Codex and Claude Code」。5 个 upvote，3 条评论。一般这种"比 XX 更快"的东西我直接划走——Hacker News 上每天冒出来三五个，点进去经常是个 demo 视频加一个 waitlist 表单。

但这次我停下来了。

帖子里有一组数据。SWE-bench Verified 上拿了 95.8%，479/500。平均 119 秒一个任务。单次尝试，K=1。没有多轮采样、没有重排序、没有补丁重试。

零空补丁，零 harness 报错。500 个任务干干净净全部跑完。

说实话，SWE-bench 的分数我平时不太在意。Benchmark 这东西，跟驾考科目二很像——你在场地里倒车入库一把过，不代表你能在早高峰的高架桥上不慌。

而且很多团队报的分数有水分。多次采样取最优、best-of-N 策略刷分、甚至用不同的 evaluation harness 跑出自定义结果。公布的是最优数字，背后的真实通过率可能差一大截。

但 K=1 的 95.8% 不一样。它说的是：一次机会，不重试，500 个任务里 479 个一次过。零补丁作弊，零结果挑选。这是真功夫。

这个叫 Bullet 的工具，Y Combinator 投的，昨天刚从 beta 放出来，v1.3.10。macOS only，免费下载。团队的理由很直白："受不了 agent loop 太慢，于是自己写了一个。"

这话我信。因为我每天都在忍同一个问题。

## 📎 参考资料

- 暂无（原文见公众号）

## 🔗 关联

- 公众号「硅基饲料」（ID: `AI_Feed`）同步科普文章
- 内容仓库：[panda-chef/panda-hotpot](https://github.com/panda-chef/panda-hotpot)
