"""渲染层：把菜品列表渲染成 README 主菜单与静态站点首页。

* :func:`render_menu_block` —— 生成 README 里 `<!-- MENU:START -->` 区块的内容
* :func:`apply_menu` —— 把生成的区块写回 README 文本
* :func:`render_site_html` —— 生成 `docs/index.html`（GitHub Pages 首页）
"""
from __future__ import annotations

import html
import re

from scripts.dishlib import (
    DISHES_DIR,
    MENU_END,
    MENU_START,
    REPO_URL,
    SITE_URL,
    TAGLINE,
    Dish,
)

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

__all__ = [
    "FAVICON",
    "apply_menu",
    "render_menu_block",
    "render_menu_rows",
    "render_site_html",
]


def render_menu_rows(dishes: list[Dish]) -> list[str]:
    """渲染菜单表格行（不含表头）。"""
    rows = []
    for dish in dishes:
        title = dish.title.replace("|", "\\|")
        rows.append(f"| [{title}]({dish.url}) | {dish.date} | {dish.status} | {dish.heat} |")
    return rows


def render_menu_block(dishes: list[Dish]) -> str:
    """渲染 README 的两个标记之间的完整区块。"""
    lines = ["| 菜品 | 上架时间 | 状态 | 热度 |", "|------|---------|------|------|"]
    lines.extend(render_menu_rows(dishes))
    lines.append("")
    lines.append(f"> 🍳 共 **{len(dishes)}** 道菜，持续上架中…")
    return f"{MENU_START}\n" + "\n".join(lines) + f"\n{MENU_END}"


def apply_menu(dishes: list[Dish], original: str) -> str:
    """把菜单区块替换进 README 原文；缺少标记时抛出 :class:`SystemExit`。"""
    if MENU_START not in original or MENU_END not in original:
        raise SystemExit(f"README 缺少 {MENU_START} / {MENU_END} 标记，请先补上。")
    pattern = re.compile(re.escape(MENU_START) + r".*?" + re.escape(MENU_END), re.S)
    block = render_menu_block(dishes)
    return pattern.sub(lambda _: block, original, count=1)


def render_site_html(dishes: list[Dish]) -> str:
    """渲染整页静态首页（自包含：内联 CSS 与 favicon，无外部依赖）。"""
    total = len(dishes)
    latest = dishes[0].date if dishes else "—"
    items = []
    for dish in dishes:
        dots = "".join(
            f'<i class="{"on" if i < dish.heat_level else ""}"></i>' for i in range(3)
        )
        label = "已发布" if dish.is_published else "制作中"
        items.append(
            f"""      <li class="dish">
        <div class="meta"><span class="date">{html.escape(dish.date)}</span>"""
            f"""<span class="badge {'ok' if dish.is_published else 'wip'}">{label}</span>"""
            f"""<span class="heat" title="热度">{dots}</span></div>
        <a class="title" href="{dish.repo_blob_url}">{html.escape(dish.title)}</a>
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
