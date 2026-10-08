"""菜品元信息解析与模型测试。"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts import dishlib  # noqa: E402

FULL_META = """# 🍲 测试菜品

> 菜品编号：2026-10-08-测试菜品
> 📢 公众号：硅基饲料 · 🗓️ 发布：2026-10-08 · 状态：✅ 已发布
> **热度**：🔥🔥（因为值得）
"""

BOLD_STATUS = """# 🔌 只有加粗元信息

> **菜品编号**：`2026-08-mcp-agent-standard`
> **热度**：🔥🔥🔥
> **状态**：📝 制作中
"""

BARE = "没有标题也没有元信息\n"


class ParseMetaTests(unittest.TestCase):
    def test_full_meta_block(self):
        dish = dishlib.dish_from_text("2026-10-08-测试菜品", FULL_META)
        self.assertEqual(dish.title, "🍲 测试菜品")
        self.assertEqual(dish.date, "2026-10-08")
        self.assertEqual(dish.status, "✅ 已发布")
        self.assertEqual(dish.heat, "🔥🔥")
        self.assertEqual(dish.heat_level, 2)
        self.assertTrue(dish.is_published)

    def test_bold_labels_and_wip_status(self):
        dish = dishlib.dish_from_text("2026-08-mcp-agent-standard", BOLD_STATUS)
        self.assertEqual(dish.status, "📝 制作中")
        self.assertFalse(dish.is_published)
        self.assertEqual(dish.heat_level, 3)

    def test_heat_level_is_clamped(self):
        dish = dishlib.dish_from_text("2026-01-01-x", "# t\n> 热度：🔥🔥🔥🔥🔥\n")
        self.assertEqual(dish.heat_level, 3)


    def test_backticked_dish_id_is_parsed(self):
        text = (
            "# 🔌 MCP\n\n"
            "> **菜品编号**：`2026-08-mcp-agent-standard`\n"
            "> **状态**：📝 制作中\n"
        )
        dish = dishlib.dish_from_text("2026-08-mcp-agent-standard", text)
        self.assertEqual(dish.date, "2026-08")
        self.assertFalse(dish.is_published)

    def test_meta_falls_back_to_slug_and_defaults(self):
        dish = dishlib.dish_from_text("2026-09-01-裸目录", BARE)
        self.assertEqual(dish.title, "2026-09-01-裸目录")
        self.assertEqual(dish.date, "2026-09-01")
        self.assertEqual(dish.status, dishlib.DEFAULT_STATUS)
        self.assertEqual(dish.heat, dishlib.DEFAULT_HEAT)

    def test_slug_without_date(self):
        dish = dishlib.dish_from_text("没有日期", BARE)
        self.assertEqual(dish.date, "0000-00")
        self.assertFalse(dish.is_published is None)

    def test_url_is_percent_encoded(self):
        dish = dishlib.dish_from_text("2026-10-08-中文 目录", FULL_META)
        self.assertTrue(dish.url.startswith("dishes/2026-10-08-%E4%B8%AD%E6%96%87"))
        self.assertTrue(dish.repo_blob_url.endswith(dish.url))
        self.assertNotIn(" ", dish.url)

    def test_relative_links_skips_external(self):
        text = (
            "[外链](https://example.com) [锚点](#x) "
            "[相对](./code/README.md) [跨目录](../a/b.md)"
        )
        self.assertEqual(dishlib.relative_links(text), ["./code/README.md", "../a/b.md"])

    def test_resolve_link_strips_query_and_anchor(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "code").mkdir()
            (base / "code" / "README.md").write_text("x", encoding="utf-8")
            self.assertTrue(
                dishlib.resolve_link(base, "./code/README.md?v=2#top").is_file()
            )


class LoadDishesTests(unittest.TestCase):
    def build_repo(self, tmp: str) -> Path:
        dishes_dir = Path(tmp) / "dishes"
        for slug, date in [
            ("2026-08-01-旧菜", "2026-08-01"),
            ("2026-10-01-新菜", "2026-10-01"),
            ("2026-09-01-中间菜", "2026-09-01"),
        ]:
            directory = dishes_dir / slug
            directory.mkdir(parents=True)
            (directory / "README.md").write_text(
                f"# {slug}\n\n> 发布：{date} · 状态：✅ 已发布\n", encoding="utf-8"
            )
        (dishes_dir / "没有README的目录").mkdir()
        return dishes_dir

    def test_load_dishes_sorted_desc_and_skips_incomplete(self):
        with tempfile.TemporaryDirectory() as tmp:
            dishes_dir = self.build_repo(tmp)
            dishes = dishlib.load_dishes(dishes_dir)
            self.assertEqual([d.slug for d in dishes], [
                "2026-10-01-新菜",
                "2026-09-01-中间菜",
                "2026-08-01-旧菜",
            ])
            self.assertEqual(len(dishlib.iter_dish_dirs(dishes_dir)), 3)

    def test_load_dishes_missing_dir_returns_empty(self):
        self.assertEqual(dishlib.load_dishes(Path("不存在的目录")), [])


class MenuRowParsingTests(unittest.TestCase):
    BLOCK = """
| 菜品 | 上架时间 | 状态 | 热度 |
|------|---------|------|------|
| [🍲 新菜](dishes/2026-10-08-新菜/README.md) | 2026-10-08 | ✅ 已发布 | 🔥🔥 |
| [🍲 旧菜](./dishes/2026-08-旧菜/) | 2026-08 | 📝 制作中 | 🔥 |

> 🍳 共 **2** 道菜，持续上架中…
"""

    def test_parse_rows_skips_header_and_separator(self):
        rows = dishlib.parse_menu_rows(self.BLOCK)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["title"], "🍲 新菜")
        self.assertEqual(rows[0]["date"], "2026-10-08")
        self.assertEqual(rows[0]["heat"], "🔥🔥")
        self.assertEqual(rows[1]["status"], "📝 制作中")

    def test_summary_count(self):
        self.assertEqual(dishlib.menu_summary_count(self.BLOCK), 2)
        self.assertIsNone(dishlib.menu_summary_count("没有计数行"))

    def test_slug_from_target_all_styles(self):
        self.assertEqual(
            dishlib.slug_from_target("dishes/2026-10-08-%E6%96%B0%E8%8F%9C/README.md"),
            "2026-10-08-新菜",
        )
        self.assertEqual(dishlib.slug_from_target("./dishes/2026-08-旧菜/"), "2026-08-旧菜")
        self.assertEqual(
            dishlib.slug_from_target(
                "https://github.com/panda-chef/panda-hotpot/blob/main/dishes/2026-10-08-新菜/README.md"
            ),
            "2026-10-08-新菜",
        )
        self.assertIsNone(dishlib.slug_from_target("https://example.com/x.md"))

    def test_menu_block_returns_none_without_markers(self):
        self.assertIsNone(dishlib.menu_block("# 没有标记"))
        self.assertIsNotNone(dishlib.menu_block(f"{dishlib.MENU_START}\nx\n{dishlib.MENU_END}"))


class ParseSlugTests(unittest.TestCase):
    def test_full_date_and_short_date(self):
        self.assertEqual(dishlib.parse_slug("2026-10-08-主题"), ("2026-10-08", "主题"))
        self.assertEqual(dishlib.parse_slug("2026-08-主题"), ("2026-08", "主题"))
        self.assertEqual(dishlib.parse_slug("随便"), ("0000-00", "随便"))


if __name__ == "__main__":
    unittest.main()
