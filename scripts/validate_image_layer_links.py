from __future__ import annotations

import json
import os
import re
from collections import Counter
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
IMAGE_LAYER_ROOT = REPO_ROOT / "知识库" / "图像解读"
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
LOCAL_SUFFIXES = (".md", ".jpg", ".jpeg", ".png", ".webp")
IGNORED_PREFIXES = ("http://", "https://", "mailto:", "#")


def iter_markdown_files() -> list[Path]:
    return sorted(IMAGE_LAYER_ROOT.rglob("*.md"))


def collect_broken_links() -> list[tuple[Path, str]]:
    broken: list[tuple[Path, str]] = []
    for md_path in iter_markdown_files():
        content = md_path.read_text(encoding="utf-8")
        for match in LINK_RE.finditer(content):
            rel = match.group(1).strip()
            if rel.startswith(IGNORED_PREFIXES):
                continue
            if not rel.lower().endswith(LOCAL_SUFFIXES):
                continue
            target = Path(os.path.normpath(os.path.join(md_path.parent, rel)))
            if not target.exists():
                broken.append((md_path, rel))
    return broken


def group_by_top_level(entries: list[tuple[Path, str]]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for md_path, _ in entries:
        try:
            rel = md_path.relative_to(IMAGE_LAYER_ROOT)
        except ValueError:
            counts["unknown"] += 1
            continue
        top_level = rel.parts[0] if rel.parts else "unknown"
        counts[top_level] += 1
    return dict(sorted(counts.items()))


def main() -> None:
    broken = collect_broken_links()
    print(
        json.dumps(
            {
                "root": str(IMAGE_LAYER_ROOT),
                "files": len(iter_markdown_files()),
                "broken": len(broken),
                "by_top_level": group_by_top_level(broken),
            },
            ensure_ascii=False,
        )
    )
    for md_path, rel in broken[:100]:
        print(f"{md_path}\t{rel}")


if __name__ == "__main__":
    main()
