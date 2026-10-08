"""熊猫厨子 AI 火锅店的厨房工具集。

模块划分：

* :mod:`scripts.dishlib` —— 菜品数据模型与元信息解析（底层库）
* :mod:`scripts.sitegen` —— 主菜单 Markdown 与静态站点 HTML 渲染
* :mod:`scripts.build_menu` —— CLI：生成 README 菜单 + docs/index.html
* :mod:`scripts.check_dishes` —— CLI：结构与链接校验（CI 使用）
* :mod:`scripts.new_dish` —— CLI：新菜脚手架
"""

__all__ = ["dishlib", "sitegen"]
