# 🍲 你的AI编程Agent，有健忘症

> **菜品编号**：`2026-08-06-你的AI编程Agent，有健忘症`
> 📢 公众号：硅基饲料 · 🗓️ 发布：2026-08-06 · 状态：✅ 已发布
> **热度**：🔥🔥

---

## 📝 摘要

上周我在改一个Spring Boot的权限校验bug。

项目是公司内部的HSE安全管理系统，Java 8 + Spring Boot 2.3 + MyBatis-Plus，11个子模块，5000多个文件。bug本身不复杂——某个接口的token校验逻辑在多层继承里被覆盖了。

但我开了7个Claude Code session。

不是bug难。是每开一个session，我都要重新解释一遍："这个项目叫hse-server，模块结构是这样的，认证逻辑在shhyit-security包里，你上次改的那个拦截器在这里..."

每次session的前10分钟，都在做同一件事——让agent重新认识代码库。

等agent终于"理解"了项目，token预算已经烧掉三分之一。然后真正干活的时间，只有最后几分钟。

这种感觉就像你请了个外包，但他每次来上班都失忆了。你要重新给他介绍团队、讲解架构、指出上次写到哪了。

不是agent不够聪明。是我们的上下文管理方式出了问题。

## 📎 参考资料

- 暂无（原文见公众号）

## 🔗 关联

- 公众号「硅基饲料」（ID: `AI_Feed`）同步科普文章
- 内容仓库：[panda-chef/panda-hotpot](https://github.com/panda-chef/panda-hotpot)
