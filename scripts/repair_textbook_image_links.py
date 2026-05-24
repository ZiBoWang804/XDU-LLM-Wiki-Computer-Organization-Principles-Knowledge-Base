from __future__ import annotations

import argparse
import os
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
TEXTBOOK_IMAGE_ROOT = REPO_ROOT / "知识库" / "图像解读" / "教材"
SOURCE_PREFIX_RE = re.compile(r"(?:\.\./)+资料整理稿/")
NEW_PREFIX = "../../../资料整理稿/"
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
LOCAL_SUFFIXES = (".md", ".jpg", ".jpeg", ".png", ".webp")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Repair and validate textbook image-layer relative links.")
    parser.add_argument("--apply", action="store_true", help="Apply the textbook path fix in-place.")
    return parser.parse_args()


def iter_markdown_files() -> list[Path]:
    return sorted(TEXTBOOK_IMAGE_ROOT.rglob("*.md"))


def repair_file(path: Path, apply: bool) -> tuple[int, bool]:
    text = path.read_text(encoding="utf-8")
    replaced_text, count = SOURCE_PREFIX_RE.subn(NEW_PREFIX, text)
    changed = replaced_text != text
    if changed and apply:
        path.write_text(replaced_text, encoding="utf-8")
    return count, changed


def validate_links() -> list[tuple[Path, str]]:
    broken: list[tuple[Path, str]] = []
    for md_path in iter_markdown_files():
        content = md_path.read_text(encoding="utf-8")
        for match in LINK_RE.finditer(content):
            rel = match.group(1)
            if not rel.lower().endswith(LOCAL_SUFFIXES):
                continue
            target = Path(os.path.normpath(os.path.join(md_path.parent, rel)))
            if not target.exists():
                broken.append((md_path, rel))
    return broken


def main() -> None:
    args = parse_args()
    files = iter_markdown_files()
    matched = 0
    changed_files = 0
    for md_path in files:
        count, changed = repair_file(md_path, args.apply)
        if count:
            matched += count
        if changed:
            changed_files += 1
    broken = validate_links()
    print(
        {
            "apply": args.apply,
            "files": len(files),
            "matched": matched,
            "changed_files": changed_files,
            "broken": len(broken),
        }
    )
    for path, rel in broken[:50]:
        print(f"{path}\t{rel}")


if __name__ == "__main__":
    main()
