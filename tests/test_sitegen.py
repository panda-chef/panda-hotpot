"""渲染层测试：README 菜单区块与静态站点首页。"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts import dishlib, sitegen  # noqa: E402

TEXT = """# 🍲 标题带 | 竖线

> 发布：2026-10-08 · 状态：✅ 已发布
> 热度：🔥🔥
"""


def make_dishes() -> list[dishlib.Dish]:
    published = dishlib.dish_from_text("2026-10-08-标题带-竖线", TEXT)
    wip = dishlib.dish_from_text(
        "2026-08-mcp", "# 🔌 MCP\n\n> **状态**：📝 制作中\n> **热度**：🔥🔥🔥\n"
    )
    return [published, wip]


class MenuTests(unittest.TestCase):
    def test_menu_block_has_header_rows_and_summary(self):
        block = sitegen.render_menu_block(make_dishes())
        self.assertIn(dishlib.MENU_START, block)
        self.assertIn(dishlib.MENU_END, block)
        self.assertIn("| 菜品 | 上架时间 | 状态 | 热度 |", block)
        self.assertEqual(block.count("\n| ["), 2)
        self.assertIn("共 **2** 道菜", block)

    def test_pipe_in_title_is_escaped(self):
        block = sitegen.render_menu_block(make_dishes())
        self.assertIn("标题带 \\| 竖线", block)

    def test_apply_menu_replaces_only_the_marked_block(self):
        readme = f"# 项目\n\n{dishlib.MENU_START}\n旧内容\n{dishlib.MENU_END}\n\n结尾\n"
        updated = sitegen.apply_menu(make_dishes(), readme)
        self.assertNotIn("旧内容", updated)
        self.assertTrue(updated.startswith("# 项目"))
        self.assertTrue(updated.endswith("结尾\n"))

    def test_apply_menu_requires_markers(self):
        with self.assertRaises(SystemExit):
            sitegen.apply_menu(make_dishes(), "# 没有标记的 README")


class SiteTests(unittest.TestCase):
    def setUp(self):
        self.html = sitegen.render_site_html(make_dishes())

    def test_one_item_per_dish(self):
        self.assertEqual(self.html.count('class="dish"'), 2)
        self.assertIn('class="badge ok"', self.html)
        self.assertIn('class="badge wip"', self.html)

    def test_stats_and_links(self):
        self.assertIn("<b>2</b><span>道菜（菜品目录）</span>", self.html)
        self.assertIn("<b>2026-10-08</b><span>最近上架</span>", self.html)
        self.assertIn(dishlib.SITE_URL, self.html)
        self.assertIn(f"{dishlib.REPO_URL}/blob/main/dishes/", self.html)

    def test_page_is_self_contained(self):
        self.assertIn("<style>", self.html)
        self.assertIn('rel="icon" href="data:image/svg+xml,', self.html)
        self.assertNotIn("cdn.", self.html)
        self.assertNotIn("<script", self.html.lower())

    def test_empty_repo_renders_placeholder(self):
        self.html = sitegen.render_site_html([])
        self.assertIn("<b>—</b><span>最近上架</span>", self.html)


if __name__ == "__main__":
    unittest.main()
