#!/usr/bin/env python3
"""把个人知识库 40.知识沉淀 的笔记迁移成 AstroPaper 文章。

用法:
    python3 scripts/migrate-vault-notes.py --dry-run          # 输出到 .staging-migration/，不碰 posts/
    python3 scripts/migrate-vault-notes.py --apply            # 真正写入 src/content/posts/

设计原则:
  * 幂等: 重跑覆盖同 slug 产物; 图片下载有本地缓存, 不重复抓取。
  * 不改写技术正文; 只做格式转换 + 插入清单里写好的引言。
  * 坏图(Windows 绝对路径 / 缺失相对路径)删除并在报告里逐条列出, 不静默吞掉。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import time
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
MANIFEST = REPO / "scripts" / "migration-manifest.json"
POSTS_DIR = REPO / "src" / "content" / "posts"
STAGING = REPO / ".staging-migration"
IMG_CACHE = Path("/tmp/vault-migration-imgcache")

IMG_MD = re.compile(r"!\[(?P<alt>[^\]]*)\]\((?P<url>[^)\s]+)(?:\s+\"[^\"]*\")?\)")
IMG_HTML = re.compile(r"<img\b[^>]*>", re.I)
ATTR_SRC = re.compile(r'src="([^"]+)"', re.I)
ATTR_ALT = re.compile(r'alt="([^"]*)"', re.I)
WIKILINK = re.compile(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]")
FM = re.compile(r"\A---\n.*?\n---\n", re.S)
BAD_URL = re.compile(r"^(?:[A-Za-z]:[\\/]|\.\.|[A-Za-z]:\\)")


def slugify_asset(url: str, used: dict[str, int]) -> str:
    name = os.path.basename(url.split("?")[0])
    name = re.sub(r"[^0-9A-Za-z._\-\u4e00-\u9fff]", "-", name) or "image.png"
    if "." not in name:
        name += ".png"
    if name in used:
        used[name] += 1
        stem, ext = os.path.splitext(name)
        return f"{stem}-{used[name]}{ext}"
    used[name] = 0
    return name


def fetch(url: str, dest: Path) -> tuple[bool, str]:
    """下载到本地缓存再复制, 返回 (ok, note)."""
    IMG_CACHE.mkdir(parents=True, exist_ok=True)
    cache = IMG_CACHE / hashlib.sha1(url.encode()).hexdigest()
    if not cache.exists():
        for attempt in range(3):
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "hermes-migrator/1.0"})
                with urllib.request.urlopen(req, timeout=30) as resp:
                    data = resp.read()
                if len(data) < 128:
                    raise ValueError(f"payload too small ({len(data)}B)")
                cache.write_bytes(data)
                break
            except Exception as exc:  # noqa: BLE001
                if attempt == 2:
                    return False, f"下载失败: {exc}"
                time.sleep(2 * (attempt + 1))
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(cache, dest)
    return True, f"{cache.stat().st_size // 1024}KB"


def convert(md: str, entry: dict, report: dict, apply_mode: bool) -> str:
    slug = entry["slug"]
    src_dir = Path(entry["_src_dir"])
    text = md
    m = FM.match(text)
    if m:
        report["stripped_frontmatter"] = m.group(0).strip().splitlines()[1:]
        text = text[m.end():]

    # 1. 正文开头的 H1 与 title 重复 -> 去掉(标题由 frontmatter 渲染)
    text = text.lstrip("\n")
    head = re.match(r"#\s+(.+?)\n", text)
    if head:
        report["dropped_h1"] = head.group(1).strip()
        text = text[head.end():].lstrip("\n")

    # 2. 图片: 下载可用的, 删掉坏图
    used: dict[str, int] = {}
    images_dir = (POSTS_DIR if apply_mode else STAGING) / slug / "images"
    asset_pools = [Path(p) for p in entry.get("_asset_pools", [])]

    def recover_local(url: str, report: dict) -> str | None:
        """本地/相对路径图片: ① 相对源文件能否落地 ② 资产池里按文件名找回。"""
        clean = url.replace("\\", "/")
        if not clean.startswith("..") and not re.match(r"^[A-Za-z]:", clean):
            cand = (src_dir / clean).resolve()
            if cand.exists():
                return str(cand)
        want = clean.split("/")[-1]
        for pool in asset_pools:
            if not pool.is_dir():
                continue
            for f in sorted(pool.iterdir()):
                if not f.is_file():
                    continue
                orig = f.name.split("-", 1)[1] if "-" in f.name else f.name
                if orig == want or f.name == want or want.endswith(orig) or orig.endswith(want):
                    return str(f)
        return None

    def replace_image(url: str, alt: str) -> str:
        if url.startswith(("http://", "https://")):
            name = slugify_asset(url, used)
            ok, note = fetch(url, images_dir / name)
            if not ok:
                report["images_failed"].append(f"{alt or name} <- {url} ({note})")
                return ""
            report["images_downloaded"].append(f"{name} ({note})")
            return f"![{alt}](./{slug}/images/{name})"
        found = recover_local(url, report)
        if found:
            name = slugify_asset(Path(found).name, used)
            dest = images_dir / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(found, dest)
            report["images_recovered"].append(f"{name} <- {url}")
            return f"![{alt}](./{slug}/images/{name})"
        report["images_dropped"].append(f"{alt or '(no alt)'} <- {url}")
        return ""

    text = IMG_MD.sub(lambda m: replace_image(m.group("url"), m.group("alt")), text)

    def html_image(match: re.Match) -> str:
        tag = match.group(0)
        src = ATTR_SRC.search(tag)
        if not src:
            report["images_dropped"].append(f"(html img 无 src) <- {tag[:80]}")
            return ""
        alt = ATTR_ALT.search(tag)
        return replace_image(src.group(1), alt.group(1) if alt else "")

    text = IMG_HTML.sub(html_image, text)

    # 3. wikilink -> 纯文本
    def link(match: re.Match) -> str:
        report["wikilinks"].append(match.group(0))
        return match.group(2) or match.group(1)

    text = WIKILINK.sub(link, text)

    # 4. 删掉清单指定的个人向小节(从该标题到处文件末尾或下一个同级标题)
    for title in entry.get("drop_sections", []):
        pattern = re.compile(rf"^#{{1,4}}\s*{re.escape(title)}\s*$.*?(?=^#{{1,4}}\s|\Z)", re.S | re.M)
        if pattern.search(text):
            text = pattern.sub("", text)
            report["dropped_sections"].append(title)

    text = re.sub(r"\n{3,}", "\n\n", text).strip()

    intro = entry.get("intro", "").strip()
    body = f"{intro}\n\n{text}" if intro else text

    head_yaml = [
        f'title: "{entry["title"]}"',
        f'description: "{entry["description"]}"',
        f'pubDatetime: {entry["pubDatetime"]}',
        "featured: false",
        "draft: false",
        "tags:",
    ] + [f"  - {t}" for t in entry["tags"]]

    sep = "---"
    return f"{sep}\n" + "\n".join(head_yaml) + f"\n{sep}\n\n{body}\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="写入 src/content/posts/")
    ap.add_argument("--dry-run", action="store_true", help="写入 .staging-migration/")
    ap.add_argument("--only", nargs="*", help="只处理指定 slug")
    ap.add_argument("--pubdate-fallback", default=None,
                    help="清单里 pubDatetime 为空时用的占位日期（仅用于 dry-run 验证管道）")
    args = ap.parse_args()
    if not (args.apply ^ args.dry_run):
        ap.error("必须且只能指定 --apply 或 --dry-run")

    cfg = json.loads(MANIFEST.read_text(encoding="utf-8"))
    vault = Path(cfg["vault_root"])
    asset_pools = cfg.get("asset_pools", [])
    summary, line_report = [], []

    for entry in cfg["entries"]:
        if not entry.get("enabled", True):
            continue
        if args.only and entry["slug"] not in args.only:
            continue
        src = vault / entry["src"]
        report: dict = {
            "slug": entry["slug"],
            "src": entry["src"],
            "images_downloaded": [],
            "images_recovered": [],
            "images_dropped": [],
            "images_failed": [],
            "wikilinks": [],
            "dropped_sections": [],
        }
        if not src.exists():
            summary.append(f"❌ {entry['slug']}: 源文件缺失 {src}")
            continue
        pubdate = entry.get("pubDatetime") or args.pubdate_fallback
        if not pubdate:
            summary.append(f"⏸  {entry['slug']}: 缺少 pubDatetime，跳过（等老板给日期）")
            line_report.append((entry, report, None, None))
            continue
        entry = {**entry, "pubDatetime": pubdate, "_asset_pools": asset_pools, "_src_dir": str(src.parent)}

        raw = src.read_text(encoding="utf-8")
        out = convert(raw, entry, report, args.apply)
        target = (POSTS_DIR if args.apply else STAGING) / f'{entry["slug"]}.md'
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(out, encoding="utf-8")
        summary.append(
            f"✅ {entry['slug']}: {raw.count(chr(10)) + 1} 行 -> {out.count(chr(10)) + 1} 行 | "
            f"图: 下载 {len(report['images_downloaded'])} / 本地找回 {len(report['images_recovered'])} / "
            f"删除 {len(report['images_dropped'])} / 失败 {len(report['images_failed'])}"
        )
        line_report.append((entry, report, raw, out))

    print("\n".join(summary))
    payload = [
        {"slug": e["slug"], "src": e["src"], **{k: v for k, v in r.items() if k not in ("slug", "src")}}
        for e, r, _raw, _out in line_report
    ]
    out_json = (STAGING if args.dry_run else REPO / "tmp") / "migration-report.json"
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n报告: {out_json}")
    for e, r, _raw, _out in line_report:
        if r["images_dropped"]:
            print(f"  坏图[{e['slug']}]: " + "; ".join(r["images_dropped"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
