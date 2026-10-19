# 🍲 关掉思考之后，DeepSeek 20 秒写出了 654 行

> **菜品编号**：`2026-10-19-关掉思考之后，DeepSeek-20-秒写出了`
> 📢 公众号：硅基饲料 · 🗓️ 发布：2026-10-19 · 状态：✅ 已发布
> **热度**：🔥🔥🔥

---

## 📝 摘要

周五晚上，我想试试 DeepSeek 那个新版本。

我给它的需求很具体：做一个单文件 HTML 的打砖块游戏，键盘控制挡板，球反弹，有分数、生命、关卡递增，用 canvas，不依赖外部库，打开就能玩。

第一次，四千个 token，全花在思考上，正文一个字没写。

我以为是自己太小气，把预算提到一万六。第二次，一万六，还是全在思考。

第三次，我把思考强度压到 low。第四次，压到 minimal。

四次，正文都是零字符。

我盯着账单看了半天。返回体里的 usage 写得很清楚：completion_tokens 和 reasoning_tokens 是同一个数。也就是说，它把能用的额度全部用来想了，一个字都没剩下写答案。

翻回官方文档，才看到一句很不显眼的话：思考模式默认打开，强度默认 high。

我把它关掉，同一句话再问一次。

二十秒。六百五十四行。一个能跑的游戏。

## 📎 参考资料

- https://api-docs.deepseek.com/zh-cn/updates
- https://api-docs.deepseek.com/zh-cn/guides/thinking_mode/

## 🔗 关联

- 公众号「硅基饲料」（ID: `AI_Feed`）同步科普文章
- 内容仓库：[panda-chef/panda-hotpot](https://github.com/panda-chef/panda-hotpot)
