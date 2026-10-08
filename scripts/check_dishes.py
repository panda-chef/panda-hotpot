#!/usr/bin/env python3
"""CLI：校验 dishes/ 的结构、元信息与相对链接（CI 使用）。

检查项：

1. 每个子目录都有 `README.md`
2. 目录名符合 `YYYY-MM-DD-短名`（或 `YYYY-MM-短名`），不含空格与括号
3. README 有一级标题
4. 元信息块含日期（`发布`/`菜品编号`）与`状态`
5. README 内指向仓库文件的相对链接都能解析到真实文件
6. README 里提到的 `code/` 目录真实存在且非空
7. README 主菜单与 dishes/ 内容一致（无漂移）

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


def check_menu(dishes: list[dishlib.Dish]) -> list[Finding]:
    """校验 README 主菜单是否与 dishes/ 同步。"""
    readme_text = dishlib.read_text(dishlib.README)
    try:
        expected = sitegen.apply_menu(dishes, readme_text)
    except SystemExit as exc:  # 缺少 MENU 标记
        return [Finding(ERROR, "README", str(exc))]
    if expected != readme_text:
        return [
            Finding(ERROR, "README", "主菜单与 dishes/ 不一致，请运行 build_menu.py 更新")
        ]
    return []


def collect(findings: list[Finding], new: list[Finding]) -> None:
    findings.extend(new)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="校验 dishes/ 结构与链接")
    parser.add_argument("--quiet", action="store_true", help="只输出错误与汇总")
    args = parser.parse_args(argv)

    if not dishlib.DISHES_DIR.is_dir():
        print("找不到 dishes/ 目录", file=sys.stderr)
        return 1

    directories = sorted(d for d in dishlib.DISHES_DIR.iterdir() if d.is_dir())
    dishes = [dishlib.load_dish(d) for d in dishlib.iter_dish_dirs()]
    dishes.sort(key=lambda d: d.sort_key, reverse=True)

    findings: list[Finding] = []
    for directory in directories:
        collect(findings, check_dish_directory(directory))
    collect(findings, check_menu(dishes))

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
