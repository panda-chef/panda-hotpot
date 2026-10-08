#!/usr/bin/env python3
"""CLI：扫描 dishes/ 生成 README 主菜单，并可同步生成静态站点首页。

用法::

    python scripts/build_menu.py                          # 更新 README 菜单
    python scripts/build_menu.py --check                  # 只校验（有漂移退出码 1，供 CI 用）
    python scripts/build_menu.py --site docs/index.html   # 同时生成站点首页

菜品解析在 :mod:`scripts.dishlib`，渲染在 :mod:`scripts.sitegen`，本文件只做编排。
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts import dishlib, sitegen  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="生成 README 主菜单与站点首页")
    parser.add_argument("--check", action="store_true", help="只校验，不写入文件")
    parser.add_argument(
        "--site", metavar="PATH", help="同时生成静态站点首页（如 docs/index.html）"
    )
    args = parser.parse_args(argv)

    dishes = dishlib.load_dishes()
    if not dishes:
        print("dishes/ 下没有找到任何菜品目录", file=sys.stderr)
        return 1

    original = dishlib.read_text(dishlib.README)
    updated = sitegen.apply_menu(dishes, original)
    drift = updated != original

    published = sum(1 for dish in dishes if dish.is_published)
    print(f"菜品总数: {len(dishes)}（已发布 {published} / 制作中 {len(dishes) - published}）")
    print(f"最近上架: {dishes[0].date} · {dishes[0].title}")
    print(f"README 菜单: {'有漂移，需要更新' if drift else '已是最新'}")

    if args.check:
        if drift:
            print("提示：运行 python scripts/build_menu.py 更新菜单", file=sys.stderr)
            return 1
        return 0

    if drift:
        dishlib.README.write_text(updated, encoding="utf-8", newline="\n")
        print(f"已更新 {dishlib.README.relative_to(dishlib.ROOT)}")

    if args.site:
        site = dishlib.ROOT / args.site
        site.parent.mkdir(parents=True, exist_ok=True)
        site.write_text(sitegen.render_site_html(dishes), encoding="utf-8", newline="\n")
        print(f"已生成 {site.relative_to(dishlib.ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
