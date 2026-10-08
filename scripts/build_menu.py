#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""扫描 dishes/ 目录，生成 README 的主菜单区块与静态站点首页。

用法::

    python scripts/build_menu.py                          # 更新 README 菜单
    python scripts/build_menu.py --check                  # 只校验（有漂移则退出码 1）
    python scripts/build_menu.py --site docs/index.html   # 同时生成站点首页

每道「菜」是一个 dishes/<目录>/README.md，脚本从它的元信息块读取标题、日期、
状态与热度；缺失时回退到目录名和默认值。
"""
from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
DISHES_DIR = ROOT / "dishes"
README = ROOT / "README.md"

MENU_START = "<!-- MENU:START -->"
MENU_END = "<!-- MENU:END -->"

DEFAULT_STATUS = "✅ 已发布"
DEFAULT_HEAT = "🔥"
REPO_URL = "https://github.com/panda-chef/panda-hotpot"
SITE_URL = "https://panda-chef.github.io/panda-hotpot/"

TAGLINE = "每道菜 = 一个 AI 热点：科普文章 + 可运行代码 + 资料清单"

# 中国红圆底 + 米色熊猫脸（内联 SVG，避免额外图标文件）
FAVICON = (
    "data:image/svg+xml,"
    "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E"
    "%3Ccircle cx='16' cy='16' r='16' fill='%23d7263d'/%3E"
    "%3Ccircle cx='10.5' cy='10' r='3.4' fill='%230d1117'/%3E"
    "%3Ccircle cx='21.5' cy='10' r='3.4' fill='%230d1117'/%3E"
    "%3Ccircle cx='16' cy='19' r='8' fill='%23f5e6c8'/%3E"
    "%3Ccircle cx='13' cy='18' r='1.7' fill='%23241a17'/%3E"
    "%3Ccircle cx='19' cy='18' r='1.7' fill='%23241a17'/%3E"
    "%3C/svg%3E"
)


class Dish:
    __slots__ = ("slug", "title", "date", "status", "heat", "path")

    def __init__(self, slug: str, title: str, date: str, status: str, heat: str, path: Path):
        self.slug = slug
        self.title = title
        self.date = date
        self.status = status
        self.heat = heat
        self.path = path

    @property
    def url(self) -> str:
        rel = f"dishes/{self.slug}/README.md"
        return quote(rel, safe="/")

    @property
    def heat_level(self) -> int:
        return max(1, self.heat.count("🔥"))

    @property
    def sort_key(self) -> tuple:
        return (self.date, self.slug)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="replace")


def first_heading(text: str) -> str | None:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return None


def find_meta(text: str, label: str, pattern: str) -> str | None:
    """在元信息块里找 `标签：值`，兼容 `> **标签**：值` 和 `· 标签：值`。"""
    m = re.search(rf"{label}\s*\**\s*[：:]\s*({pattern})", text)
    return m.group(1).strip(" ·|*\t") if m else None


def load_dish(directory: Path) -> Dish:
    readme = directory / "README.md"
    text = read_text(readme)
    slug = directory.name

    title = first_heading(text) or slug
    date = find_meta(text, "发布", r"\d{4}-\d{2}-\d{2}") or find_meta(
        text, "菜品编号", r"\d{4}-\d{2}(?:-\d{2})?"
    )
    if not date:
        m = re.match(r"(\d{4}-\d{2}(?:-\d{2})?)", slug)
        date = m.group(1) if m else "0000-00"
    status = find_meta(text, "状态", r"[^·|\n]+") or DEFAULT_STATUS
    heat = find_meta(text, "热度", r"[^（(·|\n]+") or DEFAULT_HEAT
    return Dish(slug, title, date, status, heat, readme)


def load_dishes() -> list[Dish]:
    if not DISHES_DIR.is_dir():
        return []
    dishes = [
        load_dish(d)
        for d in sorted(DISHES_DIR.iterdir())
        if d.is_dir() and (d / "README.md").is_file()
    ]
    dishes.sort(key=lambda d: d.sort_key, reverse=True)
    return dishes


def render_rows(dishes: list[Dish]) -> str:
    lines = ["| 菜品 | 上架时间 | 状态 | 热度 |", "|------|---------|------|------|"]
    for d in dishes:
        title = d.title.replace("|", "\\|")
        lines.append(f"| [{title}]({d.url}) | {d.date} | {d.status} | {d.heat} |")
    lines.append("")
    lines.append(f"> 🍳 共 **{len(dishes)}** 道菜，持续上架中…")
    return "\n".join(lines)


def render_readme(dishes: list[Dish], original: str) -> str:
    block = f"{MENU_START}\n{render_rows(dishes)}\n{MENU_END}"
    if MENU_START in original and MENU_END in original:
        pattern = re.compile(
            re.escape(MENU_START) + r".*?" + re.escape(MENU_END), re.S
        )
        return pattern.sub(lambda _: block, original, count=1)
    raise SystemExit(f"README 缺少 {MENU_START} / {MENU_END} 标记，请先补上。")


def render_site(dishes: list[Dish]) -> str:
    total = len(dishes)
    latest = dishes[0].date if dishes else "—"
    items = []
    for d in dishes:
        dots = "".join(
            f'<i class="{"on" if i < d.heat_level else ""}"></i>' for i in range(3)
        )
        done = "已发布" in d.status
        items.append(
            f"""      <li class="dish">
        <div class="meta"><span class="date">{html.escape(d.date)}</span>"""
            f"""<span class="badge {'ok' if done else 'wip'}">{'已发布' if done else '制作中'}</span>"""
            f"""<span class="heat" title="热度">{dots}</span></div>
        <a class="title" href="{REPO_URL}/blob/main/{d.url}">{html.escape(d.title)}</a>
      </li>"""
        )
    listing = "\n".join(items)
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>熊猫厨子的 AI 火锅店 · Panda Hotpot</title>
<meta name="description" content="{html.escape(TAGLINE)}">
<meta property="og:type" content="website">
<meta property="og:title" content="熊猫厨子的 AI 火锅店 · Panda Hotpot">
<meta property="og:description" content="{html.escape(TAGLINE)}">
<meta property="og:url" content="{SITE_URL}">
<meta name="theme-color" content="#0d1117">
<link rel="icon" href="{FAVICON}">
<style>
  :root {{
    --bg: #0d1117; --panel: #161b22; --line: #30363d;
    --fg: #e6edf3; --fg-dim: #8b949e; --red: #d7263d; --green: #2ea043;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; background: var(--bg); color: var(--fg);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Microsoft YaHei",
                 "PingFang SC", "Hiragino Sans GB", sans-serif;
    line-height: 1.65; -webkit-font-smoothing: antialiased;
  }}
  .wrap {{ max-width: 860px; margin: 0 auto; padding: 64px 24px 80px; }}
  header {{ border-bottom: 1px solid var(--line); padding-bottom: 28px; margin-bottom: 8px; }}
  .eyebrow {{ color: var(--red); font-size: 13px; letter-spacing: .14em; text-transform: uppercase; margin: 0 0 14px; }}
  h1 {{ font-size: 34px; line-height: 1.25; margin: 0 0 10px; letter-spacing: -.01em; }}
  h1 small {{ display: block; font-size: 15px; font-weight: 400; color: var(--fg-dim); letter-spacing: .02em; margin-top: 6px; }}
  .tagline {{ color: var(--fg-dim); margin: 0; font-size: 15px; }}
  .stats {{ display: flex; flex-wrap: wrap; gap: 32px; margin: 26px 0 8px; }}
  .stat b {{ display: block; font-size: 22px; font-weight: 600; }}
  .stat span {{ color: var(--fg-dim); font-size: 13px; }}
  h2 {{ font-size: 15px; letter-spacing: .08em; text-transform: uppercase; color: var(--fg-dim);
        margin: 40px 0 4px; font-weight: 600; }}
  ul.dishes {{ list-style: none; margin: 0; padding: 0; }}
  li.dish {{ border-bottom: 1px solid var(--line); padding: 16px 0; }}
  .meta {{ display: flex; align-items: center; gap: 10px; font-size: 12px; color: var(--fg-dim); margin-bottom: 6px; }}
  .badge {{ border: 1px solid var(--line); border-radius: 999px; padding: 1px 9px; }}
  .badge.ok {{ color: var(--green); border-color: rgba(46,160,67,.4); }}
  .badge.wip {{ color: #d29922; border-color: rgba(210,153,34,.4); }}
  .heat {{ display: inline-flex; gap: 3px; align-items: center; margin-left: auto; }}
  .heat i {{ width: 6px; height: 6px; border-radius: 50%; background: var(--line); display: inline-block; }}
  .heat i.on {{ background: var(--red); }}
  a.title {{ color: var(--fg); text-decoration: none; font-size: 16px; }}
  a.title:hover {{ color: var(--red); }}
  footer {{ margin-top: 44px; padding-top: 22px; border-top: 1px solid var(--line);
            color: var(--fg-dim); font-size: 13px; display: flex; flex-wrap: wrap; gap: 18px; }}
  footer a {{ color: var(--fg-dim); }}
  footer a:hover {{ color: var(--fg); }}
</style>
</head>
<body>
  <div class="wrap">
    <header>
      <p class="eyebrow">Panda Hotpot</p>
      <h1>熊猫厨子的 AI 火锅店<small>Panda Chef · open-source kitchen</small></h1>
      <p class="tagline">{html.escape(TAGLINE)}</p>
      <div class="stats">
        <div class="stat"><b>{total}</b><span>道菜（菜品目录）</span></div>
        <div class="stat"><b>{html.escape(latest)}</b><span>最近上架</span></div>
        <div class="stat"><b>MIT</b><span>开源协议</span></div>
      </div>
    </header>

    <h2>菜单 · Dishes</h2>
    <ul class="dishes">
{listing}
    </ul>

    <footer>
      <a href="{REPO_URL}">GitHub 仓库</a>
      <a href="{REPO_URL}/blob/main/CONTRIBUTING.md">参与贡献</a>
      <a href="{REPO_URL}/blob/main/LICENSE">MIT License</a>
      <span>公众号：硅基饲料（AI_Feed）</span>
    </footer>
  </div>
</body>
</html>
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="生成 README 主菜单与站点首页")
    parser.add_argument("--check", action="store_true", help="只校验，不写入文件")
    parser.add_argument("--site", metavar="PATH", help="同时生成静态站点首页")
    args = parser.parse_args(argv)

    dishes = load_dishes()
    if not dishes:
        print("dishes/ 下没有找到任何菜品目录", file=sys.stderr)
        return 1

    original = read_text(README)
    updated = render_readme(dishes, original)
    drift = updated != original

    published = sum(1 for d in dishes if "已发布" in d.status)
    print(f"菜品总数: {len(dishes)}（已发布 {published} / 制作中 {len(dishes) - published}）")
    print(f"最近上架: {dishes[0].date} · {dishes[0].title}")
    print(f"README 菜单: {'有漂移，需要更新' if drift else '已是最新'}")

    if args.check:
        if drift:
            print("提示：运行 python scripts/build_menu.py 更新菜单", file=sys.stderr)
            return 1
        return 0

    if drift:
        README.write_text(updated, encoding="utf-8", newline="\n")
        print(f"已更新 {README.relative_to(ROOT)}")

    if args.site:
        site = ROOT / args.site
        site.parent.mkdir(parents=True, exist_ok=True)
        site.write_text(render_site(dishes), encoding="utf-8", newline="\n")
        print(f"已生成 {site.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
