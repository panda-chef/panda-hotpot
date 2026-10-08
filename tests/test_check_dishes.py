"""check_dishes 的菜单校验兼容性测试。

重点：公众号发布流水线（sync_to_hotpot.py）写入的**绝对 URL、插在表头下方、
不维护计数行**的菜单，必须被判为通过——否则日更一发文 CI 就红。
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts import check_dishes, dishlib  # noqa: E402

SLUG_A = "2026-10-08-新菜"
SLUG_B = "2026-09-01-旧菜"


def absolute_row(slug: str, date: str = "2026-10-08") -> str:
    """发布流水线的写法：绝对 URL。"""
    return (
        f"| [🍲 {slug}](https://github.com/panda-chef/panda-hotpot/blob/main/"
        f"dishes/{slug}/README.md) | {date} | ✅ 已发布 | 🔥 |"
    )


def relative_row(slug: str, date: str = "2026-10-08") -> str:
    """build_menu.py 的写法：相对链接。"""
    return f"| [🍲 {slug}](dishes/{slug}/README.md) | {date} | ✅ 已发布 | 🔥 |"


def legacy_row(slug: str, date: str = "2026-10-08") -> str:
    """早期手工写法：./dishes/<slug>/。"""
    return f"| [🍲 {slug}](./dishes/{slug}/) | {date} | ✅ 已发布 | 🔥 |"


def readme(rows: list[str], summary: str | None = None) -> str:
    lines = [
        "# 项目",
        "",
        dishlib.MENU_START,
        "| 菜品 | 上架时间 | 状态 | 热度 |",
        "|------|---------|------|------|",
        *rows,
        dishlib.MENU_END,
        "",
    ]
    if summary:
        lines.insert(5 + len(rows), summary)
    return "\n".join(lines) + "\n"


def make_dish(slug: str, date: str = "2026-10-08") -> dishlib.Dish:
    return dishlib.dish_from_text(slug, f"# {slug}\n\n> 发布：{date} · 状态：✅ 已发布\n")


def errors_of(findings: list[check_dishes.Finding]) -> list[check_dishes.Finding]:
    return [f for f in findings if f.level == check_dishes.ERROR]


class MenuCompatibilityTests(unittest.TestCase):
    def setUp(self):
        self.dishes = [make_dish(SLUG_A, "2026-10-08"), make_dish(SLUG_B, "2026-09-01")]

    def test_pipeline_absolute_rows_pass(self):
        text = readme([absolute_row(SLUG_A, "2026-10-08"), absolute_row(SLUG_B, "2026-09-01")])
        findings = check_dishes.check_menu(self.dishes, text)
        self.assertEqual(errors_of(findings), [])

    def test_relative_rows_pass(self):
        text = readme([relative_row(SLUG_A, "2026-10-08"), relative_row(SLUG_B, "2026-09-01")])
        self.assertEqual(errors_of(check_dishes.check_menu(self.dishes, text)), [])

    def test_legacy_rows_pass(self):
        text = readme([legacy_row(SLUG_A), legacy_row(SLUG_B, "2026-09-01")])
        self.assertEqual(errors_of(check_dishes.check_menu(self.dishes, text)), [])

    def test_mixed_link_styles_warn_but_pass(self):
        text = readme([absolute_row(SLUG_A), relative_row(SLUG_B, "2026-09-01")])
        findings = check_dishes.check_menu(self.dishes, text)
        self.assertEqual(errors_of(findings), [])
        self.assertTrue(any("混用" in f.message for f in findings))

    def test_missing_dish_is_error(self):
        text = readme([absolute_row(SLUG_A)])
        findings = check_dishes.check_menu(self.dishes, text)
        slugs = {f.slug for f in errors_of(findings)}
        self.assertEqual(slugs, {SLUG_B})

    def test_stale_row_is_error(self):
        text = readme([absolute_row(SLUG_A), relative_row(SLUG_B, "2026-09-01"), relative_row("2020-01-01-已删菜")])
        findings = check_dishes.check_menu(self.dishes, text)
        self.assertTrue(any("不存在" in f.message for f in errors_of(findings)))

    def test_duplicate_row_is_error(self):
        text = readme([relative_row(SLUG_A), relative_row(SLUG_A), relative_row(SLUG_B, "2026-09-01")])
        findings = check_dishes.check_menu(self.dishes, text)
        self.assertTrue(any("重复" in f.message for f in errors_of(findings)))

    def test_summary_mismatch_is_warning_only(self):
        text = readme([relative_row(SLUG_A), relative_row(SLUG_B, "2026-09-01")], summary="> 🍳 共 **1** 道菜，持续上架中…")
        findings = check_dishes.check_menu(self.dishes, text)
        self.assertEqual(errors_of(findings), [])
        self.assertTrue(any("道菜" in f.message for f in findings))

    def test_out_of_order_is_warning_only(self):
        text = readme([relative_row(SLUG_B, "2026-09-01"), relative_row(SLUG_A, "2026-10-08")])
        findings = check_dishes.check_menu(self.dishes, text)
        self.assertEqual(errors_of(findings), [])
        self.assertTrue(any("倒序" in f.message for f in findings))

    def test_missing_markers_is_error(self):
        findings = check_dishes.check_menu(self.dishes, "# 没有标记\n")
        self.assertEqual(len(errors_of(findings)), 1)

    def test_strict_mode_rejects_pipeline_style(self):
        text = readme([absolute_row(SLUG_A), absolute_row(SLUG_B, "2026-09-01")])
        findings = check_dishes.check_menu_strict(self.dishes, text)
        self.assertTrue(errors_of(findings))


class RealRepoIntegrationTests(unittest.TestCase):
    """真实仓库必须通过——这条就是 CI 跑的那条。"""

    def test_real_repo_passes_check(self):
        dishes = dishlib.load_dishes()
        self.assertGreater(len(dishes), 0)
        findings = check_dishes.check_menu(dishes, dishlib.read_text(dishlib.README))
        self.assertEqual(errors_of(findings), [])

    def test_main_exits_zero(self):
        self.assertEqual(check_dishes.main(["--quiet"]), 0)


if __name__ == "__main__":
    unittest.main()
