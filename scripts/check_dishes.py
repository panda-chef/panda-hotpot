#!/usr/bin/env python3
"""CLI：校验 dishes/ 的结构、元信息与相对链接（CI 使用）。

检查项：

1. 每个子目录都有 `README.md`
2. 目录名符合 `YYYY-MM-DD-短名`（或 `YYYY-MM-短名`），不含空格与括号
3. README 有一级标题
4. 元信息块含日期（`发布`/`菜品编号`）与`状态`
5. README 内指向仓库文件的相对链接都能解析到真实文件
6. README 里提到的 `code/` 目录真实存在且非空
7. 主菜单覆盖每一道菜、没有指向已删目录的行（`--strict-menu` 时额外要求与生成器输出逐字节一致）

退出码：0 表示无错误（允许有警告），1 表示存在错误。
"""
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts import dishlib, sitegen  # noqa: E402

ERROR = "error"
WARNING = "warning"

BAD_CHARS_RE = dishlib.re.compile(r"[\s()（）\[\]【】]")


@dataclass
class Finding:
    level: str
    slug: str
    message: str

    def render(self) -> str:
        icon = "❌" if self.level == ERROR else "⚠️"
        return f"{icon} [{self.slug}] {self.message}"


def check_dish_directory(directory: Path) -> list[Finding]:
    """校验单个菜品目录，返回发现的问题列表。"""
    slug = directory.name
    findings: list[Finding] = []

    if BAD_CHARS_RE.search(slug):
        findings.append(Finding(ERROR, slug, "目录名含空格或括号，请改成短横线连接"))
    if not dishlib.SLUG_RE.match(slug):
        findings.append(Finding(WARNING, slug, "目录名不是 YYYY-MM-DD-短名 格式"))

    readme = directory / "README.md"
    if not readme.is_file():
        findings.append(Finding(ERROR, slug, "缺少 README.md"))
        return findings

    text = dishlib.read_text(readme)
    if not dishlib.first_heading(text):
        findings.append(Finding(ERROR, slug, "README 缺少一级标题（# 标题）"))
    if not dishlib.find_meta(text, "状态"):
        findings.append(Finding(WARNING, slug, "元信息块缺少「状态」"))
    if not (
        dishlib.find_meta(text, "发布", dishlib.DATE_RE.pattern)
        or dishlib.find_meta(text, "菜品编号", dishlib.SHORT_DATE_RE.pattern)
    ):
        findings.append(Finding(WARNING, slug, "元信息块缺少发布日期或菜品编号"))

    for link in dishlib.relative_links(text):
        if not dishlib.resolve_link(directory, link).exists():
            findings.append(Finding(ERROR, slug, f"相对链接指向不存在的文件：{link}"))

    code_dir = directory / "code"
    mentions_code = "code/" in text
    if mentions_code and not code_dir.is_dir():
        findings.append(Finding(ERROR, slug, "README 提到 code/，但目录不存在"))
    elif code_dir.is_dir() and not any(code_dir.iterdir()):
        findings.append(Finding(WARNING, slug, "code/ 目录为空"))

    return findings


def check_menu(dishes: list[dishlib.Dish], readme_text: str) -> list[Finding]:
    """校验主菜单覆盖了每一道菜，且没指向不存在的目录。

    这里刻意**不使用**「与生成器输出逐字节相同」的标准：公众号发布流水线
    （``sync_to_hotpot.py``）会自己往表头下插行、使用绝对 URL、也不维护
    「共 N 道菜」计数行。只要覆盖完整、没有失效行就放行，链接风格差异只提示。
    """
    block = dishlib.menu_block(readme_text)
    if block is None:
        return [
            Finding(ERROR, "README", f"缺少 {dishlib.MENU_START} / {dishlib.MENU_END} 标记")
        ]

    rows = dishlib.parse_menu_rows(block)
    findings: list[Finding] = []
    seen: dict[str, int] = {}
    for row in rows:
        slug = dishlib.slug_from_target(row["target"])
        if slug is None:
            findings.append(
                Finding(WARNING, "README", f"菜单行解析不出菜品目录：{row['title']}")
            )
            continue
        seen[slug] = seen.get(slug, 0) + 1

    existing = {dish.slug for dish in dishes}
    for slug, count in seen.items():
        if slug not in existing:
            findings.append(Finding(ERROR, slug, f"菜单里有 {count} 行指向不存在的菜品目录"))
        elif count > 1:
            findings.append(Finding(ERROR, slug, f"菜单里有 {count} 行重复"))
    for dish in dishes:
        if dish.slug not in seen:
            findings.append(Finding(ERROR, dish.slug, "菜单里缺少这道菜"))

    summary = dishlib.menu_summary_count(block)
    if summary is not None and summary != len(dishes):
        findings.append(
            Finding(WARNING, "README", f"「共 N 道菜」写的是 {summary}，实际 {len(dishes)} 道")
        )
    dates = [row["date"] for row in rows]
    if dates != sorted(dates, reverse=True):
        findings.append(Finding(WARNING, "README", "菜单行不是按日期倒序（build_menu.py 会重排）"))
    styles = {"absolute" if row["target"].startswith("http") else "relative" for row in rows}
    if len(styles) > 1:
        findings.append(
            Finding(WARNING, "README", "菜单混用绝对链接与相对链接（build_menu.py 会统一为相对）")
        )
    return findings


def check_menu_strict(dishes: list[dishlib.Dish], readme_text: str) -> list[Finding]:
    """额外要求菜单与生成器输出完全一致（本地手工维护菜单时用，见 --strict-menu）。"""
    try:
        expected = sitegen.apply_menu(dishes, readme_text)
    except SystemExit as exc:
        return [Finding(ERROR, "README", str(exc))]
    if expected != readme_text:
        return [Finding(ERROR, "README", "主菜单与生成器输出不一致，请运行 build_menu.py 更新")]
    return []


def collect(findings: list[Finding], new: list[Finding]) -> None:
    findings.extend(new)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="校验 dishes/ 结构与链接")
    parser.add_argument("--quiet", action="store_true", help="只输出错误与汇总")
    parser.add_argument(
        "--strict-menu",
        action="store_true",
        help="额外要求菜单与 build_menu.py 的输出逐字节一致（本地手工维护菜单时用）",
    )
    args = parser.parse_args(argv)

    if not dishlib.DISHES_DIR.is_dir():
        print("找不到 dishes/ 目录", file=sys.stderr)
        return 1

    directories = sorted(d for d in dishlib.DISHES_DIR.iterdir() if d.is_dir())
    dishes = [dishlib.load_dish(d) for d in dishlib.iter_dish_dirs()]
    dishes.sort(key=lambda d: d.sort_key, reverse=True)
    readme_text = dishlib.read_text(dishlib.README)

    findings: list[Finding] = []
    for directory in directories:
        collect(findings, check_dish_directory(directory))
    collect(findings, check_menu(dishes, readme_text))
    if args.strict_menu:
        collect(findings, check_menu_strict(dishes, readme_text))

    errors = [f for f in findings if f.level == ERROR]
    warnings = [f for f in findings if f.level == WARNING]

    for finding in findings:
        if args.quiet and finding.level == WARNING:
            continue
        print(finding.render())

    print(
        f"\n菜品目录 {len(directories)} 个 · 错误 {len(errors)} · 警告 {len(warnings)}"
    )
    if errors:
        print("校验未通过", file=sys.stderr)
        return 1
    print("校验通过 ✅")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
