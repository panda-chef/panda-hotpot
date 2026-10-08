#!/usr/bin/env python3
"""CLI：新建一道菜的脚手架，顺手把主菜单更新掉。

用法::

    python scripts/new_dish.py --title "某某热点" --with-code
    python scripts/new_dish.py --title "某某热点" --date 2026-10-09 --heat 🔥🔥 --update-menu

生成内容::

    dishes/YYYY-MM-DD-短名/
    ├── README.md          # 带元信息块的模板
    ├── code/README.md     # --with-code 时
    └── materials/links.md # --with-materials 时
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts import dishlib  # noqa: E402

PUNCT_RE = re.compile(r"[（）()【】\[\]「」《》<>:：，,。.！!？?、/\\|'\"]+")
DASH_RE = re.compile(r"-{2,}")
MAX_SLUG_NAME = 40

DISH_README = """# 🍲 {title}

> 菜品编号：{slug}
> 📢 公众号：硅基饲料 · 🗓️ 发布：{date} · 状态：{status}
> **热度**：{heat}（一句话说明为什么热）

## 📝 摘要

（一段话讲清：发生了什么 + 我的判断）

## 🧪 可运行代码

（没有代码就删掉这一节）见 [`code/`](./code/README.md)。

## 📎 相关资料

- [来源标题](https://example.com) —— 一句话说明它为什么值得读
"""

CODE_README = """# 🧪 可运行代码

本目录放这道菜配套的可运行示例：能直接 `python xxx.py` 跑起来的最小版本。

## 运行

```bash
python {entry}
```
"""

MATERIALS_LINKS = """# 📎 资料清单

| 类型 | 链接 | 说明 |
|------|------|------|
| 论文 / 报告 | https://example.com | 一句话说明 |
| 官方公告 | https://example.com | 一句话说明 |
"""


def slugify(text: str) -> str:
    """把标题压成适合做目录名的短名（保留中文，标点转短横线）。"""
    slug = PUNCT_RE.sub("-", text.strip())
    slug = re.sub(r"\s+", "-", slug)
    slug = DASH_RE.sub("-", slug).strip("-")
    return slug[:MAX_SLUG_NAME].strip("-")


def build_slug(date: str, title: str, name: str | None) -> str:
    short = slugify(name or title)
    if not short:
        raise SystemExit("无法从标题生成目录名，请用 --name 指定")
    return f"{date}-{short}"


def write_file(path: Path, content: str, overwrite: bool) -> str:
    if path.exists() and not overwrite:
        return f"跳过（已存在）：{path.name}"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")
    return f"已生成：{path}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="新建一道菜的目录脚手架")
    parser.add_argument("--title", required=True, help="菜品标题（写进 README 一级标题）")
    parser.add_argument(
        "--date", default=dt.date.today().isoformat(), help="发布日期，默认今天"
    )
    parser.add_argument("--name", help="目录短名，默认由标题生成")
    parser.add_argument("--status", default=dishlib.DEFAULT_STATUS, help="状态，默认「✅ 已发布」")
    parser.add_argument("--heat", default=dishlib.DEFAULT_HEAT, help="热度，如 🔥🔥")
    parser.add_argument("--with-code", action="store_true", help="同时建 code/ 目录")
    parser.add_argument("--with-materials", action="store_true", help="同时建 materials/ 目录")
    parser.add_argument("--update-menu", action="store_true", help="生成后顺手更新主菜单")
    parser.add_argument("--overwrite", action="store_true", help="覆盖已存在的文件")
    args = parser.parse_args(argv)

    slug = build_slug(args.date, args.title, args.name)
    directory = dishlib.DISHES_DIR / slug
    if directory.exists() and not args.overwrite:
        print(f"目录已存在：{directory}（加 --overwrite 可覆盖）", file=sys.stderr)
        return 1

    steps = [
        write_file(
            directory / "README.md",
            DISH_README.format(
                title=args.title.strip(),
                slug=slug,
                date=args.date,
                status=args.status,
                heat=args.heat,
            ),
            args.overwrite,
        )
    ]
    if args.with_code:
        steps.append(
            write_file(directory / "code" / "README.md", CODE_README.format(entry="main.py"), args.overwrite)
        )
    if args.with_materials:
        steps.append(
            write_file(directory / "materials" / "links.md", MATERIALS_LINKS, args.overwrite)
        )

    for step in steps:
        print(step)

    if args.update_menu:
        from scripts import sitegen  # 延迟导入，避免未使用时的开销

        dishes = dishlib.load_dishes()
        original = dishlib.read_text(dishlib.README)
        dishlib.README.write_text(
            sitegen.apply_menu(dishes, original), encoding="utf-8", newline="\n"
        )
        print(f"已更新主菜单（当前 {len(dishes)} 道菜）")

    print(f"\n下一步：补内容 → python scripts/build_menu.py --site docs/index.html → 提交")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
