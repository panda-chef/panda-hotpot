"""菜品数据模型与元信息解析 —— 仓库里所有脚本共用的底层库。

目录约定::

    dishes/<slug>/README.md     菜品说明（头部含元信息块）
    dishes/<slug>/code/         可运行代码（可选）
    dishes/<slug>/materials/    资料清单（可选）

菜品 README 的元信息块形如::

    # 🍲 菜品标题

    > 菜品编号：2026-10-08-GPT-6-免费
    > 📢 公众号：硅基饲料 · 🗓️ 发布：2026-10-08 · 状态：✅ 已发布
    > **热度**：🔥🔥（一句话说明为什么热）

解析对 `> **状态**：x`、`· 状态：x`、`发布日期：x` 等写法都兼容。
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote, unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
DISHES_DIR = ROOT / "dishes"
README = ROOT / "README.md"
DOCS_INDEX = ROOT / "docs" / "index.html"

MENU_START = "<!-- MENU:START -->"
MENU_END = "<!-- MENU:END -->"

REPO_URL = "https://github.com/panda-chef/panda-hotpot"
SITE_URL = "https://panda-chef.github.io/panda-hotpot/"
TAGLINE = "每道菜 = 一个 AI 热点：科普文章 + 可运行代码 + 资料清单"

DEFAULT_STATUS = "✅ 已发布"
DEFAULT_HEAT = "🔥"
PUBLISHED_MARKERS = ("已发布", "已上线", "published", "Published")

# 目录名规范：YYYY-MM-DD-短名 或 YYYY-MM-短名
SLUG_RE = re.compile(r"^(?P<date>\d{4}-\d{2}(?:-\d{2})?)-(?P<name>.+)$")
DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")
SHORT_DATE_RE = re.compile(r"\d{4}-\d{2}(?:-\d{2})?")

_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")


def read_text(path: Path) -> str:
    """按 UTF-8（容忍 BOM）读取文本，读不到时抛出原始异常。"""
    return path.read_text(encoding="utf-8-sig", errors="replace")


def first_heading(text: str) -> str | None:
    """返回第一个 `# ` 一级标题的正文，没有则返回 None。"""
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return None


def find_meta(text: str, label: str, pattern: str | None = None) -> str | None:
    """在元信息块里查找 `标签：值`。

    兼容 `> **状态**：值`（加粗标签）、`· 状态：值`（行内分隔）与
    `菜品编号：`2026-08-xxx``（值被反引号包住）三种写法。
    """
    value = pattern or r"[^·|\n]+"
    match = re.search(rf"{label}\s*\**\s*[：:]\s*[`*\s]*({value})", text)
    if not match:
        return None
    return match.group(1).strip(" ·|*\t`")


def parse_slug(slug: str) -> tuple[str, str]:
    """把目录名拆成 (日期, 短名)；不符合规范时日期回退为 `0000-00`。"""
    match = SLUG_RE.match(slug)
    if not match:
        return "0000-00", slug
    return match.group("date"), match.group("name")


def relative_links(text: str) -> list[str]:
    """取出 Markdown 里指向仓库内文件的相对链接（跳过外链与页内锚点）。"""
    links = []
    for raw in _LINK_RE.findall(text):
        if raw.startswith(("http://", "https://", "mailto:", "#", "//")):
            continue
        links.append(raw)
    return links


def resolve_link(base_dir: Path, link: str) -> Path:
    """把相对链接解析为磁盘路径（去掉 ?query / #fragment 并做 URL 解码）。"""
    path = urlparse(link).path
    return (base_dir / unquote(path)).resolve()


@dataclass(frozen=True)
class Dish:
    """一道菜。"""

    slug: str
    title: str
    date: str
    status: str
    heat: str
    path: Path

    @property
    def url(self) -> str:
        """仓库内相对链接（已百分号编码，GitHub 与静态站点都能解析）。"""
        return quote(f"dishes/{self.slug}/README.md", safe="/")

    @property
    def repo_blob_url(self) -> str:
        return f"{REPO_URL}/blob/main/{self.url}"

    @property
    def heat_level(self) -> int:
        return max(1, min(3, self.heat.count("🔥")))

    @property
    def is_published(self) -> bool:
        return any(marker in self.status for marker in PUBLISHED_MARKERS)

    @property
    def sort_key(self) -> tuple[str, str]:
        return (self.date, self.slug)


def dish_from_text(slug: str, text: str, path: Path | None = None) -> Dish:
    """从菜品 README 文本构造 :class:`Dish`（缺字段时回退到目录名与默认值）。"""
    slug_date, _ = parse_slug(slug)
    title = first_heading(text) or slug
    date = (
        find_meta(text, "发布", DATE_RE.pattern)
        or find_meta(text, "发布日期", DATE_RE.pattern)
        or find_meta(text, "菜品编号", SHORT_DATE_RE.pattern)
        or slug_date
    )
    status = find_meta(text, "状态") or DEFAULT_STATUS
    heat = find_meta(text, "热度", r"[^（(·|\n]+") or DEFAULT_HEAT
    return Dish(
        slug=slug,
        title=title,
        date=date,
        status=status,
        heat=heat,
        path=path or (DISHES_DIR / slug / "README.md"),
    )


def load_dish(directory: Path) -> Dish:
    """读取 `dishes/<slug>/README.md` 构造菜品对象。"""
    readme = directory / "README.md"
    return dish_from_text(directory.name, read_text(readme), readme)


def iter_dish_dirs(directory: Path = DISHES_DIR) -> list[Path]:
    """列出所有菜品目录（含 README.md 的、按目录名排序）。"""
    if not directory.is_dir():
        return []
    return sorted(
        d for d in directory.iterdir() if d.is_dir() and (d / "README.md").is_file()
    )


def load_dishes(directory: Path = DISHES_DIR) -> list[Dish]:
    """加载全部菜品，按日期倒序（同日期按目录名倒序）。"""
    dishes = [load_dish(d) for d in iter_dish_dirs(directory)]
    dishes.sort(key=lambda d: d.sort_key, reverse=True)
    return dishes
